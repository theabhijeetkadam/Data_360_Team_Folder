
# app/crud/fnr_project_summary.py
import logging
import json
import time
from sqlalchemy.orm import Session
from sqlalchemy import text

# Module-level logger (inherits app logging config if set)
logger = logging.getLogger(__name__)

def _safe_preview(rows, n=2):
    """Return a small, JSON-safe preview of rows for logs (max n items)."""
    try:
        return json.dumps(rows[:n], ensure_ascii=False)
    except Exception:
        # Fallback: avoid logging serialization errors
        return f"<{min(len(rows), n)} rows preview unavailable>"


def get_fnr_project_summary(db: Session):
    sql = text("""
        WITH input_ctx AS (
            SELECT
                ic.workflow_id,
                MAX(ic.project_id)       AS project_id,
                MAX(ic.project_name)     AS project_name,
                MAX(ic.environment_name) AS environment_name,
                MAX(ic.module_name)      AS module_name
            FROM clientdb.mining_workflow_input_criteria_1 ic
            GROUP BY ic.workflow_id
        ),
        output_ctx AS (
            SELECT
                oc.workflow_id,
                MAX(oc.project_id)       AS project_id,
                MAX(oc.project_name)     AS project_name,
                MAX(oc.environment_name) AS environment_name,
                MAX(oc.module_name)      AS module_name
            FROM clientdb.mining_workflow_output_criteria_1 oc
            GROUP BY oc.workflow_id
        ),
        wf_ctx AS (
            SELECT
                COALESCE(i.workflow_id, o.workflow_id)            AS workflow_id,
                COALESCE(i.project_id,     o.project_id)          AS project_id,
                COALESCE(i.project_name,   o.project_name)        AS project_name,
                COALESCE(i.environment_name, o.environment_name)  AS environment_name,
                COALESCE(i.module_name,      o.module_name)       AS module_name
            FROM input_ctx i
            FULL OUTER JOIN output_ctx o
              ON i.workflow_id = o.workflow_id
        ),
        modules AS (
            SELECT project_name, environment_name, module_id
            FROM clientdb.mining_workflow_input_criteria_1
            UNION
            SELECT project_name, environment_name, module_id
            FROM clientdb.mining_workflow_output_criteria_1
        ),
        module_counts AS (
            SELECT
                project_name,
                environment_name,
                COUNT(DISTINCT module_id) AS number_of_modules
            FROM modules
            GROUP BY project_name, environment_name
        ),
        workflow_counts AS (
            SELECT
                project_name,
                environment_name,
                COUNT(DISTINCT workflow_id) AS number_of_workflows
            FROM wf_ctx
            GROUP BY project_name, environment_name
        )
        SELECT
            mwr.workflow_id,
            mwr.workflow_name,
            COALESCE(ctx.project_id,     0)  AS project_id,
            COALESCE(ctx.project_name,   '') AS project_name,
            COALESCE(ctx.environment_name, '') AS environment_name,
            COALESCE(ctx.module_name,      '') AS module_name,
            COALESCE(mc.number_of_modules, 0)      AS number_of_modules,
            COALESCE(wc.number_of_workflows, 0)    AS number_of_workflows
        FROM clientdb.mining_workflows_reserve AS mwr
        INNER JOIN wf_ctx AS ctx                      -- ✅ require presence in input/output criteria
               ON ctx.workflow_id = mwr.workflow_id
        LEFT JOIN module_counts AS mc
               ON mc.project_name     = ctx.project_name
              AND mc.environment_name = ctx.environment_name
        LEFT JOIN workflow_counts AS wc
               ON wc.project_name     = ctx.project_name
              AND wc.environment_name = ctx.environment_name
        ORDER BY mwr.workflow_name;
    """)

    logger.info("FnR Project Summary: starting SQL execution")
    start_ms = time.time()
    try:
        result = db.execute(sql)
        rows = [dict(row) for row in result.mappings().all()]
        elapsed_ms = int((time.time() - start_ms) * 1000)

        logger.info(
            "FnR Project Summary: executed successfully",
            extra={
                "fnr_area": "project_summary",
                "row_count": len(rows),
                "elapsed_ms": elapsed_ms,
                "preview": _safe_preview(rows),
            },
        )
        return rows
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Project Summary: SQL execution failed",
            extra={"fnr_area": "project_summary", "elapsed_ms": elapsed_ms},
        )
        # Bubble up so FastAPI returns 500 with your router's handler
        raise

# -------------------------------------------------
# Project Name for a given project_id
# -------------------------------------------------


def get_project_name_by_id(db: Session, project_id: int) -> str | None:
    """
    Returns canonical project_name for the given project_id from public.project_table.
    If not found, returns None.
    """
    sql = text("""
        SELECT project_name
        FROM public.project_table
        WHERE project_id = :pid
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
):
    """
    Returns list of workflows {workflow_id, workflow_name} belonging to the given project_id.
    Pagination via limit/offset is applied to workflows.
    """
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
        SELECT
            mwr.workflow_id,
            mwr.workflow_name
        FROM clientdb.mining_workflows_reserve AS mwr
        LEFT JOIN wf_ctx AS ctx
               ON ctx.workflow_id = mwr.workflow_id
        WHERE ctx.project_id = :project_id
        ORDER BY mwr.workflow_name
    """

    logger.info(
        "FnR Workflow Summary: starting",
        extra={
            "fnr_area": "workflow_summary",
            "project_id": project_id,
            "limit": limit,
            "offset": offset,
        },
    )

    sql = base_sql
    if limit is not None:
        sql += "\nLIMIT :limit"
    if offset is not None:
        sql += "\nOFFSET :offset"

    params = {
        "project_id": project_id,
        "limit": limit,
        "offset": offset,
    }

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
            },
        )
        return payload
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Workflow Summary: SQL execution failed",
            extra={
                "fnr_area": "workflow_summary",
                "project_id": project_id,
                "elapsed_ms": elapsed_ms,
                "limit": limit,
                "offset": offset,
            },
        )
        raise
