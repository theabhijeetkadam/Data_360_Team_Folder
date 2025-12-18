from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.env import Environment
from app.schemas.env import EnvironmentCreate
from app.exceptions import (
    DBInsertError, DBReadError, DBUpdateError, DBDeleteError,
    NotFoundError, DuplicateEntryError
)

def create_environment(db: Session, env: EnvironmentCreate):
    try:
        # ✅ Check if environment already exists (env_name + env_instance)
        existing_env = db.query(Environment).filter(
            Environment.env_name == env.env_name,
            Environment.env_instance == env.env_instance
        ).first()
        if existing_env:
            raise DuplicateEntryError(message="Environment already exists", code="409")

        db_env = Environment(**env.dict())
        db.add(db_env)
        db.commit()
        db.refresh(db_env)
        return db_env

    except DuplicateEntryError:
        raise
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"DB operation failed while creating environment: {str(e)}", code="500")


def get_environment(db: Session, env_id: int):
    try:
        env = db.query(Environment).filter(Environment.env_id == env_id).first()
        if not env:
            raise NotFoundError(message="Environment not found", code="404")
        return env
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading environment: {str(e)}", code="500")


def get_environments(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Environment).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading environments: {str(e)}", code="500")


def update_environment(db: Session, env_id: int, env: EnvironmentCreate):
    try:
        db_env = db.query(Environment).filter(Environment.env_id == env_id).first()
        if not db_env:
            raise NotFoundError(message="Resource to update not found", code="404")

        # ✅ Check for duplicate name-instance combination
        conflict_env = db.query(Environment).filter(
            Environment.env_name == env.env_name,
            Environment.env_instance == env.env_instance,
            Environment.env_id != env_id
        ).first()
        if conflict_env:
            raise DuplicateEntryError(message="Environment with same name and instance already exists", code="409")

        for key, value in env.dict().items():
            setattr(db_env, key, value)

        db.commit()
        db.refresh(db_env)
        return db_env

    except DuplicateEntryError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(message=f"DB operation failed while updating environment: {str(e)}", code="500")


def delete_environment(db: Session, env_id: int):
    try:
        db_env = db.query(Environment).filter(Environment.env_id == env_id).first()
        if not db_env:
            raise NotFoundError(message="Resource to delete not found", code="404")

        db.delete(db_env)
        db.commit()
        return db_env

    except SQLAlchemyError as e:
        db.rollback()
        raise DBDeleteError(message=f"DB operation failed while deleting environment: {str(e)}", code="500")
