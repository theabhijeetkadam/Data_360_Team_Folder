from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import parameters_relation_details as crud
from app.schemas.parameters_relation_details import (
    ParametersRelationDetailsCreate,
    ParametersRelationDetailsUpdate,
    ParametersRelationDetailsOut
)

router = APIRouter(prefix="/relations", tags=["Parameters Relations"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.get("/{workflow_id}", response_model=list[ParametersRelationDetailsOut])
def get_by_id(workflow_id: int, db: Session = Depends(get_db)):
    record = crud.get_relation_by_workflow_id(db, workflow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("/", response_model=ParametersRelationDetailsOut)
def create_relation(data: ParametersRelationDetailsCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_relation(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[ParametersRelationDetailsOut])
def get_all(db: Session = Depends(get_db)):
    return crud.get_all_relations(db)

@router.get("/{relation_id}", response_model=ParametersRelationDetailsOut)
def get_by_id(relation_id: int, db: Session = Depends(get_db)):
    record = crud.get_relation_by_id(db, relation_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.put("/{relation_id}", response_model=ParametersRelationDetailsOut)
def update(relation_id: int, data: ParametersRelationDetailsUpdate, db: Session = Depends(get_db)):
    updated = crud.update_relation(db, relation_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Record not found")
    return updated

@router.delete("/{relation_id}")
def delete(relation_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_relation(db, relation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Deleted successfully"}
