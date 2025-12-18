
# app/routers/distinct_value.py

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Tuple
import re
import logging
import time

from app.database import get_db

router = APIRouter(prefix="/fetch", tags=["Fetch Values"])
logger = logging.getLogger(__name__)

# ---- Metadata table (lives in clientdb) ----
INPUT_CRITERIA_SCHEMA = "clientdb"
INPUT_CRITERIA_TABLE  = "mining_workflow_input_criteria_1"  # lowercase, unquoted

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

# allow only standard SQL identifiers: letters, digits, underscore (first char letter/underscore)
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

def _safe_ident(name: str, *, label: str) -> str:
    """
    Validate and return a safely quoted identifier for table/column names.
    Raises HTTPException(400) if invalid.
    """
    if not name or not IDENT_RE.match(name):
        logger.error("Invalid identifier detected", extra={"label": label, "name": name})
        raise HTTPException(status_code=400, detail=f"Invalid {label} identifier: {name!r}")
    # Quote identifiers since we lower-case them; Postgres will treat "name" as literal
    return f'"{name}"'

def _get_source_table_column(db: Session, workflow_id: int, business_name: str) -> Tuple[str, str]:
    """
    Fetch source_table and source_column from clientdb.mining_workflow_input_criteria_1.
    Supports 'Any' fallback to pick first criteria in the workflow.
    """
    logger.info("[distinct_value] Fetching metadata", extra={"workflow_id": workflow_id, "business_name": business_name})

    sql = text(f"""
        SELECT source_table, source_column
        FROM {INPUT_CRITERIA_SCHEMA}.{INPUT_CRITERIA_TABLE}
        WHERE workflow_id = :workflow_id AND business_name = :business_name
        LIMIT 1
    """)
    row = db.execute(sql, {"workflow_id": workflow_id, "business_name": business_name}).fetchone()

    if not row and business_name.lower() == "any":
        logger.info("[distinct_value] No exact business_name; using 'Any' fallback", extra={"workflow_id": workflow_id})
        sql_any = text(f"""
            SELECT source_table, source_column
            FROM {INPUT_CRITERIA_SCHEMA}.{INPUT_CRITERIA_TABLE}
            WHERE workflow_id = :workflow_id
            ORDER BY input_criteria_id
            LIMIT 1
        """)
        row = db.execute(sql_any, {"workflow_id": workflow_id}).fetchone()

    if not row:
        logger.warning("[distinct_value] Metadata not found", extra={"workflow_id": workflow_id, "business_name": business_name})
        raise HTTPException(status_code=404, detail="No matching metadata found for given workflow/business_name")

    logger.info("[distinct_value] Metadata found", extra={"source_table": row[0], "source_column": row[1]})
    return row[0], row[1]

def _resolve_schema_table_column(source_table: str, source_column: str) -> Tuple[str, str, str]:
    """
    Determine schema and validate identifiers.
    - If source_table is 'schema.table', use that schema.
    - Else default schema to 'gold_copy' (per your architecture).
    """
    st = source_table.strip()
    sc = source_column.strip()

    if "." in st:
        schema_name, table_name = st.split(".", 1)
    else:
        schema_name, table_name = "gold_copy", st  # ✅ default to gold_copy for source data

    # We lower-case before quoting since IDENT_RE allows lowercase letters/digits/underscore
    schema_ident = _safe_ident(schema_name.strip().lower(), label="schema")
    table_ident  = _safe_ident(table_name.strip().lower(),  label="table")
    col_ident    = _safe_ident(sc.strip().lower(),          label="column")

    logger.debug(
        "[distinct_value] Resolved identifiers",
        extra={"schema_ident": schema_ident, "table_ident": table_ident, "col_ident": col_ident}
    )
    return schema_ident, table_ident, col_ident

@router.get("/values", response_model=List[str])
def fetch_values(
    workflow_id: int = Query(..., description="Workflow Id"),
    business_name: str = Query(..., description="Business name from input criteria (or 'Any')"),
    db: Session = Depends(get_db)
):
    """
    Returns distinct values for the given workflow_id and business_name:
    - Reads source_table/source_column from clientdb.mining_workflow_input_criteria_1
    - Fetches DISTINCT values from gold_copy.<table>.<column> (unless a schema is specified in source_table)
    - Appends 'Any' sentinel for UI
    """
    start_ts = time.perf_counter()
    logger.info(
        "[distinct_value] /fetch/values called",
        extra={"workflow_id": workflow_id, "business_name": business_name}
    )

    try:
        source_table, source_column = _get_source_table_column(db, workflow_id, business_name)
        schema_ident, table_ident, col_ident = _resolve_schema_table_column(source_table, source_column)

        distinct_sql = text(f"""
            SELECT DISTINCT {col_ident}
            FROM {schema_ident}.{table_ident}
            WHERE {col_ident} IS NOT NULL
            ORDER BY {col_ident} ASC
        """)

        logger.info(
            "[distinct_value] Executing DISTINCT query",
            extra={
                "sql": distinct_sql.text,
                "schema_ident": schema_ident,
                "table_ident": table_ident,
                "col_ident": col_ident
            }
        )
        logger.info(distinct_sql)
        rows = db.execute(distinct_sql).fetchall()
        elapsed_ms = (time.perf_counter() - start_ts) * 1000

        values = [r[0] for r in rows if r and r[0] is not None]
        logger.info(
            "[distinct_value] Query complete",
            extra={
                "row_count": len(values),
                "first_value": values[0] if values else None,
                "elapsed_ms": round(elapsed_ms, 2)
            }
        )

        # Append UI sentinel
        values.append("Any")
        return values

    except HTTPException as http_ex:
        logger.warning(
            "[distinct_value] HTTPException",
            extra={"workflow_id": workflow_id, "business_name": business_name, "detail": http_ex.detail, "status_code": http_ex.status_code}
        )
        raise
    except Exception as e:
        logger.exception(
            "fetch_values failed",
            extra={"workflow_id": workflow_id, "business_name": business_name}
        )
        # FIX: previously returned the function object; now we call it
        return JSONResponse(
                       status_code=500,
            content=error_response(500, "Internal Server Error while fetching distinct values")
        )