from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas import excel_mappings as schemas
from app.crud import excel_mappings as crud

router = APIRouter(
    prefix="/excel-mappings",
    tags=["Excel Mappings"]
)

@router.get("/", response_model=List[schemas.ExcelMappingsOut])
def read_excel_mappings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_excel_mappings(db, skip=skip, limit=limit)

@router.get("/{excel_mapping_id}", response_model=schemas.ExcelMappingsOut)
def read_excel_mapping(excel_mapping_id: int, db: Session = Depends(get_db)):
    db_mapping = crud.get_excel_mapping(db, excel_mapping_id)
    if db_mapping is None:
        raise HTTPException(status_code=404, detail="Excel mapping not found")
    return db_mapping

@router.post("/", response_model=schemas.ExcelMappingsOut)
def create_excel_mapping(mapping: schemas.ExcelMappingsCreate, db: Session = Depends(get_db)):
    return crud.create_excel_mapping(db, mapping)

@router.put("/{excel_mapping_id}", response_model=schemas.ExcelMappingsOut)
def update_excel_mapping(excel_mapping_id: int, mapping: schemas.ExcelMappingsUpdate, db: Session = Depends(get_db)):
    db_mapping = crud.update_excel_mapping(db, excel_mapping_id, mapping)
    if db_mapping is None:
        raise HTTPException(status_code=404, detail="Excel mapping not found")
    return db_mapping

@router.delete("/{excel_mapping_id}", response_model=schemas.ExcelMappingsOut)
def delete_excel_mapping(excel_mapping_id: int, db: Session = Depends(get_db)):
    db_mapping = crud.delete_excel_mapping(db, excel_mapping_id)
    if db_mapping is None:
        raise HTTPException(status_code=404, detail="Excel mapping not found")
    return db_mapping
