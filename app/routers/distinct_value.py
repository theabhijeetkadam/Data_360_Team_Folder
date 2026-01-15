
# app/routers/distinct_value.py

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Tuple, Optional, Any
import re
import logging
import time
from decimal import Decimal
from datetime import date, datetime, time as dtime

from app.database import get_db

router = APIRouter(prefix="/fetch", tags=["Fetch Values"])
logger = logging.getLogger(__name__)

# ---- Metadata table (lives in clientdb) ----
INPUT_CRITERIA_SCHEMA = "clientdb"
INPUT_CRITERIA_TABLE = "mining_workflow_input_criteria_1"  # lowercase, unquoted

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

# allow only standard SQL identifiers: letters, digits, underscore (first char letter/underscore)
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_ident(name: str, *, label: str) -> str:
    """
    Validate and return a safely quoted identifier for table/column names.
    Raises HTTPException(400) if invalid.
    """
    raw = name
    name = (name or "").strip()
    logger.debug(
        "[distinct_value] Validating identifier",
        extra={"label": label, "raw": raw, "normalized": name},
    )

    if not name or not IDENT_RE.match(name):
        logger.error(
            "[distinct_value] Invalid identifier detected",
            extra={"label": label, "name": raw},
        )
        raise HTTPException(status_code=400, detail=f"Invalid {label} identifier: {raw!r}")

    # Quote identifiers; Postgres will treat "name" as literal (case-sensitive)
    quoted = f'"{name}"'
    logger.debug(
        "[distinct_value] Identifier accepted",
        extra={"label": label, "quoted": quoted},
    )
    return quoted


def _get_source_table_column(db: Session, workflow_id: int, business_name: str) -> Tuple[str, str]:
    """
    Fetch source_table and source_column from clientdb.mining_workflow_input_criteria_1.
    Supports 'Any' fallback to pick first criteria in the workflow.
    """
    bn = (business_name or "").strip()
    logger.info(
        "[distinct_value] Fetching metadata",
        extra={"workflow_id": workflow_id, "business_name": bn},
    )

    sql = text(
        f"""
        SELECT source_table, source_column
        FROM {INPUT_CRITERIA_SCHEMA}.{INPUT_CRITERIA_TABLE}
        WHERE workflow_id = :workflow_id AND business_name = :business_name
        LIMIT 1
        """
    )
    logger.debug(
        "[distinct_value] Metadata query (exact business_name)",
        extra={"sql": sql.text, "workflow_id": workflow_id, "business_name": bn},
    )
    row = db.execute(sql, {"workflow_id": workflow_id, "business_name": bn}).fetchone()

    if not row and bn.lower() == "any":
        logger.info(
            "[distinct_value] No exact business_name; using 'Any' fallback",
            extra={"workflow_id": workflow_id},
        )
        sql_any = text(
            f"""
            SELECT source_table, source_column
            FROM {INPUT_CRITERIA_SCHEMA}.{INPUT_CRITERIA_TABLE}
            WHERE workflow_id = :workflow_id
            ORDER BY input_criteria_id
            LIMIT 1
            """
        )
        logger.debug(
            "[distinct_value] Metadata query (Any fallback)",
            extra={"sql": sql_any.text, "workflow_id": workflow_id},
        )
        row = db.execute(sql_any, {"workflow_id": workflow_id}).fetchone()

    if not row:
        logger.warning(
            "[distinct_value] Metadata not found",
            extra={"workflow_id": workflow_id, "business_name": bn},
        )
        raise HTTPException(
            status_code=404,
            detail="No matching metadata found for given workflow/business_name",
        )

    source_table, source_column = row[0], row[1]
    logger.info(
        "[distinct_value] Metadata found",
        extra={"source_table": source_table, "source_column": source_column},
    )
    return source_table, source_column


