from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.api_mappings import (
    ApiMappingsCreate,
    ApiMappingsUpdate,
    ApiMappingsOut
)
from app.crud import crud_api_mappings
from app.database import get_db

router = APIRouter(
    prefix="/api_mappings",
    tags=["API Mappings"]
)

@router.get("/", response_model=List[ApiMappingsOut])
def read_all(db: Session = Depends(get_db)):
    return crud_api_mappings.get_all(db)

@router.get("/{mapping_id}", response_model=ApiMappingsOut)
def read_by_id(mapping_id: int, db: Session = Depends(get_db)):
    db_obj = crud_api_mappings.get_by_id(db, mapping_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return db_obj

@router.post("/", response_model=ApiMappingsOut)
def create(obj: ApiMappingsCreate, db: Session = Depends(get_db)):
    return crud_api_mappings.create(db, obj)

@router.put("/{mapping_id}", response_model=ApiMappingsOut)
def update(mapping_id: int, obj: ApiMappingsUpdate, db: Session = Depends(get_db)):
    updated_obj = crud_api_mappings.update(db, mapping_id, obj)
    if not updated_obj:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return updated_obj

@router.delete("/{mapping_id}", response_model=ApiMappingsOut)
def delete(mapping_id: int, db: Session = Depends(get_db)):
    deleted_obj = crud_api_mappings.delete(db, mapping_id)
    if not deleted_obj:
        raise HTTPException(status_code=404, detail="Mapping not found")
    return deleted_obj
