from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.feature_role_access_matrix import FeatureRoleAccessMatrix, FeatureRoleAccessMatrixCreate
from app.crud.feature_role_access_matrix import (
    create_feature_role_access_matrix, get_feature_role_access_matrix, get_feature_role_access_matrices,
    update_feature_role_access_matrix, delete_feature_role_access_matrix
)

router = APIRouter(prefix="/feature_role_access_matrix", tags=["Feature Role Access Matrix"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=FeatureRoleAccessMatrix)
def create(matrix: FeatureRoleAccessMatrixCreate, db: Session = Depends(get_db)):
    return create_feature_role_access_matrix(db, matrix)

@router.get("/{matrix_id}", response_model=FeatureRoleAccessMatrix)
def read(matrix_id: int, db: Session = Depends(get_db)):
    db_matrix = get_feature_role_access_matrix(db, matrix_id)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix

@router.get("/", response_model=list[FeatureRoleAccessMatrix])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_feature_role_access_matrices(db, skip, limit)

@router.put("/{matrix_id}", response_model=FeatureRoleAccessMatrix)
def update(matrix_id: int, matrix: FeatureRoleAccessMatrixCreate, db: Session = Depends(get_db)):
    db_matrix = update_feature_role_access_matrix(db, matrix_id, matrix)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix

@router.delete("/{matrix_id}", response_model=FeatureRoleAccessMatrix)
def delete(matrix_id: int, db: Session = Depends(get_db)):
    db_matrix = delete_feature_role_access_matrix(db, matrix_id)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix