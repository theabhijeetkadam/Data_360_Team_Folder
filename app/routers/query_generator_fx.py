
# app/routers/query_generate_fq.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam, func
from typing import Dict, Any, List, Tuple, Optional
import logging
from collections import defaultdict
from app.database import get_db
from app.schemas.query_generator import UserSelection
from app.crud.query_generator import create_extracted_data

log = logging.getLogger(__name__)

router = APIRouter(prefix="/generate-query-fq", tags=["Query Generator (FQ)"])

# ---- Allowed schemas/tables to prevent injection ----
ALLOWED_SCHEMAS = {"gold_copy","clientdb"}
ALLOWED_OPERATORS = {"=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "LIKE", "ILIKE"}
ALLOWED_TABLES   = {"Customer", "Customer_cards"}  # add more as needed

# ---- Distinct key per base table ----
DISTINCT_KEY_MAP = {
    ("gold_copy", "Customer"): ("customer_id", True),  # (column, is_numeric)
    # extend as needed for other base tables
}

# ---- Utilities --------------------------------------------------------------

def _strip_wrappers(s: str) -> str:
    """
    Strip surrounding quotes/backticks/brackets and trim whitespace.
    Examples:
      '"Customer"'       -> 'Customer'
      '`Customer`'       -> 'Customer'
      '[Customer]'       -> 'Customer'
      '  "Customer"  '   -> 'Customer'
    """
    if s is None:
        return ""
    s = str(s).strip()
    if len(s) >= 2:
        first, last = s[0], s[-1]
        if (first == '"' and last == '"') or (first == '`' and last == '`') or (first == '[' and last == ']'):
            s = s[1:-1].strip()
    return s

def normalize_table_path(raw: str, default_schema: str) -> Tuple[str, str]:
    """
    Accept 'schema.table' or 'table'. Strip wrappers and validate schema.
    - If only 'table' is provided, prefix with default_schema.
    """
    raw = _strip_wrappers(raw)
    parts = [p.strip() for p in raw.split(".") if p.strip()]

    if len(parts) == 2:
        schema, table = parts
    elif len(parts) == 1:
        schema, table = default_schema, parts[0]
    else:
        raise HTTPException(status_code=422, detail=f"Invalid table path in relationship: '{raw}'")

    schema = _strip_wrappers(schema)
    table  = _strip_wrappers(table)

    if not schema or not table:
        raise HTTPException(status_code=422, detail=f"Empty schema/table in relationship: '{raw}'")

    # Validate schema if you keep ALLOWED_SCHEMAS
    try:
        if schema not in ALLOWED_SCHEMAS:
            raise HTTPException(status_code=422, detail=f"Unsupported schema in relationships: {schema}")
    except NameError:
        # If ALLOWED_SCHEMAS isn't available here, skip validation gracefully
        pass
    log.info(schema)
    return schema, table

def fmt_table(schema: str, table: str) -> str:
    """Format a table as 'schema.table' without quotes (you asked to avoid quotes)."""
    return f"{schema}.{table}"


def build_joins_from_relationships(
    base_schema: str,
    base_table: str,
    rels: List[Dict[str, str]],
    allowed_tables_in_query: Optional[set[str]] = None,
    ) -> List[str]:
    """
    Build INNER JOIN clauses anchored to base table.

    Inputs: relationship rows expected to have:
      - primary_table_name
      - primary_column_name
      - secondary_table_name
      - secondary_column_name

    Strategy:
      - Start with available = {(base_schema, base_table)}.
      - Multi-pass over relationships:
         * If one side is available and the other isn’t, add a JOIN and mark the new side available.
         * If both sides available → no join needed, skip.
         * If neither side available → defer to next pass.
      - Skip relationships that introduce tables not in `allowed_tables_in_query` (if provided).
      - Deduplicate identical ON pairs.
      - Alias repeated joins to the same table to avoid DuplicateAlias.
      - Always return a list (possibly empty).
    """
    join_clauses: List[str] = []
    available: set[Tuple[str, str]] = {(base_schema, base_table)}
    alias_count: defaultdict[str, int] = defaultdict(int)
    seen_pairs: set[Tuple[str, str, str, str]] = set()

    # Normalize relationships upfront; skip bad rows instead of raising
    pending: List[Dict[str, str]] = []
    for rel in rels or []:
        p_tbl_raw = rel.get("primary_table_name", "")
        s_tbl_raw = rel.get("secondary_table_name", "")
        p_col     = _strip_wrappers(rel.get("primary_column_name", ""))
        s_col     = _strip_wrappers(rel.get("secondary_column_name", ""))

        if not p_col or not s_col:
            log.warning(f"[relationships] Skipping row with empty column(s): {rel}")
            continue

        p_norm = normalize_table_path(p_tbl_raw, base_schema)
        s_norm = normalize_table_path(s_tbl_raw, base_schema)
        if p_norm is None or s_norm is None:
            # schema/table invalid or not allowed; skip this relationship
            continue
        
        p_schema, p_table = p_norm
        s_schema, s_table = s_norm

        if allowed_tables_in_query and (
            p_table not in allowed_tables_in_query and s_table not in allowed_tables_in_query
        ):
            # both sides irrelevant to the user's query; skip
            continue

        pending.append({
            "p_schema": p_schema, "p_table": p_table, "p_col": p_col,
            "s_schema": s_schema, "s_table": s_table, "s_col": s_col,
        })

    # Breadth-first expansion (cap passes to prevent infinite loop)
    progress = True
    max_passes = 10
    passes = 0

    while progress and passes < max_passes and pending:
        passes += 1
        progress = False
        next_pending: List[Dict[str, str]] = []

        for rel in pending:
            p_schema, p_table, p_col = rel["p_schema"], rel["p_table"], rel["p_col"]
            s_schema, s_table, s_col = rel["s_schema"], rel["s_table"], rel["s_col"]

            p_key = (p_schema, p_table)
            s_key = (s_schema, s_table)

            p_tbl_q = fmt_table(p_schema, p_table)
            s_tbl_q = fmt_table(s_schema, s_table)

            if p_key in available and s_key not in available:
                # Join secondary table to available primary
                alias_count[s_tbl_q] += 1
                if alias_count[s_tbl_q] == 1:
                    right_ref = s_tbl_q
                    right_on  = s_tbl_q
                else:
                    alias = f"{s_table}_{alias_count[s_tbl_q]}"
                    right_ref = f"{s_tbl_q} AS {alias}"
                    right_on  = alias

                join_sql = f"INNER JOIN {right_ref} ON {p_tbl_q}.{p_col} = {right_on}.{s_col}"
                pair_key = (p_tbl_q, p_col, right_on, s_col)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    join_clauses.append(join_sql)
                    available.add(s_key)
                    progress = True

            elif s_key in available and p_key not in available:
                # Join primary table to available secondary
                alias_count[p_tbl_q] += 1
                if alias_count[p_tbl_q] == 1:
                    right_ref = p_tbl_q
                    right_on  = p_tbl_q
                else:
                    alias = f"{p_table}_{alias_count[p_tbl_q]}"
                    right_ref = f"{p_tbl_q} AS {alias}"
                    right_on  = alias

                join_sql = f"INNER JOIN {right_ref} ON {s_tbl_q}.{s_col} = {right_on}.{p_col}"
                pair_key = (s_tbl_q, s_col, right_on, p_col)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    join_clauses.append(join_sql)
                    available.add(p_key)
                    progress = True

            else:
                # Neither side available yet OR both already available
                if p_key in available and s_key in available:
                    # Already connected; skip
                    progress = True  # we progressed by dropping it
                    continue
                next_pending.append(rel)

        pending = next_pending

        if pending:
            log.info(f"[relationships] {len(pending)} relationship(s) could not be anchored to base "
                 f"'{base_schema}.{base_table}' and were skipped.")
            
        return

def decode_operator(op: str) -> str:
    """Decode HTML entities and normalize into SQL tokens."""
    if op is None:
        return "="  # default to equality if missing (or raise)
    o = op.strip().upper()
    html_map = {
        "&AMP;GT;": ">", "&AMP;LT;": "<", "&AMP;GT;=": ">=", "&AMP;LT;=": "<=",
        "&GT;": ">", "&LT;": "<", "&GT;=": ">=", "&LT;=": "<=",
    }
    o = html_map.get(o, o)
    return o



def qualify(schema: str, table: str, column: str) -> str:
    """Fully qualify without quoting."""
    if not schema or not table or not column:
        raise HTTPException(status_code=422, detail=f"Empty identifier: {schema}.{table}.{column}")
    return f"{schema}.{table}.{column}"



def parse_field(fq_field: str) -> Tuple[str, str, str]:
    """Parse 'schema.table.column' into components and validate."""
    parts = fq_field.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=422, detail=f"Invalid field format: {fq_field}. Expected 'schema.table.column'.")

    schema, table, column = parts

    # Normalize: trim spaces and strip surrounding double-quotes
    def norm(s: str) -> str:
        s = s.strip()
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            s = s[1:-1]
        return s

    schema = norm(schema)
    table  = norm(table)
    column = norm(column)
    log.info("Schema:"+schema+"table:"+table+"column:"+column)
    # (Optional) Normalize case if your DB uses lowercase identifiers
    # table = table  # or: table = table.lower()
    # column = column  # or: column = column.lower()

    if schema not in ALLOWED_SCHEMAS:
        raise HTTPException(status_code=422, detail=f"Unsupported schema: {schema}")
    if table not in ALLOWED_TABLES:
        raise HTTPException(status_code=422, detail=f"Unsupported table: {table}")
    return schema, table, column

