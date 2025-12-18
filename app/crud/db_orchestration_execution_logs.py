from sqlalchemy.orm import Session
from app.models import db_orchestration_execution_logs as models
from app.schemas import db_orchestration_execution_logs as schemas

def create_execution_log(db: Session, log: schemas.ExecutionLogCreate):
    db_log = models.DBOrchestrationExecutionLogs(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
