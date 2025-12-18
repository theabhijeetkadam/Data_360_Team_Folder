from sqlalchemy.orm import Session
from app.models.db_defination_table import DBDefinationTable
from app.schemas.db_defination_table import DBDefinationTableCreate
from fastapi import HTTPException

def create_db_defination(db: Session, db_def: DBDefinationTableCreate):
    db_db_def = DBDefinationTable(**db_def.dict())
    db.add(db_db_def)
    db.commit()
    db.refresh(db_db_def)
    return db_db_def

def get_db_defination(db: Session, db_id: int):
    return db.query(DBDefinationTable).filter(DBDefinationTable.db_id == db_id).first()

def get_db_definations(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DBDefinationTable).offset(skip).limit(limit).all()

def update_db_defination(db: Session, db_id: int, db_def: DBDefinationTableCreate):
    db_db_def = db.query(DBDefinationTable).filter(DBDefinationTable.db_id == db_id).first()
    if db_db_def:
        for key, value in db_def.dict().items():
            setattr(db_db_def, key, value)
        db.commit()
        db.refresh(db_db_def)
    return db_db_def

def delete_db_defination(db: Session, db_id: int):
    db_db_def = db.query(DBDefinationTable).filter(DBDefinationTable.db_id == db_id).first()
    if not db_db_def:
        raise HTTPException(status_code=404, detail="project not found")
    db.delete(db_db_def)
    db.commit()
    return {"message": "Project deleted successfully"}