def quote_ident(name: str) -> str:
    return name

def fetch_relationships(db: Session, workflow_id: int) -> List[Dict[str, str]]:
    """
    Read join relationships from clientdb.parameters_relation_details_1
    Expected columns: primary_table_name, primary_column_name, secondary_table_name, secondary_column_name
    """
    sql = text("""
        SELECT primary_table_name, primary_column_name, secondary_table_name, secondary_column_name
        FROM clientdb.parameters_relation_details_1
        WHERE workflow_id = :workflow_id
    """)
    return db.execute(sql, {"workflow_id": workflow_id}).mappings().all()

# ---- Router ----------------------------------------------------------------

@router.post("/")
def generate_query_fq(selection: UserSelection, db: Session = Depends(get_db)):
    """
    Accepts conditions where 'field' is 'schema.table.column' (fully qualified).
    Builds SQL with proper joins (from metadata, fallback to customer_id), excludes reserved rows,
    deduplicates by base key, applies limit, and reserves the results.

    Returns JSON:
    {
      "query": "...",
      "parameters": {...},
      "rows": [...],
      "reserved_count": N,
      "data_keys": [...],
      "workflow_id": int,
      "requested_volume": int
    }
    """
    try:
        workflow_id    = selection.workflow_id
        groups         = selection.groups
        group_operator = selection.group_operator
        data_volume    = selection.data_volume

        # -- Determine all tables used in conditions
        used_tables: List[Tuple[str, str]] = []  # list of (schema, table)
        for g in groups:
            for c in g.conditions:
                log.info(c.field)
                s, t, _ = parse_field(c.field)
                used_tables.append((s, t))

        # -- Base table: choose the first condition's table
        base_schema, base_table = parse_field(groups[0].conditions[0].field)[:2]
        base_table_q = f"{base_schema}.{quote_ident(base_table)}"
        log.info("base schema:"+base_schema+"base table:"+base_table_q)
        # -- Distinct key for base table
        distinct_key_col, is_numeric = DISTINCT_KEY_MAP.get((base_schema, base_table), ("customer_id", True))
        distinct_key_q = f"{base_table_q}.{distinct_key_col}"

        # -- Build SELECT: include distinct key + some useful fields
        select_parts = [
            f"{distinct_key_q} AS \"__data_key\"",
            f"{base_table_q}.customer_city AS \"city\"",
            f"{base_table_q}.card_type AS \"credit_check\"",
            f"{base_table_q}.card_limit AS \"ab\"",
            f"{base_table_q}.card_limit AS \"ade\"",
        ]
        join_clauses: List[str] = []

        
