
# app/routers/query_generate_fq.py
from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import text, bindparam
from typing import Dict, Any, List, Tuple, Optional
import logging, re
from collections import defaultdict
from decimal import Decimal
from datetime import date, datetime, time as dtime
from app.database import get_db
from app.schemas.query_generator import UserSelection
from app.crud.query_generator import create_extracted_data

log = logging.getLogger(__name__)
router = APIRouter(prefix="/generate-query-fq", tags=["Query Generator (FQ)"])

ALLOWED_SCHEMAS = {"gold_copy", "clientdb"}
ALLOWED_OPERATORS = {"=", "!=", ">", "<", ">=", "<=", "IN", "NOT IN", "LIKE", "ILIKE"}
ALLOWED_TABLES = {"Customer", "Customer_cards"}
DISTINCT_KEY_MAP = {("gold_copy", "Customer"): ("customer_id", True)}

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$", re.ASCII)

def _strip_wrappers(s: str) -> str:
    if s is None: return ""
    s = str(s).strip()
    if len(s) >= 2 and ((s[0], s[-1]) in {('"','"'),('`','`'),('[',']')}): s = s[1:-1].strip()
    return s

def normalize_table_path(raw: str, default_schema: str) -> Tuple[str, str]:
    raw = _strip_wrappers(raw)
    parts = [p.strip() for p in raw.split(".") if p.strip()]
    if len(parts) == 2: schema, table = parts
    elif len(parts) == 1: schema, table = default_schema, parts[0]
    else: raise HTTPException(status_code=422, detail=f"Invalid table path in relationship: '{raw}'")
    schema, table = _strip_wrappers(schema), _strip_wrappers(table)
    if not schema or not table: raise HTTPException(status_code=422, detail=f"Empty schema/table in relationship: '{raw}'")
    if schema not in ALLOWED_SCHEMAS: raise HTTPException(status_code=422, detail=f"Unsupported schema in relationships: {schema}")
    return schema, table

def fmt_table(schema: str, table: str) -> str: return f"{schema}.{table}"

def _coerce_param_value(val: Any) -> Any:
    if isinstance(val, (bool, int, float)): return val
    if isinstance(val, Decimal): return float(val)
    if isinstance(val, (datetime, date, dtime)): return val.isoformat()
    if isinstance(val, str):
        s = val.strip()
        if _INT_RE.match(s): 
            try: return int(s)
            except: return s
        if _FLOAT_RE.match(s):
            try: return float(s)
            except: return s
        if s.lower() in ("true", "false"): return s.lower() == "true"
        return s
    return val

def _coerce_value_for_json(v: Any) -> Any:
    if isinstance(v, Decimal): return float(v)
    if isinstance(v, (datetime, date, dtime)): return v.isoformat()
    return v

def build_joins_from_relationships(
    base_schema: str,
    base_table: str,
    rels: List[Dict[str, str]],
    allowed_tables_in_query: Optional[set[str]] = None,
) -> List[str]:
    join_clauses: List[str] = []
    available: set[Tuple[str, str]] = {(base_schema, base_table)}
    alias_count: defaultdict[str, int] = defaultdict(int)
    seen_pairs: set[Tuple[str, str, str, str]] = set()
    pending: List[Dict[str, str]] = []

    for rel in rels or []:
        p_tbl_raw, s_tbl_raw = rel.get("primary_table_name",""), rel.get("secondary_table_name","")
        p_col, s_col = _strip_wrappers(rel.get("primary_column_name","")), _strip_wrappers(rel.get("secondary_column_name",""))
        if not p_col or not s_col: 
            log.warning(f"[relationships] Skip empty cols: {rel}"); 
            continue
        try:
            p_schema, p_table = normalize_table_path(p_tbl_raw, base_schema)
            s_schema, s_table = normalize_table_path(s_tbl_raw, base_schema)
        except HTTPException as he:
            log.warning(f"[relationships] Skip invalid: {rel} ({he.detail})"); 
            continue
        if allowed_tables_in_query and (p_table not in allowed_tables_in_query and s_table not in allowed_tables_in_query):
            continue
        pending.append({"p_schema": p_schema, "p_table": p_table, "p_col": p_col, "s_schema": s_schema, "s_table": s_table, "s_col": s_col})

    progress, passes, max_passes = True, 0, 10
    while progress and passes < max_passes and pending:
        passes += 1; progress = False; next_pending: List[Dict[str, str]] = []
        for rel in pending:
            p_schema, p_table, p_col = rel["p_schema"], rel["p_table"], rel["p_col"]
            s_schema, s_table, s_col = rel["s_schema"], rel["s_table"], rel["s_col"]
            p_key, s_key = (p_schema, p_table), (s_schema, s_table)
            p_tbl_q, s_tbl_q = fmt_table(p_schema, p_table), fmt_table(s_schema, s_table)

            if p_key in available and s_key not in available:
                alias_count[s_tbl_q] += 1
                right_ref, right_on = (s_tbl_q, s_tbl_q) if alias_count[s_tbl_q] == 1 else (f"{s_tbl_q} AS {s_table}_{alias_count[s_tbl_q]}", f"{s_table}_{alias_count[s_tbl_q]}")
                join_sql = f"INNER JOIN {right_ref} ON {p_tbl_q}.{p_col} = {right_on}.{s_col}"
                pair_key = (p_tbl_q, p_col, right_on, s_col)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key); join_clauses.append(join_sql); available.add(s_key); progress = True
            elif s_key in available and p_key not in available:
                alias_count[p_tbl_q] += 1
                right_ref, right_on = (p_tbl_q, p_tbl_q) if alias_count[p_tbl_q] == 1 else (f"{p_tbl_q} AS {p_table}_{alias_count[p_tbl_q]}", f"{p_table}_{alias_count[p_tbl_q]}")
                join_sql = f"INNER JOIN {right_ref} ON {s_tbl_q}.{s_col} = {right_on}.{p_col}"
                pair_key = (s_tbl_q, s_col, right_on, p_col)
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key); join_clauses.append(join_sql); available.add(p_key); progress = True
            else:
                if not (p_key in available and s_key in available): next_pending.append(rel)
                else: progress = True
        pending = next_pending

    if pending:
        log.info(f"[relationships] {len(pending)} relationship(s) could not be anchored to base '{base_schema}.{base_table}' and were skipped.")
    return join_clauses

