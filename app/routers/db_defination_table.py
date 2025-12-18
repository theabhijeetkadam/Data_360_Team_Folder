from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.db_defination_table import DBDefinationTable, DBDefinationTableCreate
from app.crud.db_defination_table import (
    create_db_defination, get_db_defination, get_db_definations,
    update_db_defination, delete_db_defination
)
from pydantic import BaseModel

# ✅ Define MessageResponse schema
class MessageResponse(BaseModel):
    message: str

router = APIRouter(prefix="/db_definations", tags=["DB Defination Table"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DBDefinationTable)
def create(db_def: DBDefinationTableCreate, db: Session = Depends(get_db)):
    return create_db_defination(db, db_def)

@router.get("/{db_id}", response_model=DBDefinationTable)
def read(db_id: int, db: Session = Depends(get_db)):
    db_def = get_db_defination(db, db_id)
    if not db_def:
        raise HTTPException(status_code=404, detail="DB Defination not found")
    return db_def

@router.get("/", response_model=list[DBDefinationTable])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_db_definations(db, skip, limit)

@router.put("/{db_id}", response_model=DBDefinationTable)
def update(db_id: int, db_def: DBDefinationTableCreate, db: Session = Depends(get_db)):
    db_def_updated = update_db_defination(db, db_id, db_def)
    if not db_def_updated:
        raise HTTPException(status_code=404, detail="DB Defination not found")
    return db_def_updated

@router.delete("/{db_id}", response_model=MessageResponse)
def delete(db_id: int, db: Session = Depends(get_db)):
    db_def = delete_db_defination(db, db_id)
    if not db_def:
        raise HTTPException(status_code=404, detail="DB Defination not found")
    return {"message": f"DB Defination with ID {db_id} deleted successfully"}