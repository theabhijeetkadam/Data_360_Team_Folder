from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import environment_instance as crud
from app.schemas.environment_instance import EnvironmentInstanceCreate

router = APIRouter(prefix="/environment_instance", tags=["Environment Instance"])

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

@router.get("/", response_model=dict)
def read_instances(db: Session = Depends(get_db)):
    instances = crud.get_all_instances(db)
    return {"message": "Environment instances retrieved successfully", "data": [to_dict(i) for i in instances], "code": "200"}

@router.post("/", response_model=dict)
def create_instance(instance: EnvironmentInstanceCreate, db: Session = Depends(get_db)):
    db_instance = crud.create_instance(db, instance)
    return {"message": "Environment instance created successfully", "data": to_dict(db_instance), "code": "200"}