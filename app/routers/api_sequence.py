from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud.api_sequence import create_sequence, get_sequences, get_sequence, update_sequence, delete_sequence
from app.schemas.api_sequence import APISequenceCreate, APISequence, APISequenceUpdate
from app.database import get_db

router = APIRouter(prefix="/api-sequence", tags=["API Sequence"])

@router.get("/", response_model=List[APISequence])
def read_sequences(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_sequences(db, skip=skip, limit=limit)

@router.get("/{sequence_id}", response_model=APISequence)
def read_sequence(sequence_id: int, db: Session = Depends(get_db)):
    db_seq = get_sequence(db, sequence_id)
    if not db_seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return db_seq

@router.post("/", response_model=APISequence)
def create_new_sequence(sequence: APISequenceCreate, db: Session = Depends(get_db)):
    return create_sequence(db, sequence)

@router.put("/{sequence_id}", response_model=APISequence)
def update_existing_sequence(sequence_id: int, sequence: APISequenceUpdate, db: Session = Depends(get_db)):
    db_seq = update_sequence(db, sequence_id, sequence)
    if not db_seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return db_seq

@router.delete("/{sequence_id}", response_model=APISequence)
def delete_existing_sequence(sequence_id: int, db: Session = Depends(get_db)):
    db_seq = delete_sequence(db, sequence_id)
    if not db_seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return db_seq