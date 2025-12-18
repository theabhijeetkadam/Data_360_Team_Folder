from sqlalchemy.orm import Session
from app.models.aa_workflow_deleted_logs import AAWorkflowDeletedLogs
from app.schemas.aa_workflow_deleted_logs import AAWorkflowDeletedLogsCreate

def create_deleted_log(db: Session, log: AAWorkflowDeletedLogsCreate):
    new_log = AAWorkflowDeletedLogs(**log.dict())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log