def decode_operator(op: str) -> str:
    if op is None: return "="
    o = op.strip().upper()
    html_map = {"&AMP;GT;": ">", "&AMP;LT;": "<", "&AMP;GT;=": ">=", "&AMP;LT;=": "<=", "&GT;": ">", "&LT;": "<", "&GT;=": ">=", "&LT;=": "<=", "&AMP;AMP;GT;": ">", "&AMP;AMP;LT;": "<", "&AMP;AMP;GT;=": ">=", "&AMP;AMP;LT;=": "<=", "&amp;gt;": ">", "&amp;lt;": "<", "&amp;gt;=": ">=", "&amp;lt;=": "<="}
    return html_map.get(o, o)

def qualify(schema: str, table: str, column: str) -> str:
    if not schema or not table or not column: raise HTTPException(status_code=422, detail=f"Empty identifier: {schema}.{table}.{column}")
    return f"{schema}.{table}.{column}"

def parse_field(fq_field: str) -> Tuple[str, str, str]:
    parts = fq_field.split(".")
    if len(parts) != 3: raise HTTPException(status_code=422, detail=f"Invalid field format: {fq_field}. Expected 'schema.table.column'.")
    def norm(s: str) -> str:
        s = s.strip()
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"': s = s[1:-1]
        return s
    schema, table, column = norm(parts[0]), norm(parts[1]), norm(parts[2])
    
    log.info(f"[parse_field] schema={schema} table={table} column={column}")
    if schema not in ALLOWED_SCHEMAS: raise HTTPException(status_code=422, detail=f"Unsupported schema: {schema}")
    if table not in ALLOWED_TABLES: raise HTTPException(status_code=422, detail=f"Unsupported table: {table}")
    return schema, table, column

def quote_ident(name: str) -> str: return name

def fetch_relationships(db: Session, workflow_id: int) -> List[Dict[str, str]]:
    sql = text("""
        SELECT primary_table_name, primary_column_name, secondary_table_name, secondary_column_name
        FROM clientdb.parameters_relation_details_1
        WHERE workflow_id = :workflow_id
    """)
    rows = db.execute(sql, {"workflow_id": workflow_id}).mappings().all()
    log.info(f"[fetch_relationships] workflow_id={workflow_id} count={len(rows)}")
    return rows

