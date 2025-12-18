
# app/routers/workflow_summary.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.workflow_summary import WorkflowItem, WorkflowSummaryResponse
from app.crud.workflow_summary import get_workflow_summary_by_project_id  # ✅ new import

router = APIRouter(prefix="/genrocket/workflow-summary", tags=["GenRocket Workflow Summary"])

@router.get(
    "",
    response_model=WorkflowSummaryResponse,
    operation_id="genrocket_workflow_summary_get",
)
def get_workflow_summary(
    project_id: int = Query(..., gt=0, description="Project id to filter workflows"),  # ✅ required
    limit: Optional[int] = Query(None, ge=1, le=500, description="Optional page size for workflows"),
    offset: Optional[int] = Query(None, ge=0, description="Optional offset for workflows"),
    db: Session = Depends(get_db),
):
    """
    Returns: { project_name, project_id, workflows: [{workflow_id, workflow_name}, ...] }
    """
    try:
        pn, pid, rows = get_workflow_summary_by_project_id(
            db=db,
            project_id=project_id,
            limit=limit,
            offset=offset,
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

    if pid == -1 or not rows:
        raise HTTPException(status_code=404, detail=f"No workflows found for project_id='{project_id}'")

    return WorkflowSummaryResponse(
        project_name=pn,
        project_id=pid,
        workflows=[WorkflowItem(workflow_id=wid, workflow_name=wname) for wid, wname in rows],
    )