def _resolve_schema_table_column(source_table: str, source_column: str) -> Tuple[str, str, str, str, str]:
    """
    Determine schema and validate identifiers.
    - If source_table is 'schema.table', use that schema.
    - Else default schema to 'gold_copy' (per your architecture).

    Returns both quoted identifiers and unquoted lowercase names for catalog lookups:
    (schema_ident, table_ident, col_ident, schema_unq, table_unq, col_unq)
    """
    st_raw = source_table
    sc_raw = source_column
    st = (source_table or "").strip()
    sc = (source_column or "").strip()

    logger.debug(
        "[distinct_value] Resolving schema/table/column",
        extra={
            "source_table_raw": st_raw,
            "source_column_raw": sc_raw,
            "normalized_table": st,
            "normalized_column": sc,
        },
    )

    if "." in st:
        schema_name, table_name = st.split(".", 1)
        schema_name = schema_name.strip()
        table_name = table_name.strip()
        logger.info(
            "[distinct_value] Source table is qualified; using provided schema",
            extra={"schema_name": schema_name, "table_name": table_name},
        )
    else:
        schema_name, table_name = "gold_copy", st  # ✅ default to gold_copy for source data
        logger.info(
            "[distinct_value] Source table not qualified; defaulting schema",
            extra={"default_schema": "gold_copy", "table_name": table_name},
        )

    # Lower-case before quoting to align with unquoted Postgres identifiers
    schema_unq = schema_name.strip().lower()
    table_unq = table_name.strip().lower()
    col_unq = sc.strip().lower()

    schema_ident = _safe_ident(schema_unq, label="schema")
    table_ident = _safe_ident(table_unq, label="table")
    col_ident = _safe_ident(col_unq, label="column")

    logger.debug(
        "[distinct_value] Resolved identifiers",
        extra={
            "schema_ident": schema_ident,
            "table_ident": table_ident,
            "col_ident": col_ident,
            "schema_unq": schema_unq,
            "table_unq": table_unq,
            "col_unq": col_unq,
        },
    )
    return schema_ident, table_ident, col_ident, schema_unq, table_unq, col_unq


def _get_pg_data_type(db: Session, schema_unq: str, table_unq: str, col_unq: str) -> Optional[str]:
    """
    Lookup PostgreSQL data type from information_schema for the resolved schema/table/column.
    Returns data_type string (e.g., 'integer', 'numeric', 'text', 'date', 'timestamp with time zone', etc.)
    """
    type_sql = text(
        """
        SELECT data_type
        FROM information_schema.columns
        WHERE table_schema = :schema
          AND table_name  = :table
          AND column_name = :column
        LIMIT 1
        """
    )
    logger.debug(
        "[distinct_value] Inspecting column type",
        extra={"schema": schema_unq, "table": table_unq, "column": col_unq, "sql": type_sql.text},
    )
    row = db.execute(type_sql, {"schema": schema_unq, "table": table_unq, "column": col_unq}).fetchone()
    dtype = row[0] if row else None
    logger.info(
        "[distinct_value] Column type resolved",
        extra={"schema": schema_unq, "table": table_unq, "column": col_unq, "data_type": dtype},
    )
    return dtype


def _coerce_value_by_type(dtype: Optional[str], v: Any) -> Any:
    """
    Coerce DB value to a JSON-safe Python type based on PostgreSQL data type.
    """
    if v is None:
        return None

    # Normalize dtype to lower
    dt = (dtype or "").lower()

    # Integers
    if dt in {"integer", "bigint", "smallint"}:
        try:
            return int(v)
        except Exception:
            logger.debug("[distinct_value] int coercion failed; returning raw", extra={"value": v, "dtype": dt})
            return v

    # Numeric / Decimal / Floating
    if dt in {"numeric", "decimal", "real", "double precision"}:
        try:
            if isinstance(v, Decimal):
                return float(v)
            return float(v)
        except Exception:
            logger.debug("[distinct_value] float coercion failed; returning string", extra={"value": v, "dtype": dt})
            return str(v)

    # Boolean
    if dt == "boolean":
        try:
            return bool(v)
        except Exception:
            logger.debug("[distinct_value] bool coercion failed; returning raw", extra={"value": v, "dtype": dt})
            return v

    # Date / Timestamp / Time
    if dt in {"date"}:
        try:
            if isinstance(v, date):
                return v.isoformat()
            # fallback
            return str(v)
        except Exception:
            return str(v)

    if dt in {"timestamp without time zone", "timestamp with time zone"}:
        try:
            if isinstance(v, datetime):
                return v.isoformat()
            return str(v)
        except Exception:
            return str(v)

    if dt in {"time without time zone", "time with time zone"}:
        try:
            if isinstance(v, dtime):
                return v.isoformat()
            return str(v)
        except Exception:
            return str(v)

    # UUID
    if dt == "uuid":
        return str(v)

    # Textual types
    if dt in {"character varying", "varchar", "character", "char", "text"}:
        return str(v)

    # Fallback: stringify to be safe
    logger.debug("[distinct_value] Using fallback string coercion", extra={"value": v, "dtype": dt})
    return str(v)


