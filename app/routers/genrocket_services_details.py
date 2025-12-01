
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import genrocket_services_details as crud
from app.schemas.genrocket_services_details import GenRocketServicesDetailsCreate, GenRocketServicesDetailsUpdate

router = APIRouter(prefix="/genrocket_services_details", tags=["GenRocket Services Details"])

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

@router.get("/", response_model=dict)
def read_services(db: Session = Depends(get_db)):
    services = crud.get_all_services(db)
    return {"message": "Services retrieved successfully", "data": [to_dict(s) for s in services], "code": "200"}

@router.get("/{workflow_id}", response_model=dict)
def read_service(workflow_id: int, db: Session = Depends(get_db)):
    db_service = crud.get_service_by_id(db, workflow_id)
    return {"message": "Service details retrieved successfully", "data": to_dict(db_service), "code": "200"}

@router.post("/", response_model=dict)
def create_service(service: GenRocketServicesDetailsCreate, db: Session = Depends(get_db)):
    db_service = crud.create_service(db, service)
    return {"message": "Service created successfully", "data": to_dict(db_service), "code": "200"}

@router.put("/{workflow_id}", response_model=dict)
def update_service(workflow_id: int, service: GenRocketServicesDetailsUpdate, db: Session = Depends(get_db)):
    db_service = crud.update_service(db, workflow_id, service)
    return {"message": "Service updated successfully", "data": to_dict(db_service), "code": "200"}

@router.delete("/{workflow_id}", response_model=dict)
def delete_service(workflow_id: int, db: Session = Depends(get_db)):
    db_service = crud.delete_service(db, workflow_id)
    return {"message": "Service deleted successfully", "data": to_dict(db_service), "code": "200"}
