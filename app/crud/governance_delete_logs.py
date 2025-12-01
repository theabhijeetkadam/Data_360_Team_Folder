from sqlalchemy.orm import Session
from app.models.governance_delete_logs import GovernanceDeleteLogs
from app.schemas.governance_delete_logs import GovernanceDeleteLogCreate, GovernanceDeleteLogUpdate

def get_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(GovernanceDeleteLogs).offset(skip).limit(limit).all()

def get_log(db: Session, log_id: int):
    return db.query(GovernanceDeleteLogs).filter(GovernanceDeleteLogs.log_id == log_id).first()

def create_log(db: Session, log: GovernanceDeleteLogCreate):
    last_project = db.query(GovernanceDeleteLogs).order_by(GovernanceDeleteLogs.deleted_project_id.desc()).first()
    deleted_project_id = (last_project.deleted_project_id + 1) if last_project else 1

    last_env = db.query(GovernanceDeleteLogs).order_by(GovernanceDeleteLogs.deleted_environment_id.desc()).first()
    deleted_environment_id = (last_env.deleted_environment_id + 1) if last_env else 1

    db_log = GovernanceDeleteLogs(**log.dict(),
        deleted_project_id=deleted_project_id,
         deleted_environment_id= deleted_environment_id,
         )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def update_log(db: Session, log_id: int, log: GovernanceDeleteLogUpdate):
    db_log = db.query(GovernanceDeleteLogs).filter(GovernanceDeleteLogs.log_id == log_id).first()
    if db_log:
        for key, value in log.dict(exclude_unset=True).items():
            setattr(db_log, key, value)
        db.commit()
        db.refresh(db_log)
    return db_log

def delete_log(db: Session, log_id: int):
    db_log = db.query(GovernanceDeleteLogs).filter(GovernanceDeleteLogs.log_id == log_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
    return db_log
