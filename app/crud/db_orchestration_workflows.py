from sqlalchemy.orm import Session
from app import models, schemas
from app.models.db_orchestration_workflows import DBOrchestrationWorkflows


def create_workflow(db: Session, workflow: schemas.WorkflowCreate):
    new_workflow = models.db_orchestration_workflows.DBOrchestrationWorkflows(**workflow.dict())
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    return new_workflow

def get_all_workflows(db: Session):
    return db.query(models.db_orchestration_workflows.DBOrchestrationWorkflows).all()

def get_workflow_by_id(db: Session, workflow_id: int):
    return db.query(models.db_orchestration_workflows.DBOrchestrationWorkflows).filter(
        models.db_orchestration_workflows.DBOrchestrationWorkflows.workflow_id == workflow_id
    ).first()

def update_workflow(db: Session, workflow_id: int, updated_data: schemas.WorkflowUpdate):
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        return None
    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(workflow, key, value)
    db.commit()
    db.refresh(workflow)
    return workflow

def delete_workflow(db: Session, workflow_id: int):
    workflow = get_workflow_by_id(db, workflow_id)
    if not workflow:
        return None
    db.delete(workflow)
    db.commit()
    return workflow
