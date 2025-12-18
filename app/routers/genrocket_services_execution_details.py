
# app/routers/genrocket_services_execution_details.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.genrocket_services_execution_details import (
    GenRocketServicesExecutionDetailsCreate,
    GenRocketServicesExecutionDetailsUpdate,
    GenRocketServicesExecutionDetailsResponse,
)
from app.crud import genrocket_services_execution_details as crud
from app.database import get_db

router = APIRouter(
    prefix="/genrocket_services_execution_details",
    tags=["GenRocket Services Execution Details"]
)

# Get all jobs
@router.get(
    "/",
    response_model=list[GenRocketServicesExecutionDetailsResponse],
    operation_id="exec_details_list_all"
)
def read_jobs(db: Session = Depends(get_db)):
    return crud.get_all_jobs(db)

# ✅ Get ONE job by job_id (disambiguated path)
@router.get(
    "/jobs/{job_id}",
    response_model=GenRocketServicesExecutionDetailsResponse,
    operation_id="exec_details_get_job_by_id"
)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job_by_id(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

# ✅ Get list of jobs by workflow_id (disambiguated path)
@router.get(
    "/workflows/{workflow_id}",
    response_model=list[GenRocketServicesExecutionDetailsResponse],
    operation_id="exec_details_get_jobs_by_workflow_id"
)
def read_workflow_jobs(workflow_id: int, db: Session = Depends(get_db)):
    jobs = crud.get_jobs_by_workflow_id(db, workflow_id)
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found for workflow_id")
    return jobs

# Create
@router.post(
    "/",
    response_model=GenRocketServicesExecutionDetailsResponse,
    operation_id="exec_details_create_job"
)
def create_job(job: GenRocketServicesExecutionDetailsCreate, db: Session = Depends(get_db)):
    return crud.create_job(db, job)

# Update by job_id
@router.put(
    "/jobs/{job_id}",
    response_model=GenRocketServicesExecutionDetailsResponse,
    operation_id="exec_details_update_job_by_id"
)
def update_job(job_id: int, job: GenRocketServicesExecutionDetailsUpdate, db: Session = Depends(get_db)):
    updated_job = crud.update_job(db, job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

# Delete by job_id
@router.delete(
    "/jobs/{job_id}",
    response_model=GenRocketServicesExecutionDetailsResponse,
    operation_id="exec_details_delete_job_by_id"
)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    deleted_job = crud.delete_job(db, job_id)
    if not deleted_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return deleted_job
