from sqlalchemy.orm import Session
from app.models.api_sequence import APISequence
from app.schemas.api_sequence import APISequenceCreate, APISequenceUpdate

def get_sequences(db: Session, skip: int = 0, limit: int = 100):
    return db.query(APISequence).offset(skip).limit(limit).all()

def get_sequence(db: Session, sequence_id: int):
    return db.query(APISequence).filter(APISequence.sequence_id == sequence_id).first()

def create_sequence(db: Session, sequence: APISequenceCreate):
    db_seq = APISequence(**sequence.dict())
    db.add(db_seq)
    db.commit()
    db.refresh(db_seq)
    return db_seq

def update_sequence(db: Session, sequence_id: int, sequence: APISequenceUpdate):
    db_seq = db.query(APISequence).filter(APISequence.sequence_id == sequence_id).first()
    if db_seq:
        for key, value in sequence.dict(exclude_unset=True).items():
            setattr(db_seq, key, value)
        db.commit()
        db.refresh(db_seq)
    return db_seq

def delete_sequence(db: Session, sequence_id: int):
    db_seq = db.query(APISequence).filter(APISequence.sequence_id == sequence_id).first()
    if db_seq:
        db.delete(db_seq)
        db.commit()
    return db_seq