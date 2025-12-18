
# app/routers/fnr_project_summary.py
import logging
import json
import time
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import SessionLocal
from app.schemas.fnr_project_summary import (
    FnrProjectSummaryOut,
    FnrWorkflowSummaryOut,
    FnrWorkflowSummaryItem,
)
from app.crud.fnr_project_summary import (
    get_fnr_project_summary,
    get_fnr_workflows_for_project,
    get_project_name_by_id
)

# Module-level logger (inherits app/global logging config if present)
logger = logging.getLogger(__name__)

def _safe_preview(rows, n: int = 2) -> str:
    """Return a small, JSON-safe preview of rows for logs (max n items)."""
    try:
        return json.dumps(rows[:n], ensure_ascii=False)
    except Exception:
        return f"<preview unavailable; len={len(rows)}>"

# Existing router for Project Summary
router = APIRouter(prefix="/fnr/project-summary", tags=["FnR Project Summary"])

# ✅ Router for Workflow Summary
workflow_router = APIRouter(prefix="/fnr/workflow-summary", tags=["FnR Workflow Summary"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# Existing: Read Project Summary
# ------------------------------
@router.get("/", response_model=list[FnrProjectSummaryOut])
def read_project_summary(db: Session = Depends(get_db)):
    start_ms = time.time()
    logger.info("FnR Project Summary: request started")
    try:
        rows = get_fnr_project_summary(db)
        elapsed_ms = int((time.time() - start_ms) * 1000)

        logger.info(
            "FnR Project Summary: success",
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
            "FnR Project Summary: failed",
            extra={"fnr_area": "project_summary", "elapsed_ms": elapsed_ms},
        )
        raise HTTPException(status_code=500, detail=f"Failed to compute summary: {str(e)}")

# --------------------------------
# ✅ Read Workflow Summary BY project_id
# --------------------------------
@workflow_router.get("/", response_model=FnrWorkflowSummaryOut)
def read_workflow_summary(
    project_id: int = Query(..., gt=0),          # ✅ required project_id
    limit: Optional[int] = Query(None, gt=0),
    offset: Optional[int] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    start_ms = time.time()
    logger.info(
        "FnR Workflow Summary: request started",
        extra={
            "fnr_area": "workflow_summary",
            "project_id": project_id,
            "limit": limit,
            "offset": offset,
        },
    )
    try:
        workflows = get_fnr_workflows_for_project(
            db=db,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )

        # If you want to populate project_name here, we can add a tiny helper
        # (e.g., get_project_name_by_id) to resolve it from project_table.
        
        canonical_name = get_project_name_by_id(db, project_id)
        if canonical_name is None:
        # 400 Bad Request: invalid/missing project_id in project_table
        # (Not using 404 since the resource is identified by query input—not a path parameter)
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
            },
        )
        raise HTTPException(status_code=500, detail=f"Failed to compute workflow summary: {str(e)}")
