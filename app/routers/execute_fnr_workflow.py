
import re, logging
from typing import List, Union, Optional
import uuid
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
    created_by: str

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
        
        if isinstance(val, str) and val.lower() == "any":
            where_parts.append(f"{t}.{c} = {t}.{c}")
            continue

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

    #The logic added to find out which of the rows in result of the final_query were reserved
    # and to remove these reserved data from final_query result
    
    # --- Step 1: get data_keys (columns marked reserved in output criteria) ---
    # db.execute(text("SET search_path TO clientdb"))
    dk_rows = db.execute(
        text("""
            SELECT source_column
            FROM clientdb.mining_workflow_output_criteria_1
            WHERE workflow_id = :wid
            AND is_parameter_flag = true
        """),
        {"wid": str(wid)},
    ).mappings().all()
    
    data_keys = [r["source_column"] for r in dk_rows]

    # Normalize to plain column names (strip table qualifiers like 'customer.customer_id' -> 'customer_id')
    # data_keys = [str(r["source_column"]).split(".")[-1] for r in dk_rows]

    # --- Step 2: collect reserved values by key from extract_and_reserve_log and filter final_query rows ---
    res_rows = db.execute(
        text("""
            SELECT data_keys, data_records
            FROM clientdb.extract_and_reserve_log
            WHERE workflow_id = :wid
        """),
        {"wid": str(wid)},
    ).mappings().all()

    # Build a map of { key -> set(reserved_values) }
    reserved_by_key = {k: set() for k in data_keys}
    for rr in res_rows:
        rr_keys = rr.get("data_keys") or []
        # Normalize keys in the stored row as well
        # rr_keys_norm = [str(k).split(".")[-1] for k in rr_keys]
        records = rr.get("data_records") or []
        for k in data_keys:
            if k in rr_keys:
                for rec in records:
                    # Only consider records explicitly marked reserved = true
                    if str(rec.get("is_reserved")).lower() == "true":
                        val = rec.get(k)
                        if val is not None:
                            reserved_by_key[k].add(str(val))
    
    # Remove any final_query row if any of its key values are in reserved_by_key
    filtered_rows = []
    for row in rows:
        drop = False
        for k in data_keys:
            v = row.get(k)
            if v is not None and str(v) in reserved_by_key.get(k, set()):
                drop = True
                break
        if not drop:
            filtered_rows.append(row)

    rows = filtered_rows

    if not rows:
        log.info("No data found matching the criteria after filtering reserved records.")
        db.execute(
            text("""
                INSERT INTO clientdb.extract_and_reserve_log
                (workflow_id, execution_id, data_keys, data_records, created_by)
                VALUES (:wid, :execution_id, :data_keys, :data_records, :created_by)
            """),
            {"wid": str(wid), "execution_id": uuid.uuid4(), 
             "data_keys": [], "data_records": [],
             "created_by": payload.created_by})
        db.commit()
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