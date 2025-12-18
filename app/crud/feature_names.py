from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.feature_names import FeatureNames
from app.schemas.feature_names import FeatureNamesCreate
from app.exceptions import (
    DuplicateEntryError, DBInsertError, DBReadError,
    DBUpdateError, DBDeleteError
)

def create_feature_name(db: Session, feature: FeatureNamesCreate):
    try:
        db_feature = FeatureNames(**feature.dict())
        db.add(db_feature)
        db.commit()
        db.refresh(db_feature)
        return db_feature
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError()
    except Exception:
        db.rollback()
        raise DBInsertError()

def get_feature_name(db: Session, feature_id: int):
    try:
        return db.query(FeatureNames).filter(FeatureNames.feature_id == feature_id).first()
    except Exception:
        raise DBReadError()

def get_feature_names(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(FeatureNames).offset(skip).limit(limit).all()
    except Exception:
        raise DBReadError()

def update_feature_name(db: Session, feature_id: int, feature: FeatureNamesCreate):
    try:
        db_feature = db.query(FeatureNames).filter(FeatureNames.feature_id == feature_id).first()
        if db_feature:
            for key, value in feature.dict().items():
                setattr(db_feature, key, value)
            db.commit()
            db.refresh(db_feature)
        return db_feature
    except Exception:
        db.rollback()
        raise DBUpdateError()

def delete_feature_name(db: Session, feature_id: int):
    try:
        db_feature = db.query(FeatureNames).filter(FeatureNames.feature_id == feature_id).first()
        if db_feature:
            db.delete(db_feature)
            db.commit()
        return db_feature
    except IntegrityError:
        db.rollback()
        raise DBDeleteError()
    except Exception:
        db.rollback()
        raise DBDeleteError()