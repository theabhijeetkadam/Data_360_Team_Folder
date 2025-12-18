from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.environment_instance import EnvironmentInstance
from app.schemas.environment_instance import EnvironmentInstanceCreate
from app.exceptions import DBReadError, DBInsertError

def get_all_instances(db: Session):
    try:
        return db.query(EnvironmentInstance).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"Failed to fetch environment instances: {str(e)}")

def create_instance(db: Session, instance: EnvironmentInstanceCreate):
    try:
        db_instance = EnvironmentInstance(**instance.dict())
        db.add(db_instance)
        db.commit()
        db.refresh(db_instance)
        return db_instance
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"Failed to create environment instance: {str(e)}")