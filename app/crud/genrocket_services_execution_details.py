
# app/crud/genrocket_services_execution_details.py
from sqlalchemy.orm import Session
from app.models.genrocket_services_execution_details import GenRocketServicesExecutionDetails
from app.schemas.genrocket_services_execution_details import (
    GenRocketServicesExecutionDetailsCreate,
    GenRocketServicesExecutionDetailsUpdate,
)

# OPTIONAL: existence check (as you had)
try:
    from app.models.tdm_tool import TDMToolName
except Exception:
    TDMToolName = None

def _assert_tool_exists(db: Session, tool_id: int) -> None:
    if TDMToolName is None:
        return
    exists = db.query(TDMToolName).filter(TDMToolName.tool_id == tool_id).first()
    if not exists:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"tool_id '{tool_id}' not found in tdm_tool_names")

def get_all_jobs(db: Session):
    return db.query(GenRocketServicesExecutionDetails).all()

def get_job_by_id(db: Session, job_id: int):
    return db.query(GenRocketServicesExecutionDetails).filter(
        GenRocketServicesExecutionDetails.job_id == job_id
    ).first()

def get_jobs_by_workflow_id(db: Session, workflow_id: int):
    """New name for clarity; same behavior."""
    return db.query(GenRocketServicesExecutionDetails).filter(
        GenRocketServicesExecutionDetails.workflow_id == workflow_id
    ).all()

# Keep old name if used elsewhere
def get_workflow_by_id(db: Session, workflow_id: int):
    return get_jobs_by_workflow_id(db, workflow_id)

def create_job(db: Session, job: GenRocketServicesExecutionDetailsCreate):
    payload = job.model_dump()
    _assert_tool_exists(db, payload["tool_id"])

    db_job = GenRocketServicesExecutionDetails(**payload)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: int, job: GenRocketServicesExecutionDetailsUpdate):
    db_job = db.query(GenRocketServicesExecutionDetails).filter(
        GenRocketServicesExecutionDetails.job_id == job_id
    ).first()
    if not db_job:
        return None

    updates = job.model_dump(exclude_unset=True)

    if "tool_id" in updates and updates["tool_id"] is not None:
        _assert_tool_exists(db, updates["tool_id"])

    for key, value in updates.items():
        setattr(db_job, key, value)

    db.commit()
    db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int):
    db_job = db.query(GenRocketServicesExecutionDetails).filter(
        GenRocketServicesExecutionDetails.job_id == job_id
    ).first()
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job
