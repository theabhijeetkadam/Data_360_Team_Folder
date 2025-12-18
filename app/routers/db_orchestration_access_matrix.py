from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import db_orchestration_access_matrix as schemas
from app.crud import db_orchestration_access_matrix as crud

router = APIRouter(
    prefix="/access-matrix",
    tags=["DB Orchestration Access Matrix"]
)

@router.post("/", response_model=schemas.AccessMatrixResponse)
def create_access_matrix(matrix: schemas.AccessMatrixCreate, db: Session = Depends(get_db)):
    return crud.create_access_matrix(db, matrix)

@router.get("/", response_model=list[schemas.AccessMatrixResponse])
def get_all_access_matrix(db: Session = Depends(get_db)):
    return crud.get_all_access_matrix(db)

@router.get("/{matrix_id}", response_model=schemas.AccessMatrixResponse)
def get_access_matrix_by_id(matrix_id: int, db: Session = Depends(get_db)):
    db_matrix = crud.get_access_matrix_by_id(db, matrix_id)
    if not db_matrix:
        raise HTTPException(status_code=404, detail="Access matrix not found")
    return db_matrix

@router.put("/{matrix_id}", response_model=schemas.AccessMatrixResponse)
def update_access_matrix(matrix_id: int, matrix: schemas.AccessMatrixUpdate, db: Session = Depends(get_db)):
    updated = crud.update_access_matrix(db, matrix_id, matrix)
    if not updated:
        raise HTTPException(status_code=404, detail="Access matrix not found")
    return updated

@router.delete("/{matrix_id}")
def delete_access_matrix(matrix_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_access_matrix(db, matrix_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Access matrix not found")
    return {"message": "Access matrix deleted successfully"}
