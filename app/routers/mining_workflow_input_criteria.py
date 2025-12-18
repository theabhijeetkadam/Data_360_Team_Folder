
# routers/mining_workflow_input_criteria.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from app.database import SessionLocal
from fastapi.responses import JSONResponse
from app.schemas.mining_workflow_input_criteria import (
    MiningWorkflowInputCriteriaCreate,
    MiningWorkflowInputCriteriaUpdate,
    MiningWorkflowInputCriteriaOut,
)
from app.crud import mining_workflow_input_criteria as crud

router = APIRouter(prefix="/input-criteria", tags=["Mining Workflow Input Criteria"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.post("/", response_model=MiningWorkflowInputCriteriaOut)
def create_input_criteria(data: MiningWorkflowInputCriteriaCreate, db: Session = Depends(get_db)):
    """
    Requires workflow_id in payload (validated by CRUD).
    """
    try:
        record = crud.create_input_criteria(db, data)
        # If you want 201 Created instead of 200 OK:
        # return JSONResponse(status_code=201, content=record.model_dump())
        return record
    except ValueError as e:
        # e.g., invalid workflow_id or invalid project/environment names
        return JSONResponse(status_code=400, content=error_response(400, str(e)))

@router.get("/{workflow_id}", response_model=List[MiningWorkflowInputCriteriaOut])
def get_by_workflow_id(workflow_id: int, db: Session = Depends(get_db)):
    return crud.get_input_criteria_by_workflow_id_via_python(db, workflow_id)

@router.get("/", response_model=list[MiningWorkflowInputCriteriaOut])
def get_all(db: Session = Depends(get_db)):
    return crud.get_all_input_criteria(db)


@router.get("/{input_criteria_id}", response_model=MiningWorkflowInputCriteriaOut)
def get_by_id(input_criteria_id: int, db: Session = Depends(get_db)):
    record = crud.get_input_criteria_by_id(db, input_criteria_id)
    if not record:
        return JSONResponse(status_code=404, content=error_response(404, "Input criteria not found"))
    return record

@router.put("/{input_criteria_id}", response_model=MiningWorkflowInputCriteriaOut)
def update(input_criteria_id: int, data: MiningWorkflowInputCriteriaUpdate, db: Session = Depends(get_db)):
    """
    Allows optional workflow_id in payload (validated by CRUD).
    """
    try:
        updated = crud.update_input_criteria(db, input_criteria_id, data)
        if not updated:
            return JSONResponse(status_code=404, content=error_response(404, "Input criteria not found"))
        return updated
    except ValueError as e:
        # e.g., invalid workflow_id or invalid environment/project name
        return JSONResponse(status_code=400, content=error_response(400, str(e)))


@router.delete("/{input_criteria_id}")
def delete(input_criteria_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_input_criteria(db, input_criteria_id)
    if not deleted:
        return JSONResponse(status_code=404, content=error_response(404, "Input criteria not found"))
    return {"message": "Deleted successfully"}
