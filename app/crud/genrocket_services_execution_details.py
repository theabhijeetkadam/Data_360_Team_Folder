from sqlalchemy.orm import Session
from app.models.genrocket_services_execution_details import GenRocketServicesExecutionDetails
from app.schemas.genrocket_services_execution_details import GenRocketServicesExecutionDetailsCreate, GenRocketServicesExecutionDetailsUpdate

def get_all_jobs(db: Session):
    return db.query(GenRocketServicesExecutionDetails).all()

def get_job_by_id(db: Session, job_id: int):
    return db.query(GenRocketServicesExecutionDetails).filter(GenRocketServicesExecutionDetails.job_id == job_id).first()

def create_job(db: Session, job: GenRocketServicesExecutionDetailsCreate):
    db_job = GenRocketServicesExecutionDetails(**job.model_dump())
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: int, job: GenRocketServicesExecutionDetailsUpdate):
    db_job = db.query(GenRocketServicesExecutionDetails).filter(GenRocketServicesExecutionDetails.job_id == job_id).first()
    if db_job:
        for key, value in job.model_dump(exclude_unset=True).items():
            setattr(db_job, key, value)
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int):
    db_job = db.query(GenRocketServicesExecutionDetails).filter(GenRocketServicesExecutionDetails.job_id == job_id).first()
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job