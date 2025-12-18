from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas import fnr_workflow_execution_log as schemas
from app.crud import fnr_workflow_execution_log as crud
from app.database import SessionLocal

router = APIRouter(prefix="/workflow-execution-log", tags=["Workflow Execution Log"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.post("/", response_model=schemas.WorkflowExecutionLogCreate)
def create_log(log: schemas.WorkflowExecutionLogCreate, db: Session = Depends(get_db)):
    return crud.create_workflow_execution_log(db=db, log=log)
