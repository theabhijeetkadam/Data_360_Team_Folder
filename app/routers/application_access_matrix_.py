from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.application_access_matrix import (
    ApplicationAccessMatrixCreate,
    ApplicationAccessMatrixUpdate,
    ApplicationAccessMatrixOut
)
from app.crud import application_access_matrix
from app.database import get_db

router = APIRouter(
    prefix="/application_access_matrix",
    tags=["Application Access Matrix"]
)

@router.get("/", response_model=List[ApplicationAccessMatrixOut])
def read_all(db: Session = Depends(get_db)):
    return application_access_matrix.get_all(db)

@router.get("/{id}", response_model=ApplicationAccessMatrixOut)
def read_by_id(id: int, db: Session = Depends(get_db)):
    db_obj = application_access_matrix.get_by_id(db, id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_obj

@router.post("/", response_model=ApplicationAccessMatrixOut)
def create(obj: ApplicationAccessMatrixCreate, db: Session = Depends(get_db)):
    return application_access_matrix.create(db, obj)

@router.put("/{id}", response_model=ApplicationAccessMatrixOut)
def update(id: int, obj: ApplicationAccessMatrixUpdate, db: Session = Depends(get_db)):
    updated_obj = application_access_matrix.update(db, id, obj)
    if not updated_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_obj

@router.delete("/{id}", response_model=ApplicationAccessMatrixOut)
def delete(id: int, db: Session = Depends(get_db)):
    deleted_obj = application_access_matrix.delete(db, id)
    if not deleted_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return deleted_obj
