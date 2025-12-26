
# app/crud/distinct_value.py

import logging
import re
import time
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.distinct_value import MiningWorkflowInputCriteria

# Configure a module-level logger
logger = logging.getLogger(__name__)

# ---------- ORM helper: criteria lookups in clientdb ----------
def get_criteria_by_business_name(db: Session, workflow_id: int, business_name: str) -> List[MiningWorkflowInputCriteria]:
    """
    Returns criteria rows matching workflow_id and business_name (from clientdb.mining_workflow_input_criteria_1),
    or all for the workflow if 'Any' is passed.
    """
    bn = (business_name or "").strip()
    logger.info(
        "[distinct_value][CRUD] get_criteria_by_business_name called",
        extra={"workflow_id": workflow_id, "business_name": bn},
    )

    try:
        q = db.query(MiningWorkflowInputCriteria).filter(MiningWorkflowInputCriteria.workflow_id == workflow_id)
        logger.debug(
            "[distinct_value][CRUD] Base query built",
            extra={"workflow_id": workflow_id},
        )

        if bn.lower() != "any":
            q = q.filter(MiningWorkflowInputCriteria.business_name == bn)
            logger.debug(
                "[distinct_value][CRUD] Applied business_name filter",
                extra={"workflow_id": workflow_id, "business_name": bn},
            )
        else:
            logger.debug(
                "[distinct_value][CRUD] 'Any' requested; skipping business_name filter",
                extra={"workflow_id": workflow_id},
            )

        rows = q.all()
        logger.info(
            "[distinct_value][CRUD] Criteria lookup complete",
            extra={"workflow_id": workflow_id, "business_name": bn, "row_count": len(rows)},
        )
        # Optionally log a sample of rows (safe fields only)
        if rows:
            sample = [{
                "input_criteria_id": r.input_criteria_id,
                "business_name": r.business_name,
                "source_table": r.source_table,
                "source_column": r.source_column,
                # "source_schema": getattr(r, "source_schema", None),  # uncomment if model includes it
            } for r in rows[:5]]
            logger.debug(
                "[distinct_value][CRUD] Criteria sample",
                extra={"sample": sample},
            )
        return rows

    except Exception as e:
        logger.exception(
            "[distinct_value][CRUD] Failed to fetch criteria by business_name",
            extra={"workflow_id": workflow_id, "business_name": bn},
        )
        # Propagate; the router should wrap/handle appropriately
        raise


# ---------- Raw SQL helper: distinct values from source schema ----------
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_ident(name: str) -> str:
    raw = name
    name = (name or "").strip()
    logger.debug(
        "[distinct_value][CRUD] Validating identifier",
        extra={"raw": raw, "normalized": name},
    )

    if not name or not IDENT_RE.match(name):
        logger.error(
            "[distinct_value][CRUD] Invalid identifier",
            extra={"raw": raw, "normalized": name},
        )
        raise ValueError(f"Invalid identifier: {raw!r}")

    quoted = f'"{name}"'
    logger.debug(
        "[distinct_value][CRUD] Identifier accepted",
        extra={"quoted": quoted},
    )
    return quoted


def get_value_from_source_table(db: Session, source_schema: str, source_table: str, source_column: str) -> List[str]:
    """
    Fetch distinct values from the given source schema.table.column.
    Defaults to gold_copy at call sites if schema not provided.
    """
    ss_raw, st_raw, sc_raw = source_schema, source_table, source_column
    ss = (source_schema or "").strip().lower()
    st = (source_table or "").strip().lower()
    sc = (source_column or "").strip().lower()

    logger.info(
        "[distinct_value][CRUD] get_value_from_source_table called",
        extra={"source_schema": ss_raw, "source_table": st_raw, "source_column": sc_raw},
    )

    try:
        schema_ident = _safe_ident(ss)
        table_ident  = _safe_ident(st)
        column_ident = _safe_ident(sc)

        sql = text(f"""
            SELECT DISTINCT {column_ident}
            FROM {schema_ident}.{table_ident}
            WHERE {column_ident} IS NOT NULL
            ORDER BY {column_ident} ASC
        """)

        start_ts = time.perf_counter()
        logger.info(
            "[distinct_value][CRUD] Executing DISTINCT SQL",
            extra={
                "sql": sql.text,
                "schema_ident": schema_ident,
                "table_ident": table_ident,
                "column_ident": column_ident,
            },
        )

        rows = db.execute(sql).fetchall()
        elapsed_ms = round((time.perf_counter() - start_ts) * 1000, 2)

        values = [r[0] for r in rows if r and r[0] is not None]
        logger.info(
            "[distinct_value][CRUD] DISTINCT query complete",
            extra={"row_count": len(values), "elapsed_ms": elapsed_ms},
        )

        # Log a sample of the values to aid debugging without log flooding
        if values:
            logger.debug(
                "[distinct_value][CRUD] Values sample",
                extra={"sample_values": values[:5]},
            )

        return values

    except ValueError as ve:
        # Identifier validation errors
        logger.warning(
            "[distinct_value][CRUD] Validation error during identifier handling",
            extra={"error": str(ve), "source_schema": ss_raw, "source_table": st_raw, "source_column": sc_raw},
        )
        raise
    except Exception as e:
        logger.exception(
            "[distinct_value][CRUD] Failed to fetch distinct values",
            extra={"source_schema": ss_raw, "source_table": st_raw, "source_column": sc_raw},
               )
