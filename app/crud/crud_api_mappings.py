from sqlalchemy.orm import Session
from app.models.api_mappings import ApiMappings
from app.schemas.api_mappings import ApiMappingsCreate, ApiMappingsUpdate

def get_all(db: Session):
    return db.query(ApiMappings).all()

def get_by_id(db: Session, mapping_id: int):
    return db.query(ApiMappings).filter(ApiMappings.mapping_id == mapping_id).first()

def create(db: Session, obj: ApiMappingsCreate):
    db_obj = ApiMappings(**obj.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, mapping_id: int, obj: ApiMappingsUpdate):
    db_obj = db.query(ApiMappings).filter(ApiMappings.mapping_id == mapping_id).first()
    if not db_obj:
        return None
    for key, value in obj.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, mapping_id: int):
    db_obj = db.query(ApiMappings).filter(ApiMappings.mapping_id == mapping_id).first()
    if not db_obj:
        return None
    db.delete(db_obj)
    db.commit()
    return db_obj
