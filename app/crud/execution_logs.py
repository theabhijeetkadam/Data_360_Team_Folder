from sqlalchemy.orm import Session
from app.models import execution_logs as models
from app.schemas import execution_logs as schemas

def create_execution_log(db: Session, log: schemas.ExecutionLogCreate):
    db_log = models.ExecutionLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_execution_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ExecutionLog).offset(skip).limit(limit).all()

def get_execution_log(db: Session, execution_id: int):
    return db.query(models.ExecutionLog).filter(models.ExecutionLog.execution_id == execution_id).first()

def update_execution_log(db: Session, execution_id: int, log: schemas.ExecutionLogUpdate):
    db_log = db.query(models.ExecutionLog).filter(models.ExecutionLog.execution_id == execution_id).first()
    if db_log:
        for key, value in log.dict(exclude_unset=True).items():
            setattr(db_log, key, value)
        db.commit()
        db.refresh(db_log)
    return db_log

def delete_execution_log(db: Session, execution_id: int):
    db_log = db.query(models.ExecutionLog).filter(models.ExecutionLog.execution_id == execution_id).first()
    if db_log:
        db.delete(db_log)
        db.commit()
    return db_log
