from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.feature_names import FeatureNamesCreate
from app.crud.feature_names import (
    create_feature_name, get_feature_name, get_feature_names,
    update_feature_name, delete_feature_name
)
from app.exceptions import NotFoundError

router = APIRouter(prefix="/feature_names", tags=["Feature Names"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Helper to convert SQLAlchemy object to dict
def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Create Feature
@router.post("/", response_model=dict)
def create(feature: FeatureNamesCreate, db: Session = Depends(get_db)):
    db_feature = create_feature_name(db, feature)
    return {
        "message": "Feature created successfully.",
        "data": to_dict(db_feature),
        "code": "200"
    }

# ✅ Read Feature by ID
@router.get("/{feature_id}", response_model=dict)
def read(feature_id: int, db: Session = Depends(get_db)):
    db_feature = get_feature_name(db, feature_id)
    if not db_feature:
        raise NotFoundError(message="Feature not found", code="404")
    return {
        "message": "Feature details retrieved successfully.",
        "data": to_dict(db_feature),
        "code": "200"
    }

# ✅ Read All Features
@router.get("/", response_model=dict)
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    features = get_feature_names(db, skip, limit)
    return {
        "message": "Feature list retrieved successfully.",
        "data": [to_dict(f) for f in features],
        "code": "200"
    }

# ✅ Update Feature
@router.put("/{feature_id}", response_model=dict)
def update(feature_id: int, feature: FeatureNamesCreate, db: Session = Depends(get_db)):
    db_feature = update_feature_name(db, feature_id, feature)
    if not db_feature:
        raise NotFoundError(message="Resource to update not found", code="ERR_007")
    return {
        "message": "Feature updated successfully.",
        "data": to_dict(db_feature),
        "code": "200"
    }

# ✅ Delete Feature
@router.delete("/{feature_id}", response_model=dict)
def delete(feature_id: int, db: Session = Depends(get_db)):
    db_feature = delete_feature_name(db, feature_id)
    if not db_feature:
        raise NotFoundError(message="Resource to delete not found", code="ERR_009")
    return {
        "message": "Feature deleted successfully.",
        "data": to_dict(db_feature),
        "code": "200"
    }