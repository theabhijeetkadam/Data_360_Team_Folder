from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas import WorkflowCreate, WorkflowResponse, WorkflowUpdate
from app.database import get_db
from app import crud

router = APIRouter(prefix="/workflows", tags=["Workflows"])

@router.post("/", response_model=WorkflowResponse)
def create_new_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    return crud.create_workflow(db, workflow)

@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_workflows(db, skip=skip, limit=limit)

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow_by_id(db, workflow_id)
    if not db_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return db_workflow

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: int, workflow: WorkflowUpdate, db: Session = Depends(get_db)):
    updated_workflow = crud.update_workflow(db, workflow_id, workflow)
    if not updated_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return updated_workflow

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    deleted_workflow = crud.delete_workflow(db, workflow_id)
    if not deleted_workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"detail": f"Workflow {workflow_id} deleted successfully"}
