# app/routers/fnr_project_summary.py
import logging
import json
import time
import inspect
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from sqlalchemy.orm import Session
from typing import List, Dict

from app.database import SessionLocal
from app.schemas.fnr_project_summary import (
    FnrProjectSummaryOut, 
    FnrWorkflowSummaryOut,
    FnrWorkflowSummaryItem
)
from app.crud.fnr_project_summary import (
    get_fnr_project_summary,
    get_fnr_workflows_for_project,
    get_project_name_by_id
)

logger = logging.getLogger(__name__)

def _safe_preview(rows: List[Dict], n: int = 2) -> str:
    try:
        return json.dumps(rows[:n], ensure_ascii=False)
    except Exception:
        return f"<preview unavailable; len={len(rows)}>"

router = APIRouter(prefix="/fnr/project-summary", tags=["FnR Project Summary"])

workflow_router = APIRouter(prefix="/fnr/workflow-summary", tags=["FnR Workflow Summary"])
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# Read Project Summary (reserve-only)
# ------------------------------
@router.get("/", response_model=list[FnrProjectSummaryOut])
def read_project_summary(db: Session = Depends(get_db)):
    start_ms = time.time()

    # 🔎 DEBUG: confirm which file the function comes from (helpful if multiple copies exist)
    logger.warning(
        "Using get_fnr_project_summary from %s:%s",
        inspect.getsourcefile(get_fnr_project_summary),
        inspect.getsourcelines(get_fnr_project_summary)[1],
    )

    logger.info("FnR Project Summary: request started")
    try:
        # env_only=True → only workflows with env_id (if you need all workflows, set env_only=False)
        rows = get_fnr_project_summary(db, env_only=True)
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.info(
            "FnR Project Summary: success",
            extra={
                "fnr_area": "project_summary",
                "row_count": len(rows),
                "elapsed_ms": elapsed_ms,
                "preview": _safe_preview(rows),
                "env_only": True,
            },
        )
        return rows
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Project Summary: failed",
            extra={"fnr_area": "project_summary", "elapsed_ms": elapsed_ms, "env_only": True},
        )
        raise HTTPException(status_code=500, detail=f"Failed to compute summary: {str(e)}")

# --------------------------------
# Read Workflow Summary BY project_id
# --------------------------------
@workflow_router.get("/", response_model=FnrWorkflowSummaryOut)
def read_workflow_summary(
    project_id: int = Query(..., gt=0),
    limit: Optional[int] = Query(None, gt=0),
    offset: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    start_ms = time.time()
    # 🔎 DEBUG: confirm file for workflows function
    logger.warning(
        "Using get_fnr_workflows_for_project from %s:%s",
        inspect.getsourcefile(get_fnr_workflows_for_project),
        inspect.getsourcelines(get_fnr_workflows_for_project)[1],
    )

    logger.info(
        "FnR Workflow Summary: request started",
        extra={"fnr_area": "workflow_summary", "project_id": project_id, "limit": limit, "offset": offset, "env_only": True},
    )
    try:
        workflows = get_fnr_workflows_for_project(
            db=db,
            project_id=project_id,
            limit=limit,
            offset=offset,
            env_only=True,
        )

        canonical_name = get_project_name_by_id(db, project_id)
        if canonical_name is None:
            raise HTTPException(status_code=400, detail=f"Project not found for project_id={project_id}")

        payload = FnrWorkflowSummaryOut(
            project_name=canonical_name,
            project_id=project_id,
            workflows=[FnrWorkflowSummaryItem(**wf) for wf in workflows],
        )

        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.info(
            "FnR Workflow Summary: success",
            extra={
                "fnr_area": "workflow_summary",
                "project_id": project_id,
                "row_count": len(payload.workflows),
                "elapsed_ms": elapsed_ms,
                "preview": _safe_preview(payload.workflows),
                "env_only": True,
            },
        )
        return payload
    except Exception as e:
        elapsed_ms = int((time.time() - start_ms) * 1000)
        logger.exception(
            "FnR Workflow Summary: failed",
            extra={
                "fnr_area": "workflow_summary",
                "project_id": project_id,
                "limit": limit,
                "offset": offset,
                "elapsed_ms": elapsed_ms,
                "env_only": True,
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to compute workflow summary: {str(e)}")
