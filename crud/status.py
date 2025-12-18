from sqlalchemy.orm import Session
from ..models.status import Status
from ..schemas import StatusCreate, StatusUpdate

def create_status(db: Session, status: StatusCreate):
    db_status = Status(entity_type=status.entity_type, status_value=status.status_value)
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    return db_status

def get_status(db: Session, status_id: int):
    return db.query(Status).filter(Status.status_id == status_id).first()

def get_all_status(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Status).offset(skip).limit(limit).all()

def update_status(db: Session, status_id: int, status: StatusUpdate):
    db_status = db.query(Status).filter(Status.status_id == status_id).first()
    if db_status:
        db_status.entity_type = status.entity_type
        db_status.status_value = status.status_value
        db.commit()
        db.refresh(db_status)
    return db_status

def delete_status(db: Session, status_id: int):
    db_status = db.query(Status).filter(Status.status_id == status_id).first()
    if db_status:
        db.delete(db_status)
        db.commit()
    return db_status