
# app/routers/query_generator.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.schemas.query_generator import UserSelection, Operator
from app.database import SessionLocal
from app.models.mining_workflow_output_criteria import MiningWorkflowOutputCriteria
from app.models.parameters_relation_details import ParametersRelationDetails

router = APIRouter(prefix="/generate-query", tags=["Query Generator"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sanitize_operator(op: Operator) -> str:
    # Map enum to SQL ops
    mapping = {
        Operator.EQ: "=",
        Operator.NE: "!=",
        Operator.GT: ">",
        Operator.LT: "<",
        Operator.GTE: ">=",
        Operator.LTE: "<=",
        Operator.IN: "IN",
        Operator.NIN: "NOT IN",
        Operator.LIKE: "LIKE",
        Operator.ILIKE: "ILIKE",
    }
    return mapping[op]

def qualify(schema_default: str, table_name: str) -> str:
    # If fully qualified (schema.table) leave as is; else prefix schema
    return table_name if "." in table_name else f"{schema_default}.{table_name}"

@router.post("/")
def generate_query(selection: UserSelection, db: Session = Depends(get_db)):
    workflow_id = selection.workflow_id
    groups = selection.groups
    group_operator = selection.group_operator
    data_volume = selection.data_volume

    # Schemas: source vs. reservation
    SOURCE_SCHEMA = "gold_copy"
    RESV_SCHEMA   = "clientdb"

    # 1) Load configured output fields for this workflow
    output_fields = (
        db.query(MiningWorkflowOutputCriteria)
          .filter(MiningWorkflowOutputCriteria.workflow_id == workflow_id)
          .all()
    )
    if not output_fields:
        raise HTTPException(status_code=404, detail="No output fields configured for this workflow")

    # Build a map from Business Name -> (table, column)
    # UI uses Business Name as the first field label.
    field_map = {}
    for f in output_fields:
        # Expect f.source_table, f.source_column, f.business_name
        # If source_table missing schema, default to SOURCE_SCHEMA
        fq_table = qualify(SOURCE_SCHEMA, f.source_table)
        field_map[f.business_name] = (fq_table, f.source_column)

    # BASE TABLE: pick the table of the FIRST output field for simplicity
    base_table = list(field_map.values())[0][0]  # fully qualified e.g. gold_copy.customer

    # 2) Load relationships to build JOINs
    relationships = (
        db.query(ParametersRelationDetails)
          .filter(ParametersRelationDetails.workflow_id == workflow_id)
          .all()
    )

    # Alias assignment for tables
    aliases = {}
    def alias_for(fq_table: str) -> str:
        if fq_table not in aliases:
            aliases[fq_table] = f"t{len(aliases)+1}"
        return aliases[fq_table]

    # Ensure base table has an alias
    base_alias = alias_for(base_table)

    # 3) SELECT clause (use aliases)
    select_parts = []
    for f in output_fields:
        fq_table, col = field_map[f.business_name]
        alias = alias_for(fq_table)
        if f.business_name:
            select_parts.append(f'{alias}.{col} AS "{f.business_name}"')
        else:
            select_parts.append(f"{alias}.{col}")
    select_sql = ", ".join(select_parts)

    # 4) JOINs
    join_clauses = []
    for rel in relationships:
        # rel.primary_table_name, rel.secondary_table_name, rel.primary_column_name, rel.secondary_column_name
        pt = qualify(SOURCE_SCHEMA, rel.primary_table_name)
        st = qualify(SOURCE_SCHEMA, rel.secondary_table_name)
        pa = alias_for(pt)
        sa = alias_for(st)
        join_clauses.append(
            f"INNER JOIN {st} AS {sa} ON {pa}.{rel.primary_column_name} = {sa}.{rel.secondary_column_name}"
        )
    join_sql = " ".join(join_clauses)

    # 5) WHERE (groups) — map Business Name to table.column
    where_groups_sql = []
    values = {}

    for gi, group in enumerate(groups):
        cond_sql = []
        for cj, cond in enumerate(group.conditions):
            # Skip UI "Any" selection: no filter if user chose ANY
            if isinstance(cond.value, str) and cond.value.strip().upper() == "ANY":
                continue

            # Resolve Business Name -> (table, column)
            if cond.field not in field_map:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported field in filter: {cond.field}. Ensure it matches a configured Business Name."
                )
            fq_table, col = field_map[cond.field]
            alias = alias_for(fq_table)

            op = sanitize_operator(cond.operator)
            param = f"param_{gi}_{cj}"

            # IN/NOT IN require a list; others are scalar
            if op in ("IN", "NOT IN"):
                if not isinstance(cond.value, list) or len(cond.value) == 0:
                    raise HTTPException(status_code=400, detail=f"Operator {op} requires a non-empty list")
                cond_sql.append(f"{alias}.{col} {op} :{param}")
            elif op in ("LIKE", "ILIKE"):
                cond_sql.append(f"{alias}.{col} {op} :{param}")
            else:
                cond_sql.append(f"{alias}.{col} {op} :{param}")

            values[param] = cond.value

        if cond_sql:  # if any conditions survived (skip-only ANY)
            joined = " AND ".join(cond_sql) if group.logical == "AND" else " OR ".join(cond_sql)
            where_groups_sql.append(f"({joined})")

    final_where = f" {group_operator} ".join(where_groups_sql) if where_groups_sql else "TRUE"

    # 6) Exclude already reserved rows
    # Distinct key for gold_copy.customer is customer_id (per your screenshot).
    DISTINCT_KEY_COL = "customer_id"  # If you ever need another table, make this configurable per workflow

    not_exists_clause = f"""
    AND NOT EXISTS (
        SELECT 1
        FROM {RESV_SCHEMA}.extracted_data_table AS edt
        WHERE edt.workflow_id = :workflow_id
          AND edt.source_table = :source_table
          AND edt.source_key   = {base_alias}.{DISTINCT_KEY_COL}
          AND edt.is_reserved  = TRUE
    )
    """

    # 7) Final query (ORDER BY + LIMIT for determinism)
    query = f"""
        SELECT {select_sql}
        FROM {base_table} AS {base_alias}
        {join_sql}
        WHERE {final_where}
        {not_exists_clause}
        ORDER BY {base_alias}.{DISTINCT_KEY_COL} ASC
        LIMIT :limit
    """

    # Bind values
    values["workflow_id"] = workflow_id
    values["source_table"] = base_table  # e.g., "gold_copy.customer"
    values["limit"] = data_volume

    # 8) Execute with safe search_path
    db.execute(text("SET search_path TO gold_copy, clientdb, public"))
    result = db.execute(text(query), values)
    rows = result.mappings().all()
    col_names = list(rows[0].keys()) if rows else []

    return {
        "query": query.strip(),
        "params": values,
        "columns": col_names,
        "data": rows,
        "requested_volume": data_volume,
        "row_count": len(rows),
        "base_table": base_table,
        "distinct_key": DISTINCT_KEY_COL,
    }