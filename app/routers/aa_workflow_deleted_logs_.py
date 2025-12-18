from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app import database
from app.schemas.aa_workflow_deleted_logs import AAWorkflowDeletedLogsCreate, AAWorkflowDeletedLogsOut
from app.crud.aa_workflow_deleted_logs import create_deleted_log

router = APIRouter(
    prefix="/aa_workflow_deleted_logs",
    tags=["AA Workflow Deleted Logs"]
)

@router.post("/", response_model=AAWorkflowDeletedLogsOut)
def create_deleted_log_route(
    log: AAWorkflowDeletedLogsCreate,
    db: Session = Depends(database.get_db)
):
    return create_deleted_log(db=db, log=log)
