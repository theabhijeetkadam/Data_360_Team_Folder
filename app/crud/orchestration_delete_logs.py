from sqlalchemy.orm import Session
from app.models.orchestration_delete_logs import OrchestrationDeleteLogs  # Model
from app.schemas.orchestration_delete_logs import OrchestrationDeleteLogCreate, OrchestrationDeleteLogUpdate

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(OrchestrationDeleteLogs).offset(skip).limit(limit).all()

def get_log(db: Session, log_id: int):
    return db.query(OrchestrationDeleteLogs).filter(OrchestrationDeleteLogs.log_id == log_id).first()

def create_log(db: Session, log: OrchestrationDeleteLogCreate):
    last_record = db.query(OrchestrationDeleteLogs).order_by(OrchestrationDeleteLogs.record_id.desc()).first()
    record_id = (last_record.module_id + 1) if last_record else 1

    last_project = db.query(OrchestrationDeleteLogs).order_by(OrchestrationDeleteLogs.deleted_project_id.desc()).first()
    deleted_project_id = (last_project.module_id + 1) if last_project else 1

    last_service = db.query(OrchestrationDeleteLogs).order_by(OrchestrationDeleteLogs.service_id.desc()).first()
    service_id = (last_service.service_id + 1) if last_service else 1

    db_log = OrchestrationDeleteLogs(**log.dict(),
        record_id=record_id,
        deleted_project_id=deleted_project_id,
         service_id= service_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_log(db: Session, log_id: int, log: OrchestrationDeleteLogUpdate):
    db_log = db.query(OrchestrationDeleteLogs).filter(OrchestrationDeleteLogs.log_id == log_id).first()
    if db_log:
        for key, value in log.dict(exclude_unset=True).items():
            setattr(db_log, key, value)
        db.commit()
        db.refresh(db_log)
    return db_log

def delete_log(db: Session, log_id: int):
    db_log = db.query(OrchestrationDeleteLogs).filter(OrchestrationDeleteLogs.log_id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
    return db_log