from sqlalchemy.orm import Session
from app.models.application_access_matrix import ApplicationAccessMatrix
from app.schemas.application_access_matrix import (
    ApplicationAccessMatrixCreate,
    ApplicationAccessMatrixUpdate
)

def get_all(db: Session):
    return db.query(ApplicationAccessMatrix).all()

def get_by_id(db: Session, id: int):
    return db.query(ApplicationAccessMatrix).filter(ApplicationAccessMatrix.id == id).first()

def create(db: Session, obj: ApplicationAccessMatrixCreate):
    db_obj = ApplicationAccessMatrix(**obj.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, id: int, obj: ApplicationAccessMatrixUpdate):
    db_obj = db.query(ApplicationAccessMatrix).filter(ApplicationAccessMatrix.id == id).first()
    if not db_obj:
        return None
    for key, value in obj.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, id: int):
    db_obj = db.query(ApplicationAccessMatrix).filter(ApplicationAccessMatrix.id == id).first()
    if not db_obj:
        return None
    db.delete(db_obj)
    db.commit()
    return db_obj