@router.get("/values")
def fetch_values(
    workflow_id: int = Query(..., description="Workflow Id"),
    business_name: str = Query(..., description="Business name from input criteria (or 'Any')"),
    db: Session = Depends(get_db),
):
    """
    Returns distinct values for the given workflow_id and business_name:
    - Reads source_table/source_column from clientdb.mining_workflow_input_criteria_1
    - Fetches DISTINCT values from <schema>.<table>.<column>
    - Coerces values based on column type (integer/decimal/boolean/date/time/text/etc.)
    - Appends 'Any' sentinel for UI (as a string)
    """
    bn = (business_name or "").strip()
    start_ts = time.perf_counter()
    logger.info(
        "[distinct_value] /fetch/values called",
        extra={"workflow_id": workflow_id, "business_name": bn, "start_ts": start_ts},
    )

    try:
        # 1) Metadata
        source_table, source_column = _get_source_table_column(db, workflow_id, bn)

        # 2) Resolve identifiers (quoted + unquoted names)
        schema_ident, table_ident, col_ident, schema_unq, table_unq, col_unq = _resolve_schema_table_column(
            source_table, source_column
        )

        # 3) Determine column type
        dtype = _get_pg_data_type(db, schema_unq, table_unq, col_unq)

        # 4) DISTINCT SQL
        distinct_sql = text(
            f"""
            SELECT DISTINCT {col_ident}
            FROM {schema_ident}.{table_ident}
            WHERE {col_ident} IS NOT NULL
            ORDER BY {col_ident} ASC
            """
        )
        logger.info(
            "[distinct_value] Executing DISTINCT query",
            extra={
                "sql": distinct_sql.text,
                "schema_ident": schema_ident,
                "table_ident": table_ident,
                "col_ident": col_ident,
                "workflow_id": workflow_id,
                "business_name": bn,
                "resolved_data_type": dtype,
            },
        )

        rows = db.execute(distinct_sql).fetchall()
        elapsed_ms = round((time.perf_counter() - start_ts) * 1000, 2)

        # 5) Extract and coerce values by detected type
        raw_values = [r[0] for r in rows if r and r[0] is not None]
        values: List[Any] = [_coerce_value_by_type(dtype, v) for v in raw_values]

        sample = values[:5]
        logger.info(
            "[distinct_value] Query complete",
            extra={
                "row_count": len(values),
                "sample_values": sample,
                "elapsed_ms": elapsed_ms,
                "data_type": dtype,
            },
        )

        # 6) Append UI sentinel as a string (won't break JSON types)
        values.append("Any")
        logger.debug(
            "[distinct_value] Appended sentinel",
            extra={"sentinel": "Any", "final_count": len(values)},
        )

        # 7) Return JSON-safe payload
        return jsonable_encoder(values)

    except HTTPException as http_ex:
        logger.warning(
            "[distinct_value] HTTPException",
            extra={
                "workflow_id": workflow_id,
                "business_name": bn,
                "detail": http_ex.detail,
                "status_code": http_ex.status_code,
            },
        )
        raise
    except Exception as e:
        logger.exception(
                       "fetch_values failed",
            extra={"workflow_id": workflow_id, "business_name": bn},
        )
        return JSONResponse(
            status_code=500,
            content=error_response(500, "Internal Server Error while fetching")
        )
