from sqlalchemy.orm import Session
from app.models.runtime_logs import RuntimeLog
from app.schemas import runtime_logs as schemas

def create_runtime_log(db: Session, log: schemas.RuntimeLogCreate):
    db_log = RuntimeLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_all_runtime_logs(db: Session):
    return db.query(RuntimeLog).all()

def get_runtime_log_by_id(db: Session, execution_id: int):
    return db.query(RuntimeLog).filter(RuntimeLog.execution_id == execution_id).first()

def update_runtime_log(db: Session, execution_id: int, log: schemas.RuntimeLogUpdate):
    db_log = db.query(RuntimeLog).filter(RuntimeLog.execution_id == execution_id).first()
    if not db_log:
        return None
    for key, value in log.dict(exclude_unset=True).items():
        setattr(db_log, key, value)
    db.commit()
    db.refresh(db_log)
    return db_log

def delete_runtime_log(db: Session, execution_id: int):
    db_log = db.query(RuntimeLog).filter(RuntimeLog.execution_id == execution_id).first()
    if not db_log:
        return None
    db.delete(db_log)
    db.commit()
    return db_log
