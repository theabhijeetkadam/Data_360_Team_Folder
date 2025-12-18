from sqlalchemy.orm import Session
from app.models.sequence_mappings import SequenceMapping
from app.schemas import sequence_mappings as schemas

def create_sequence(db: Session, sequence: schemas.SequenceMappingCreate):
    db_sequence = SequenceMapping(**sequence.dict())
    db.add(db_sequence)
    db.commit()
    db.refresh(db_sequence)
    return db_sequence

def get_all_sequences(db: Session):
    return db.query(SequenceMapping).all()

def get_sequence_by_id(db: Session, sequence_id: int):
    return db.query(SequenceMapping).filter(SequenceMapping.sequence_id == sequence_id).first()

def update_sequence(db: Session, sequence_id: int, sequence: schemas.SequenceMappingUpdate):
    db_sequence = db.query(SequenceMapping).filter(SequenceMapping.sequence_id == sequence_id).first()
    if not db_sequence:
        return None
    for key, value in sequence.dict(exclude_unset=True).items():
        setattr(db_sequence, key, value)
    db.commit()
    db.refresh(db_sequence)
    return db_sequence

def delete_sequence(db: Session, sequence_id: int):
    db_sequence = db.query(SequenceMapping).filter(SequenceMapping.sequence_id == sequence_id).first()
    if not db_sequence:
        return None
    db.delete(db_sequence)
    db.commit()
    return db_sequence
