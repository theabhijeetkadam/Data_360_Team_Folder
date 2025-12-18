from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import sequence_mappings as schemas
from app.crud import sequence_mappings as crud

router = APIRouter(
    prefix="/sequence-mappings",
    tags=["Sequence Mappings"]
)

@router.post("/", response_model=schemas.SequenceMappingResponse)
def create_sequence(sequence: schemas.SequenceMappingCreate, db: Session = Depends(get_db)):
    return crud.create_sequence(db, sequence)

@router.get("/", response_model=list[schemas.SequenceMappingResponse])
def get_all_sequences(db: Session = Depends(get_db)):
    return crud.get_all_sequences(db)

@router.get("/{sequence_id}", response_model=schemas.SequenceMappingResponse)
def get_sequence(sequence_id: int, db: Session = Depends(get_db)):
    db_sequence = crud.get_sequence_by_id(db, sequence_id)
    if not db_sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return db_sequence

@router.put("/{sequence_id}", response_model=schemas.SequenceMappingResponse)
def update_sequence(sequence_id: int, sequence: schemas.SequenceMappingUpdate, db: Session = Depends(get_db)):
    updated = crud.update_sequence(db, sequence_id, sequence)
    if not updated:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return updated

@router.delete("/{sequence_id}")
def delete_sequence(sequence_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_sequence(db, sequence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return {"message": "Sequence deleted successfully"}
