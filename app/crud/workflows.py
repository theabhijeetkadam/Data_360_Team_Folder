from sqlalchemy.orm import Session
from app.models.workflows import Workflows
from app.schemas.workflows import WorkflowCreate, WorkflowUpdate

def create_workflow(db: Session, workflow: WorkflowCreate):
    db_workflow = Workflows(**workflow.dict())
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def get_workflows(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Workflows).offset(skip).limit(limit).all()

def get_workflow_by_id(db: Session, workflow_id: int):
    return db.query(Workflows).filter(Workflows.workflow_id == workflow_id).first()

def update_workflow(db: Session, workflow_id: int, workflow: WorkflowUpdate):
    db_workflow = get_workflow_by_id(db, workflow_id)
    if not db_workflow:
        return None
    for key, value in workflow.dict(exclude_unset=True).items():
        setattr(db_workflow, key, value)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def delete_workflow(db: Session, workflow_id: int):
    db_workflow = get_workflow_by_id(db, workflow_id)
    if not db_workflow:
        return None
    db.delete(db_workflow)
    db.commit()
    return db_workflow
