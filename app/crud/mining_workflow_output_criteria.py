
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional

from app.models.mining_workflow_output_criteria import MiningWorkflowOutputCriteria
from app.models.project import Project
from app.models.env import Environment
from app.models.mining_workflows_reserve import MiningWorkflowsReserve
from app.schemas.mining_workflow_output_criteria import (
    MiningWorkflowOutputCriteriaCreate,
    MiningWorkflowOutputCriteriaUpdate,
)

# Autofetch foreign keys (except workflow_id)
def _autofetch_ids(db: Session, project_name, module_name, environment_name):
    project = (
        db.query(Project)
        .filter_by(project_name=project_name, module_name=module_name)
        .first()
    )
    env = db.query(Environment).filter_by(env_name=environment_name).first()

    if not project:
        raise ValueError(f"Invalid project/module: {project_name}/{module_name}")
    if not env:
        raise ValueError(f"Invalid environment: {environment_name}")

    return {
        "project_id": project.project_id,
        "module_id": project.module_id,
        "environment_id": env.env_id,
    }

def _validate_workflow_id(db: Session, workflow_id: int):
    wf = db.query(MiningWorkflowsReserve).filter_by(workflow_id=workflow_id).first()
    if not wf:
        raise ValueError(f"Invalid workflow_id: {workflow_id}")
    return wf

# CRUD Operations
def create_output_criteria(db: Session, data: MiningWorkflowOutputCriteriaCreate):
    _validate_workflow_id(db, data.workflow_id)
    ids = _autofetch_ids(db, data.project_name, data.module_name, data.environment_name)

    record_data = data.dict(exclude_unset=True)
    new_record = MiningWorkflowOutputCriteria(**record_data, **ids)
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def get_all_output_criteria(db: Session):
    return db.query(MiningWorkflowOutputCriteria).all()

def get_output_criteria_by_id(db: Session, output_criteria_id: int):
    return (
        db.query(MiningWorkflowOutputCriteria)
        .filter_by(output_criteria_id=output_criteria_id)
        .first()
    )

def get_output_criteria_by_workflow_id(db: Session, workflow_id: int):
    return (
        db.query(MiningWorkflowOutputCriteria)
        .filter_by(workflow_id=workflow_id)
        .all()
    )

def update_output_criteria(db: Session, output_criteria_id: int, data: MiningWorkflowOutputCriteriaUpdate):
    record = get_output_criteria_by_id(db, output_criteria_id)
    if not record:
        return None

    # If payload contains workflow_id, validate
    if data.workflow_id is not None:
        _validate_workflow_id(db, data.workflow_id)

    # If names are provided, refresh IDs
    changes = data.dict(exclude_unset=True)
    if {"project_name", "module_name", "environment_name"} <= changes.keys():
        ids = _autofetch_ids(db, changes["project_name"], changes["module_name"], changes["environment_name"])
        changes.update(ids)

    for key, value in changes.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

def delete_output_criteria(db: Session, output_criteria_id: int):
    record = get_output_criteria_by_id(db, output_criteria_id)
    if record:
        db.delete(record)
        db.commit()
        return True
    return False

# ✅ NEW: toggle flag for a single row
def set_parameter_flag(db: Session, output_criteria_id: int, flag: bool) -> Optional[MiningWorkflowOutputCriteria]:
    record = get_output_criteria_by_id(db, output_criteria_id)
    if not record:
        return None
    record.is_parameter_flag = bool(flag)
    db.commit()
    db.refresh(record)
    return record

# ✅ NEW: bulk toggle flags for a workflow
def set_parameter_flags_bulk(
    db: Session,
    workflow_id: int,
    source_columns: List[str],
    flag: bool
) -> int:
    """
    Set/unset is_parameter_flag for all rows matching workflow_id and source_column IN source_columns.
    Returns the number of rows updated.
    """
    if not source_columns:
        return 0

    q = (
        db.query(MiningWorkflowOutputCriteria)
        .filter(
            and_(
                MiningWorkflowOutputCriteria.workflow_id == workflow_id,
                MiningWorkflowOutputCriteria.source_column.in_(source_columns),
            )
        )
    )
    rows = q.all()
    for r in rows:
        r.is_parameter_flag = bool(flag)
    db.commit()
    return len(rows)
