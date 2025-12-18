from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user_app_matrix import UserAppMatrix, UserAppMatrixCreate
from app.crud.user_app_matrix import (
    create_user_app_matrix, get_user_app_matrix, get_user_app_matrices,
    update_user_app_matrix, delete_user_app_matrix
)

router = APIRouter(prefix="/user_app_matrix", tags=["User App Matrix"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserAppMatrix)
def create(matrix: UserAppMatrixCreate, db: Session = Depends(get_db)):
    return create_user_app_matrix(db, matrix)

@router.get("/{matrix_id}", response_model=UserAppMatrix)
def read(matrix_id: int, db: Session = Depends(get_db)):
    db_matrix = get_user_app_matrix(db, matrix_id)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix

@router.get("/", response_model=list[UserAppMatrix])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_user_app_matrices(db, skip, limit)

@router.put("/{matrix_id}", response_model=UserAppMatrix)
def update(matrix_id: int, matrix: UserAppMatrixCreate, db: Session = Depends(get_db)):
    db_matrix = update_user_app_matrix(db, matrix_id, matrix)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix

@router.delete("/{matrix_id}", response_model=UserAppMatrix)
def delete(matrix_id: int, db: Session = Depends(get_db)):
    db_matrix = delete_user_app_matrix(db, matrix_id)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Matrix not found")
    return db_matrix