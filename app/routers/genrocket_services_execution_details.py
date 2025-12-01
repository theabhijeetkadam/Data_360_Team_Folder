from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.genrocket_services_execution_details import GenRocketServicesExecutionDetailsCreate, GenRocketServicesExecutionDetailsUpdate, GenRocketServicesExecutionDetailsResponse
from app.crud import genrocket_services_execution_details as crud
from app.database import get_db

router = APIRouter(
    prefix="/genrocket_services_execution_details",
    tags=["GenRocket Services Execution Details"]
)

@router.get("/", response_model=list[GenRocketServicesExecutionDetailsResponse])
def read_jobs(db: Session = Depends(get_db)):
    return crud.get_all_jobs(db)

@router.get("/{job_id}", response_model=GenRocketServicesExecutionDetailsResponse)
def read_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job_by_id(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.post("/", response_model=GenRocketServicesExecutionDetailsResponse)
def create_job(job: GenRocketServicesExecutionDetailsCreate, db: Session = Depends(get_db)):
    return crud.create_job(db, job)

@router.put("/{job_id}", response_model=GenRocketServicesExecutionDetailsResponse)
def update_job(job_id: int, job: GenRocketServicesExecutionDetailsUpdate, db: Session = Depends(get_db)):
    updated_job = crud.update_job(db, job_id, job)
    if not updated_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return updated_job

@router.delete("/{job_id}", response_model=GenRocketServicesExecutionDetailsResponse)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    deleted_job = crud.delete_job(db, job_id)
    if not deleted_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return deleted_job