# Determine which tables the user actually referenced in conditions
        tables_set = {t for (_, t) in used_tables}

        rels = fetch_relationships(db, workflow_id)

# Build joins anchored to base table, only for relevant tables
        join_clauses = build_joins_from_relationships(base_schema, base_table, rels, tables_set)
        log.info(join_clauses)
# Fallback join only if no relationships and both Customer and Customer_cards used
        if not join_clauses and "Customer" in tables_set and "Customer_cards" in tables_set:
            cust_q  = f"{base_schema}.Customer"
            cards_q = f"{base_schema}.Customer_cards"
            join_clauses.append(f"INNER JOIN {cards_q} ON {cust_q}.customer_id = {cards_q}.customer_id")

        join_sql = "\n".join(join_clauses or [])

        # -- Build WHERE with groups
        where_clauses: List[str] = []
        values: Dict[str, Any] = {}
        expanding_params: Dict[str, List[Any]] = {}

        
        for i, group in enumerate(groups):
            cond_sqls: List[str] = []
            for j, cond in enumerate(group.conditions):
                log.info(f"[cond] raw field={cond.field}, operator={cond.operator}, value={cond.value}")

                schema, table, column = parse_field(cond.field)
                fq_col = qualify(schema, table, column)

                op = decode_operator(cond.operator)
                if op not in ALLOWED_OPERATORS:
                    raise HTTPException(status_code=422, detail=f"Unsupported operator: {cond.operator}")

                if op in ("IN", "NOT IN"):
                    param_name = f"p_{i}_{j}"
                    lst = cond.value if isinstance(cond.value, list) else [cond.value]
                    cond_sqls.append(f"{fq_col} {op} :{param_name}")
                    expanding_params[param_name] = lst
                else:
                    param_name = f"p_{i}_{j}"
                    cond_sqls.append(f"{fq_col} {op} :{param_name}")
                    v = cond.value
                if isinstance(v, str) and v.isdigit():
                    values[param_name] = int(v)
                else:
                    values[param_name] = v

                log.info(f"[cond] fq_col={fq_col}, op={op}, sql='{cond_sqls}'")
            group_sql = f"({' AND '.join(cond_sqls)})" if group.logical == "AND" else f"({' OR '.join(cond_sqls)})"
            where_clauses.append(group_sql)

        final_where = f" {group_operator} ".join(where_clauses) if where_clauses else "TRUE"
        source_table_exact = f"{base_schema}.{base_table}"
        not_exists_clause = f"""
        AND NOT EXISTS (
            SELECT 1
            FROM clientdb.extracted_data_table AS edt
            WHERE edt.workflow_id = :workflow_id
              AND edt.source_table = :source_table
              AND edt.is_reserved  = TRUE
        )
        """
        values["workflow_id"] = workflow_id
        values["source_table"] = source_table_exact
        values["limit"]       = data_volume

        # -- Core SQL
        core_sql = f"""
            SELECT {', '.join(select_parts)}
            FROM {base_table_q}
            {join_sql}
            WHERE {final_where}
            {not_exists_clause}
        """

        final_text = text(f"""
            SET search_path TO gold_copy, clientdb, public;
            SELECT DISTINCT ON (q.__data_key) *
            FROM ({core_sql}) AS q
            ORDER BY q.__data_key ASC
            LIMIT :limit
        """)

        # bind expanding params
        for name, lst in expanding_params.items():
            final_text = final_text.bindparams(bindparam(name, expanding=True, value=lst))

        # Execute
        result = db.execute(final_text, values)
        rows = result.mappings().all() if hasattr(result, "mappings") else []  # driver-safe fallback

        # Reserve returned keys
        reserved_keys: List[int] = []
        for row in rows:
            key = row.get("__data_key")
            # persist reservation
            reserved_keys.append(key)

        return {
            "query": final_text.text,
            "parameters": {**values, **expanding_params},
            "rows": rows,
            "reserved_count": len(reserved_keys),
            "data_keys": reserved_keys,
            "workflow_id": workflow_id,
            "requested_volume": data_volume
        }

    
    except HTTPException:
        raise
    except Exception as e:
        log.exception("generate_query_fq failed")
        raise HTTPException(status_code=422, detail=str(e))

