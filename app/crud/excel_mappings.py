from sqlalchemy.orm import Session
from app.models import excel_mappings
from app.schemas import excel_mappings as schemas

def get_excel_mappings(db: Session, skip: int = 0, limit: int = 100):
    return db.query(excel_mappings.ExcelMappings).offset(skip).limit(limit).all()

def get_excel_mapping(db: Session, excel_mapping_id: int):
    return db.query(excel_mappings.ExcelMappings).filter(excel_mappings.ExcelMappings.excel_mapping_id == excel_mapping_id).first()

def create_excel_mapping(db: Session, mapping: schemas.ExcelMappingsCreate):
    db_mapping = excel_mappings.ExcelMappings(**mapping.dict())
    db.add(db_mapping)
    db.commit()
    db.refresh(db_mapping)
    return db_mapping

def update_excel_mapping(db: Session, excel_mapping_id: int, mapping: schemas.ExcelMappingsUpdate):
    db_mapping = get_excel_mapping(db, excel_mapping_id)
    if db_mapping:
        for key, value in mapping.dict().items():
            setattr(db_mapping, key, value)
        db.commit()
        db.refresh(db_mapping)
    return db_mapping

def delete_excel_mapping(db: Session, excel_mapping_id: int):
    db_mapping = get_excel_mapping(db, excel_mapping_id)
    if db_mapping:
        db.delete(db_mapping)
        db.commit()
    return db_mapping
