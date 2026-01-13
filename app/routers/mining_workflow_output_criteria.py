
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.responses import JSONResponse

from app.database import SessionLocal
from app.crud import mining_workflow_output_criteria as crud
from app.schemas.mining_workflow_output_criteria import (
    MiningWorkflowOutputCriteriaCreate,
    MiningWorkflowOutputCriteriaUpdate,
    MiningWorkflowOutputCriteriaOut
)
from app.models.mining_workflow_output_criteria import MiningWorkflowOutputCriteria

router = APIRouter(prefix="/output-criteria", tags=["Mining Workflow Output Criteria"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.post("/", response_model=MiningWorkflowOutputCriteriaOut)
def create_output_criteria(data: MiningWorkflowOutputCriteriaCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_output_criteria(db, data)
    except ValueError as e:
        return JSONResponse(status_code=400, content=error_response(400, str(e)))

# ✅ rename to avoid conflict with below get_by_id
@router.get("/workflow/{workflow_id}", response_model=list[MiningWorkflowOutputCriteriaOut])
def list_by_workflow(workflow_id: int, db: Session = Depends(get_db)):
    records = crud.get_output_criteria_by_workflow_id(db, workflow_id)
    if not records:
        return JSONResponse(status_code=404, content=error_response(404, "Input criteria not found"))
    return records

@router.get("/", response_model=list[MiningWorkflowOutputCriteriaOut])
def get_all(db: Session = Depends(get_db)):
    return crud.get_all_output_criteria(db)

@router.get("/count")
def count_by_workflow(
    workflow_id: int = Query(..., description="Workflow ID to count output fields for"),
    db: Session = Depends(get_db),
):
    count = (
        db.query(func.count())
        .select_from(MiningWorkflowOutputCriteria)
        .filter(MiningWorkflowOutputCriteria.workflow_id == workflow_id)
        .scalar()
    )
    return {"workflow_id": workflow_id, "count": count, "max_allowed": 15}

@router.get("/{output_criteria_id}", response_model=MiningWorkflowOutputCriteriaOut)
def get_by_id(output_criteria_id: int, db: Session = Depends(get_db)):
    record = crud.get_output_criteria_by_id(db, output_criteria_id)
    if not record:
        return JSONResponse(status_code=404, content=error_response(404, "Output criteria not found"))
    return record

@router.put("/{output_criteria_id}", response_model=MiningWorkflowOutputCriteriaOut)
def update(output_criteria_id: int, data: MiningWorkflowOutputCriteriaUpdate, db: Session = Depends(get_db)):
    try:
        updated = crud.update_output_criteria(db, output_criteria_id, data)
        if not updated:
            return JSONResponse(status_code=404, content=error_response(404, "Output criteria not found"))
        return updated
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

@router.delete("/{output_criteria_id}")
def delete(output_criteria_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_output_criteria(db, output_criteria_id)
    if not deleted:
        return JSONResponse(status_code=404, content=error_response(404, "Output criteria not found"))
    return {"message": "Deleted successfully"}

# ✅ NEW: single-flag toggle endpoint
@router.post("/{output_criteria_id}/flag")
def set_flag(
    output_criteria_id: int,
    flag: bool = Query(..., description="true to mark as parameter; false to unmark"),
    db: Session = Depends(get_db),
):
    record = crud.set_parameter_flag(db, output_criteria_id, flag)
    if not record:
        return JSONResponse(status_code=404, content=error_response(404, "Output criteria not found"))
    return {"message": "Flag updated", "output_criteria_id": output_criteria_id, "is_parameter_flag": record.is_parameter_flag}

# ✅ NEW: bulk-flag toggle for workflow + source_columns
@router.post("/workflow/{workflow_id}/flags")
def set_flags_bulk(
    workflow_id: int,
    payload: dict = Body(..., example={"source_columns": ["customer_id", "reward_id"], "flag": True}),
    db: Session = Depends(get_db),
):
    source_columns = payload.get("source_columns") or []
    flag = bool(payload.get("flag", True))
    updated_count = crud.set_parameter_flags_bulk(db, workflow_id, source_columns, flag)
    return {"message": "Flags updated", "workflow_id": workflow_id, "updated": updated_count, "flag": flag}
