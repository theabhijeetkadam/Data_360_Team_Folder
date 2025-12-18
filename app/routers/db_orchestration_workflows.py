from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import db_orchestration_workflows as schemas
from app.crud import db_orchestration_workflows as crud
from app.schemas.db_orchestration_workflows import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from app.crud.db_orchestration_workflows import create_workflow, get_all_workflows, get_workflow_by_id, update_workflow, delete_workflow


router = APIRouter(
    prefix="/db_orchestration_workflows",
    tags=["DB Orchestration Workflows"]
)

@router.post("/", response_model=schemas.WorkflowResponse)
def create_workflow(workflow: schemas.WorkflowCreate, db: Session = Depends(get_db)):
    return crud.create_workflow(db, workflow)

@router.get("/", response_model=list[schemas.WorkflowResponse])
def get_all_workflows(db: Session = Depends(get_db)):
    return crud.get_all_workflows(db)

@router.get("/{workflow_id}", response_model=schemas.WorkflowResponse)
def get_workflow_by_id(workflow_id: int, db: Session = Depends(get_db)):
    workflow = crud.get_workflow_by_id(db, workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow

@router.put("/{workflow_id}", response_model=schemas.WorkflowResponse)
def update_workflow(workflow_id: int, workflow: schemas.WorkflowUpdate, db: Session = Depends(get_db)):
    updated = crud.update_workflow(db, workflow_id, workflow)
    if not updated:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return updated

@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_workflow(db, workflow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"message": "Workflow deleted successfully"}
