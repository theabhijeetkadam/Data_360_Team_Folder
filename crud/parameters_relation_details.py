from sqlalchemy.orm import Session
from app.models.parameters_relation_details import ParametersRelationDetails
from app.models.project import Project
from app.models.env import Environment
from app.models.mining_workflows_reserve import MiningWorkflowsReserve
from app.schemas.parameters_relation_details import ParametersRelationDetailsCreate, ParametersRelationDetailsUpdate

# Autofetch foreign keys
def _autofetch_ids(db: Session, project_name, module_name, environment_name, workflow_name):
    project = db.query(Project).filter_by(project_name=project_name, module_name=module_name).first()
    env = db.query(Environment).filter_by(env_name=environment_name).first()
    workflow = db.query(MiningWorkflowsReserve).filter_by(workflow_name=workflow_name).first()

    if not project:
        raise ValueError(f"Invalid project/module: {project_name}/{module_name}")
    if not env:
        raise ValueError(f"Invalid environment: {environment_name}")
    if not workflow:
        raise ValueError(f"Invalid workflow: {workflow_name}")

    return {
        "project_id": project.project_id,
        "module_id": project.module_id,
        "environment_id": env.env_id,
        "workflow_id": workflow.workflow_id,
    }

# CRUD Operations
def create_relation(db: Session, data: ParametersRelationDetailsCreate):
    ids = _autofetch_ids(db, data.project_name, data.module_name, data.environment_name, data.workflow_name)
    record_data = data.dict(exclude_unset=True)
    new_record = ParametersRelationDetails(**record_data, **ids)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def get_all_relations(db: Session):
    return db.query(ParametersRelationDetails).all()

def get_relation_by_id(db: Session, relation_id: int):
    return db.query(ParametersRelationDetails).filter_by(relation_id=relation_id).first()


def get_relation_by_workflow_id(db: Session, workflow_id: int, *, offset: int = 0, limit: int = 100):
    return (
        db.query(ParametersRelationDetails)
          .filter(ParametersRelationDetails.workflow_id == workflow_id)
          .offset(offset).limit(limit)
          .all()
    )


def update_relation(db: Session, relation_id: int, data: ParametersRelationDetailsUpdate):
    record = get_relation_by_id(db, relation_id)
    if not record:
        return None
    ids = _autofetch_ids(db, data.project_name, data.module_name, data.environment_name, data.workflow_name)
    for key, value in {**data.dict(exclude_unset=True), **ids}.items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record

def delete_relation(db: Session, relation_id: int):
    record = get_relation_by_id(db, relation_id)
    if record:
        db.delete(record)
        db.commit()
        return True
    return False
