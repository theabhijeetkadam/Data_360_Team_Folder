from sqlalchemy.orm import Session
from app.models import db_workflow_deleted_logs as models
from app.schemas import db_workflow_deleted_logs as schemas

def create_deleted_log(db: Session, log: schemas.DeletedLogCreate):
    db_log = models.DBWorkflowDeletedLogs(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
