
# app/crud/fnr_project_summary.py
import logging
import json
import time
from typing import List, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

logger = logging.getLogger(__name__)


def _safe_preview(rows: List[Dict], n: int = 2) -> str:
    try:
        return json.dumps(rows[:n], ensure_ascii=False)
    except Exception:
        return f"<preview unavailable; len={len(rows)}>"

# -------------------------------------------------
# Project summary
# -------------------------------------------------

def get_fnr_project_summary(db: Session, env_only: bool = True) -> List[Dict]:
    """
    One row per project_id.
    Base set: public.project_table (canonical_project).
    Counts from reserve; env_only affects counts only.
    Fallback name from reserve if project_table name is missing.
    """
    sql = """
        WITH canonical_project AS (
            SELECT
                pt.project_id,
                MAX(pt.project_name) AS project_name
            FROM public.project_table pt
            GROUP BY pt.project_id
        ),
        counts AS (
            SELECT
                mwr.project_id,
                COUNT(DISTINCT mwr.workflow_id) AS number_of_workflows
            FROM clientdb.mining_workflows_reserve AS mwr
            WHERE mwr.project_id IS NOT NULL
              AND mwr.workflow_id IS NOT NULL
              {env_filter}
            GROUP BY mwr.project_id
        ),
        reserve_name AS (
            SELECT
                mwr.project_id,
                MIN(mwr.project_name) AS fallback_name
            FROM clientdb.mining_workflows_reserve AS mwr
            WHERE mwr.project_id IS NOT NULL
            GROUP BY mwr.project_id
        )
        SELECT
            cp.project_id,
            COALESCE(cp.project_name, rn.fallback_name) AS project_name,
            1 AS number_of_modules,
            COALESCE(c.number_of_workflows, 0) AS number_of_workflows
        FROM canonical_project cp
        LEFT JOIN counts c
               ON c.project_id = cp.project_id
        LEFT JOIN reserve_name rn
               ON rn.project_id = cp.project_id
        ORDER BY cp.project_id;
    """.format(env_filter="AND mwr.env_id IS NOT NULL" if env_only else "")

    logger.info("FnR Project Summary: starting SQL", extra={"env_only": env_only})
    start_ms = time.time()
    try:
        result = db.execute(text(sql))
        rows = [dict(row) for row in result.mappings().all()]
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.info(
            "FnR Project Summary: success",
            extra={
                "row_count": len(rows),
                "elapsed_ms": elapsed_ms,
                "preview": _safe_preview(rows),
                "env_only": env_only,
            },
        )
        return rows
    except Exception:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Project Summary: failed",
            extra={"elapsed_ms": elapsed_ms, "env_only": env_only},
        )
        raise

# -------------------------------------------------
# Helpers
# -------------------------------------------------

def get_project_name_by_id(db: Session, project_id: int) -> Optional[str]:
    sql = text("""
        SELECT project_name
        FROM public.project_table
        WHERE project_id = :pid
        ORDER BY project_name DESC
        LIMIT 1
    """)
    row = db.execute(sql, {"pid": project_id}).mappings().first()
    if not row:
        return None
    return row.get("project_name") or None

# -------------------------------------------------
# Workflows list for a given project_id
# -------------------------------------------------

def get_fnr_workflows_for_project(
    db: Session,
    project_id: int,
    limit: int | None = None,
    offset: int | None = None,
    **kwargs,  # accepts env_only
):
    """
    Returns list of workflows {workflow_id, workflow_name} belonging to the given project_id.
    Pagination via limit/offset is applied to workflows.

    If 'env_only' is passed and True, restrict to workflows that have env_id IS NOT NULL in reserve.
    We treat reserve (clientdb.mining_workflows_reserve) as the authoritative source for project_id.
    """
    env_only = bool(kwargs.get("env_only", False))

    base_sql = """
        WITH input_ctx AS (
            SELECT
                ic.workflow_id,
                MAX(ic.project_id)       AS project_id,
                MAX(ic.project_name)     AS project_name
            FROM clientdb.mining_workflow_input_criteria_1 ic
            GROUP BY ic.workflow_id
        ),
        output_ctx AS (
            SELECT
                oc.workflow_id,
                MAX(oc.project_id)       AS project_id,
                MAX(oc.project_name)     AS project_name
            FROM clientdb.mining_workflow_output_criteria_1 oc
            GROUP BY oc.workflow_id
        ),
        wf_ctx AS (
            SELECT
                COALESCE(i.workflow_id, o.workflow_id)     AS workflow_id,
                COALESCE(i.project_id,  o.project_id)      AS project_id,
                COALESCE(i.project_name, o.project_name)   AS project_name
            FROM input_ctx i
            FULL OUTER JOIN output_ctx o
              ON i.workflow_id = o.workflow_id
        )
        SELECT DISTINCT
            mwr.workflow_id,
            mwr.workflow_name
        FROM clientdb.mining_workflows_reserve AS mwr
        LEFT JOIN wf_ctx AS ctx
               ON ctx.workflow_id = mwr.workflow_id
        WHERE
            mwr.project_id = :project_id
            {env_filter}
        ORDER BY mwr.workflow_name
    """.format(env_filter="\n  AND mwr.env_id IS NOT NULL" if env_only else "")

    logger.info(
        "FnR Workflow Summary: starting",
        extra={
            "fnr_area": "workflow_summary",
            "project_id": project_id,
            "limit": limit,
            "offset": offset,
            "env_only": env_only,
        },
    )

    sql = base_sql
    params = {"project_id": project_id}

    if limit is not None:
        sql += "\nLIMIT :limit"
        params["limit"] = limit
    if offset is not None:
        sql += "\nOFFSET :offset"
        params["offset"] = offset

    start_ms = time.time()
    try:
        result = db.execute(text(sql), params)
        rows = result.mappings().all()
        payload = [{"workflow_id": r["workflow_id"], "workflow_name": r["workflow_name"]} for r in rows]
        elapsed_ms = int((time.time() - start_ms) * 1000)

        logger.info(
            "FnR Workflow Summary: executed successfully",
            extra={
                "fnr_area": "workflow_summary",
                "project_id": project_id,
                "row_count": len(payload),
                "elapsed_ms": elapsed_ms,
                "preview": _safe_preview(payload),
                "env_only": env_only,
            },
        )
        return payload
    except Exception:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Workflow Summary: SQL execution failed",
            extra={
                "fnr_area": "workflow_summary",
                "project_id": project_id,
                "elapsed_ms": elapsed_ms,
                "limit": limit,
                "offset": offset,
                "env_only": env_only,
            },
        )
        raise
