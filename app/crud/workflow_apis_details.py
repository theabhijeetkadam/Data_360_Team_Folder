from sqlalchemy.orm import Session
from app.models.workflow_apis_details import WorkflowAPIDetail
from app.schemas.workflow_apis_details import WorkflowAPIDetailsCreate, WorkflowAPIDetailsUpdate

def get_workflow_api(db: Session, api_id: int):
    return db.query(WorkflowAPIDetail).filter(WorkflowAPIDetail.api_id == api_id).first()

def get_workflow_apis(db: Session, skip: int = 0, limit: int = 100):
    return db.query(WorkflowAPIDetail).offset(skip).limit(limit).all()

def create_workflow_api(db: Session, api: WorkflowAPIDetailsCreate):
    db_api = WorkflowAPIDetail(**api.dict())
    db.add(db_api)
    db.commit()
    db.refresh(db_api)
    return db_api

def update_workflow_api(db: Session, api_id: int, api: WorkflowAPIDetailsUpdate):
    db_api = db.query(WorkflowAPIDetail).filter(WorkflowAPIDetail.api_id == api_id).first()
    if not db_api:
        return None
    for key, value in api.dict(exclude_unset=True).items():
        setattr(db_api, key, value)
    db.commit()
    db.refresh(db_api)
    return db_api

def delete_workflow_api(db: Session, api_id: int):
    db_api = db.query(WorkflowAPIDetail).filter(WorkflowAPIDetail.api_id == api_id).first()
    if not db_api:
        return None
    db.delete(db_api)
    db.commit()
    return db_api
