from sqlalchemy.orm import Session
from app.models.db_orchestration_access_matrix import DBOrchestrationAccessMatrix
from app.schemas import db_orchestration_access_matrix as schemas

def create_access_matrix(db: Session, matrix: schemas.AccessMatrixCreate):
    db_matrix = DBOrchestrationAccessMatrix(**matrix.dict())
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)
    return db_matrix

def get_all_access_matrix(db: Session):
    return db.query(DBOrchestrationAccessMatrix).all()

def get_access_matrix_by_id(db: Session, matrix_id: int):
    return db.query(DBOrchestrationAccessMatrix).filter(DBOrchestrationAccessMatrix.id == matrix_id).first()

def update_access_matrix(db: Session, matrix_id: int, matrix: schemas.AccessMatrixUpdate):
    db_matrix = db.query(DBOrchestrationAccessMatrix).filter(DBOrchestrationAccessMatrix.id == matrix_id).first()
    if not db_matrix:
        return None
    for key, value in matrix.dict(exclude_unset=True).items():
        setattr(db_matrix, key, value)
    db.commit()
    db.refresh(db_matrix)
    return db_matrix

def delete_access_matrix(db: Session, matrix_id: int):
    db_matrix = db.query(DBOrchestrationAccessMatrix).filter(DBOrchestrationAccessMatrix.id == matrix_id).first()
    if not db_matrix:
        return None
    db.delete(db_matrix)
    db.commit()
    return db_matrix
