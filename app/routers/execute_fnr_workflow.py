
import re, logging
from typing import List, Union, Optional
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import get_db

log = logging.getLogger(__name__)
router = APIRouter(prefix="/execute-fnr-workflow", tags=["FnR Workflow Execution"])

ALLOWED_OPS = {"=", "!=", "<", "<=", ">", ">="}

class Condition(BaseModel):
    business_name: str
    operator: str
    value: Union[str, int, float]

class FnRExecutePayload(BaseModel):
    workflow_id: int
    conditions: List[Condition]
    data_volume: int

def _is_ident(s: str) -> bool:
    """Minimal identifier safety: letters/underscore start; then alnum/underscore."""
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", s))

def execute_fnr(payload: FnRExecutePayload, db):
    wid = payload.workflow_id

    # --- 1) Fetch mapping tables for the workflow ---
    db.execute(text("SET search_path TO clientdb"))
    in_rows = db.execute(
        text("""
            SELECT business_name, source_table, source_column
            FROM mining_workflow_input_criteria_1
            WHERE workflow_id = :wid
        """), {"wid": wid}
    ).mappings().all()

    out_rows = db.execute(
        text("""
            SELECT business_name, source_table, source_column
            FROM mining_workflow_output_criteria_1
            WHERE workflow_id = :wid
        """), {"wid": wid}
    ).mappings().all()

    rel_rows = db.execute(
        text("""
            SELECT primary_table_name, primary_column_name,
                   secondary_table_name, secondary_column_name
            FROM parameters_relation_details_1
            WHERE workflow_id = :wid
        """), {"wid": wid}
    ).mappings().all()

    if not out_rows:
        raise ValueError("No output criteria found for the workflow.")
    if not rel_rows:
        raise ValueError("No relationships found for the workflow.")

    # --- 2) Build business_name -> (table, column) map for WHERE clauses ---
    bn_to_tc = {}
    for r in in_rows:
        bn, st, sc = r["business_name"], r["source_table"], r["source_column"]
        if not (_is_ident(st) and _is_ident(sc)):
            raise ValueError(f"Invalid identifier in input criteria: {st}.{sc}")
        bn_to_tc[bn] = (st, sc)

    # --- 3) Build SELECT columns ---
    select_cols = []
    tables_seen = set()
    for r in out_rows:
        st, sc = r["source_table"], r["source_column"]
        if not (_is_ident(st) and _is_ident(sc)):
            raise ValueError(f"Invalid identifier in output criteria: {st}.{sc}")
        select_cols.append(f"{st}.{sc}")
        tables_seen.add(st)

    # --- 4) Build JOINs from relationships (simple chain builder) ---
    join_clauses = []
    base_table: Optional[str] = None
    joined = set()

    for rel in rel_rows:
        pt, pc = rel["primary_table_name"], rel["primary_column_name"]
        st, sc = rel["secondary_table_name"], rel["secondary_column_name"]

        for name in (pt, pc, st, sc):
            if name is None:
                raise ValueError("Relationship row has NULLs.")
        if not (_is_ident(pt) and _is_ident(pc) and _is_ident(st) and _is_ident(sc)):
            raise ValueError(f"Invalid identifier in relationship: {pt}.{pc} = {st}.{sc}")

        if base_table is None:
            base_table = pt
            joined.add(pt)

        if pt in joined and st not in joined:
            join_clauses.append(f"JOIN {st} ON {pt}.{pc} = {st}.{sc}")
            joined.add(st)
        elif st in joined and pt not in joined:
            join_clauses.append(f"JOIN {pt} ON {pt}.{pc} = {st}.{sc}")
            joined.add(pt)
        elif pt not in joined and st not in joined:
            # Start a new segment off current base_table
            join_clauses.append(f"JOIN {st} ON {pt}.{pc} = {st}.{sc}")
            joined.update({pt, st})

    if base_table is None:
        # Fallback to any table seen in output, otherwise first relationship’s primary table
        base_table = next(iter(tables_seen), rel_rows[0]["primary_table_name"])

    if not _is_ident(base_table):
        raise ValueError(f"Invalid base table: {base_table}")

    # --- 5) WHERE from payload conditions ---
    where_parts = []
    params = {"limit": payload.data_volume}

    for i, cond in enumerate(payload.conditions):
        bn = cond.business_name
        op = cond.operator.strip().upper()
        val = cond.value

        if op not in ALLOWED_OPS:
            raise ValueError(f"Unsupported operator: {cond.operator}")

        if bn not in bn_to_tc:
            raise ValueError(f"Condition business_name not mapped in input criteria: {bn}")

        t, c = bn_to_tc[bn]
        if not (_is_ident(t) and _is_ident(c)):
            raise ValueError(f"Invalid identifier from input map: {t}.{c}")

        pname = f"p{i}"
        where_parts.append(f"{t}.{c} {op} :{pname}")
        params[pname] = val

    # --- 6) Assemble final query ---
    select_sql = ", ".join(select_cols)
    join_sql = " ".join(join_clauses)
    where_sql = (" WHERE " + " AND ".join(where_parts)) if where_parts else ""
    final_query = f"SELECT distinct {select_sql} FROM {base_table} {join_sql}{where_sql} LIMIT :limit"

    # --- 7) Execute and return rows (list of dicts) ---
    db.execute(text("SET search_path TO gold_copy"))
    result = db.execute(text(final_query), params)
    rows = result.mappings().all()
    payload = {
        "workflow_id": wid,
        "result": rows            
    }
    return payload

@router.post("/")
def post_execute(payload: FnRExecutePayload, db: Session = Depends(get_db)):
    try:
        return execute_fnr(payload, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))