@router.post("/")
def generate_query_fq(selection: UserSelection, db: Session = Depends(get_db)):
    try:
        workflow_id, groups, group_operator, data_volume = selection.workflow_id, selection.groups, selection.group_operator, selection.data_volume
        log.info("[generate_query_fq] called", extra={"workflow_id": workflow_id, "group_operator": group_operator, "data_volume": data_volume})
        used_tables: List[Tuple[str, str]] = []
        for g in groups:
            for c in g.conditions:
                log.info(f"[condition] field={c.field}")
                s, t, _ = parse_field(c.field)
                used_tables.append((s, t))
        base_schema, base_table = parse_field(groups[0].conditions[0].field)[:2]
        base_table_q = f"{base_schema}.{quote_ident(base_table)}"
        log.info(f"[base] schema={base_schema} table={base_table_q}")
        distinct_key_col, is_numeric = DISTINCT_KEY_MAP.get((base_schema, base_table), ("customer_id", True))
        distinct_key_q = f"{base_table_q}.{distinct_key_col}"
        log.info(f"[distinct_key] column={distinct_key_col} is_numeric={is_numeric}")

        select_parts = [
            f"{distinct_key_q} AS \"__data_key\"",
            f"{base_table_q}.customer_city AS \"city\"",
            f"{base_table_q}.card_type AS \"credit_check\"",
            f"{base_table_q}.card_limit AS \"ab\"",
            f"{base_table_q}.card_limit AS \"ade\"",
        ]

        tables_set = {t for (_, t) in used_tables}
        rels = fetch_relationships(db, workflow_id)
        join_clauses = build_joins_from_relationships(base_schema, base_table, rels, tables_set)
        log.info(f"[joins] count={len(join_clauses)} clauses={join_clauses}")
        if not join_clauses and "Customer" in tables_set and "Customer_cards" in tables_set:
            cust_q, cards_q = f"{base_schema}.Customer", f"{base_schema}.Customer_cards"
            join_clauses.append(f"INNER JOIN {cards_q} ON {cust_q}.customer_id = {cards_q}.customer_id")
            log.info("[joins] applied fallback Customer↔Customer_cards")
        join_sql = "\n".join(join_clauses or [])

        where_clauses, values, expanding_params = [], {}, {}
        for i, group in enumerate(groups):
            cond_sqls: List[str] = []
            for j, cond in enumerate(group.conditions):
                log.info(f"[cond] raw field={cond.field}, operator={cond.operator}, value={cond.value}")
                schema, table, column = parse_field(cond.field)
                fq_col = qualify(schema, table, column)
                op = decode_operator(cond.operator)
                if op not in ALLOWED_OPERATORS: raise HTTPException(status_code=422, detail=f"Unsupported operator: {cond.operator}")
                param_name = f"p_{i}_{j}"
                if op in ("IN", "NOT IN"):
                    lst_in = cond.value if isinstance(cond.value, list) else [cond.value]
                    lst_norm = [_coerce_param_value(v) for v in lst_in]
                    cond_sqls.append(f"{fq_col} {op} :{param_name}")
                    expanding_params[param_name] = lst_norm
                else:
                    v = _coerce_param_value(cond.value)
                    cond_sqls.append(f"{fq_col} {op} :{param_name}")
                    values[param_name] = v
                log.info(f"[cond] fq_col={fq_col}, op={op}, sql_fragment={cond_sqls[-1]}")
            group_sql = f"({' AND '.join(cond_sqls)})" if group.logical == "AND" else f"({' OR '.join(cond_sqls)})"
            where_clauses.append(group_sql)
            log.info(f"[group {i}] logical={group.logical} fragment={group_sql}")

        final_where = f" {group_operator} ".join(where_clauses) if where_clauses else "TRUE"
        source_table_exact = f"{base_schema}.{base_table}"
        not_exists_clause = """
        AND NOT EXISTS (
            SELECT 1
            FROM clientdb.extracted_data_table AS edt
            WHERE edt.workflow_id = :workflow_id
              AND edt.source_table = :source_table
              AND edt.is_reserved  = TRUE
        )
        """
        values["workflow_id"], values["source_table"], values["limit"] = workflow_id, source_table_exact, data_volume

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
        for name, lst in expanding_params.items():
            final_text = final_text.bindparams(bindparam(name, expanding=True, value=lst))
        log.info("[sql] executing", extra={"text": final_text.text, "params": {**values, **expanding_params}})

        result = db.execute(final_text, values)
        rows_raw = result.mappings().all() if hasattr(result, "mappings") else []

        rows: List[Dict[str, Any]] = []
        for r in rows_raw:
            d: Dict[str, Any] = {}
            for k, v in dict(r).items():
                d[k] = _coerce_value_for_json(v)
            rows.append(d)

        reserved_keys: List[Any] = []
        for row in rows:
            reserved_keys.append(_coerce_value_for_json(row.get("__data_key")))

        payload = {
            "query": final_text.text,
            "parameters": {**values, **expanding_params},
            "rows": rows,
            "reserved_count": len(reserved_keys),
            "data_keys": reserved_keys,
            "workflow_id": workflow_id,
            "requested_volume": data_volume            
        }
        log.info('payload++++',payload)
        return jsonable_encoder(payload)

    except HTTPException:
        raise
    except Exception as e:
        log.exception("generate_query_fq failed")
