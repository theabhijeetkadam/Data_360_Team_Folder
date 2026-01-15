
# app/routers/genrocket_services_details.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.crud import genrocket_services_details as crud

# ✅ Import the same schemas where tool_id is declared as int
from app.schemas.genrocket_services_details import (
    GenRocketServicesDetailsCreate,
    GenRocketServicesDetailsUpdate,
    GenRocketServicesDetailsResponse,
)

router = APIRouter(prefix="/genrocket_services_details", tags=["GenRocket Services Details"])

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# --- List all services ---
@router.get("/", response_model=List[GenRocketServicesDetailsResponse], operation_id="gsd_list_all")
def read_services(db: Session = Depends(get_db)):
    services = crud.get_all_services(db)
    # Return typed models (FastAPI will serialize automatically)
    return services

# --- Get one by workflow_id ---
@router.get("/{workflow_id}", response_model=GenRocketServicesDetailsResponse, operation_id="gsd_get_by_workflow_id")
def read_service(workflow_id: int, db: Session = Depends(get_db)):
    db_service = crud.get_service_by_id(db, workflow_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

# --- Create ---
@router.post("/", response_model=GenRocketServicesDetailsResponse, operation_id="gsd_create")
def create_service(service: GenRocketServicesDetailsCreate, db: Session = Depends(get_db)):
    # The request body schema (GenRocketServicesDetailsCreate) must have tool_id: int
    db_service = crud.create_service(db, service)
    return db_service

# --- Update ---
@router.put("/{workflow_id}", response_model=GenRocketServicesDetailsResponse, operation_id="gsd_update")
def update_service(workflow_id: int, service: GenRocketServicesDetailsUpdate, db: Session = Depends(get_db)):
    db_service = crud.update_service(db, workflow_id, service)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service

# --- Delete ---
@router.delete("/{workflow_id}", response_model=GenRocketServicesDetailsResponse, operation_id="gsd_delete")
def delete_service(workflow_id: int, db: Session = Depends(get_db)):
    db_service = crud.delete_service(db, workflow_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    return db_service
