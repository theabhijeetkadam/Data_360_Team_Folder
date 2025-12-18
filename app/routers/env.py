from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.env import EnvironmentCreate
from app.crud.env import (
    create_environment, get_environment, get_environments,
    update_environment, delete_environment
)
from app.exceptions import NotFoundError

router = APIRouter(prefix="/Env_Management_Module", tags=["Environments"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Helper to convert SQLAlchemy object to dict
def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Create Environment
@router.post("/", response_model=dict)
def create(env: EnvironmentCreate, db: Session = Depends(get_db)):
    db_env = create_environment(db, env)
    return {
        "message": "Environment created successfully.",
        "data": to_dict(db_env),
        "code": "200"
    }

# ✅ Read Environment by ID
@router.get("/{env_id}", response_model=dict)
def read(env_id: int, db: Session = Depends(get_db)):
    db_env = get_environment(db, env_id)
    if not db_env:
        raise NotFoundError(message="Environment not found", code="404")
    return {
        "message": "Environment details retrieved successfully.",
        "data": to_dict(db_env),
        "code": "200"
    }

# ✅ Read All Environments
@router.get("/", response_model=dict)
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    envs = get_environments(db, skip, limit)
    return {
        "message": "Environment list retrieved successfully.",
        "data": [to_dict(e) for e in envs],
        "code": "200"
    }

# ✅ Update Environment
@router.put("/{env_id}", response_model=dict)
def update(env_id: int, env: EnvironmentCreate, db: Session = Depends(get_db)):
    db_env = update_environment(db, env_id, env)
    if not db_env:
        raise NotFoundError(message="Resource to update not found", code="404")
    return {
        "message": "Environment updated successfully.",
        "data": to_dict(db_env),
        "code": "200"
    }

# ✅ Delete Environment
@router.delete("/{env_id}", response_model=dict)
def delete(env_id: int, db: Session = Depends(get_db)):
    db_env = delete_environment(db, env_id)
    if not db_env:
        raise NotFoundError(message="Resource to delete not found", code="404")
    return {
        "message": "Environment deleted successfully.",
        "data": to_dict(db_env),
        "code": "200"
    }