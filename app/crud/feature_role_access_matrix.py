from sqlalchemy.orm import Session
from app.models.feature_role_access_matrix import FeatureRoleAccessMatrix
from app.schemas.feature_role_access_matrix import FeatureRoleAccessMatrixCreate

def create_feature_role_access_matrix(db: Session, matrix: FeatureRoleAccessMatrixCreate):
    db_matrix = FeatureRoleAccessMatrix(**matrix.dict())
    db.add(db_matrix)
    db.commit()
    db.refresh(db_matrix)
    return db_matrix

def get_feature_role_access_matrix(db: Session, matrix_id: int):
    return db.query(FeatureRoleAccessMatrix).filter(FeatureRoleAccessMatrix.matrix_id == matrix_id).first()

def get_feature_role_access_matrices(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FeatureRoleAccessMatrix).offset(skip).limit(limit).all()

def update_feature_role_access_matrix(db: Session, matrix_id: int, matrix: FeatureRoleAccessMatrixCreate):
    db_matrix = db.query(FeatureRoleAccessMatrix).filter(FeatureRoleAccessMatrix.matrix_id == matrix_id).first()
    if db_matrix:
        for key, value in matrix.dict().items():
            setattr(db_matrix, key, value)
        db.commit()
        db.refresh(db_matrix)
    return db_matrix

def delete_feature_role_access_matrix(db: Session, matrix_id: int):
    db_matrix = db.query(FeatureRoleAccessMatrix).filter(FeatureRoleAccessMatrix.matrix_id == matrix_id).first()
    if db_matrix:
        db.delete(db_matrix)
        db.commit()
    return db_matrix