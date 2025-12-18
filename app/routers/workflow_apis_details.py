from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.workflow_apis_details import (
    WorkflowAPIDetailsCreate,
    WorkflowAPIDetailsUpdate,
    WorkflowAPIDetailsResponse,
)
from app.crud import workflow_apis_details as crud
from app.database import get_db

router = APIRouter(prefix="/workflow-apis", tags=["Workflow API Details"])

@router.post("/", response_model=WorkflowAPIDetailsResponse)
def create_api(api: WorkflowAPIDetailsCreate, db: Session = Depends(get_db)):
    return crud.create_workflow_api(db, api)

@router.get("/", response_model=List[WorkflowAPIDetailsResponse])
def list_apis(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_workflow_apis(db, skip=skip, limit=limit)

@router.get("/{api_id}", response_model=WorkflowAPIDetailsResponse)
def get_api(api_id: int, db: Session = Depends(get_db)):
    db_api = crud.get_workflow_api(db, api_id)
    if not db_api:
        raise HTTPException(status_code=404, detail="API not found")
    return db_api

@router.put("/{api_id}", response_model=WorkflowAPIDetailsResponse)
def update_api(api_id: int, api: WorkflowAPIDetailsUpdate, db: Session = Depends(get_db)):
    db_api = crud.update_workflow_api(db, api_id, api)
    if not db_api:
        raise HTTPException(status_code=404, detail="API not found")
    return db_api

@router.delete("/{api_id}", response_model=WorkflowAPIDetailsResponse)
def delete_api(api_id: int, db: Session = Depends(get_db)):
    db_api = crud.delete_workflow_api(db, api_id)
    if not db_api:
        raise HTTPException(status_code=404, detail="API not found")
    return db_api
