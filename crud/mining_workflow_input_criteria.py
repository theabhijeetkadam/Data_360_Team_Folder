
# crud/mining_workflow_input_criteria.py
from sqlalchemy.orm import Session
from app.models.mining_workflow_input_criteria import MiningWorkflowInputCriteria
from app.models.mining_fields_type import MiningFieldsType
from app.schemas.mining_workflow_input_criteria import (
    MiningWorkflowInputCriteriaCreate,
    MiningWorkflowInputCriteriaUpdate,
)
from typing import List
# Import your other models
from app.models.project import Project
from app.models.env import Environment
from app.models.mining_workflows_reserve import MiningWorkflowsReserve


# ---- Auto-fetch helper inside CRUD ----
def _autofetch_ids(db: Session, project_name: str, module_name: str, environment_name: str):
    """
    Fetch project_id, module_id, environment_id from their names.
    NOTE: no longer fetches workflow_id (it must come from payload).
    """
    project = db.query(Project).filter_by(project_name=project_name, module_name=module_name).first()
    environment = db.query(Environment).filter_by(env_name=environment_name).first()

    if not project:
        raise ValueError(f"Invalid project/module: {project_name} / {module_name}")
    if not environment:
        raise ValueError(f"Invalid environment: {environment_name}")

    return {
        "project_id": project.project_id,
        "module_id": project.module_id,
        "environment_id": environment.env_id,
    }


def _validate_workflow_id(db: Session, workflow_id: int):
    """
    Ensure workflow_id exists in MiningWorkflowsReserve.
    """
    wf = db.query(MiningWorkflowsReserve).filter_by(workflow_id=workflow_id).first()
    if not wf:
        raise ValueError(f"Invalid workflow_id: {workflow_id}")
    return wf


# ---- CRUD Operations ----
def create_input_criteria(db: Session, data: MiningWorkflowInputCriteriaCreate):
    # ensure type_of_field exists (if your schema includes it)
    if hasattr(data, "type_of_field") and data.type_of_field:
        field = db.query(MiningFieldsType).filter_by(type_of_field=data.type_of_field).first()
        if not field:
            new_field = MiningFieldsType(type_of_field=data.type_of_field)
            db.add(new_field)
            db.commit()
            db.refresh(new_field)

    # validate workflow_id provided in payload
    _validate_workflow_id(db, data.workflow_id)

    # fetch other IDs from names
    ids = _autofetch_ids(db, data.project_name, data.module_name, data.environment_name)

    # construct the new record:
    # - use payload workflow_id
    # - include names as given (workflow_name is kept as a descriptive field)
    payload = data.model_dump()  # Pydantic v2: model_dump()
    new_record = MiningWorkflowInputCriteria(**payload, **ids)

    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


def get_all_input_criteria(db: Session):
    return db.query(MiningWorkflowInputCriteria).all()


def get_input_criteria_by_id(db: Session, input_criteria_id: int):
    return db.query(MiningWorkflowInputCriteria).filter_by(input_criteria_id=input_criteria_id).first()




def get_input_criteria_by_workflow_id_via_python(db: Session, workflow_id: int) -> List[MiningWorkflowInputCriteria]:
    all_rows = get_all_input_criteria(db)
    # Filter in Python
    return [row for row in all_rows if row.workflow_id == workflow_id]




def update_input_criteria(db: Session, input_criteria_id: int, data: MiningWorkflowInputCriteriaUpdate):
    record = get_input_criteria_by_id(db, input_criteria_id)
    if not record:
        return None

    # Collect changes from payload (exclude None to avoid overwriting)
    changes = data.model_dump(exclude_none=True)

    # If user provided names, refresh the corresponding IDs
    # Only fetch when both project_name and module_name are given (as in your helper)
    if "project_name" in changes and "module_name" in changes:
        ids = _autofetch_ids(
            db,
            changes["project_name"],
            changes["module_name"],
            changes.get("environment_name", record.environment_name),
        )
        changes.update(ids)
    elif "environment_name" in changes:
        # environment can change alone
        env = db.query(Environment).filter_by(env_name=changes["environment_name"]).first()
        if not env:
            raise ValueError(f"Invalid environment: {changes['environment_name']}")
        changes["environment_id"] = env.env_id

    # If workflow_id is provided, validate and set it
    if "workflow_id" in changes:
        _validate_workflow_id(db, changes["workflow_id"])

    # Apply all changes to the record
    for key, value in changes.items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record


def delete_input_criteria(db: Session, input_criteria_id: int):
    record = get_input_criteria_by_id(db, input_criteria_id)
    if record:
        db.delete(record)
        db.commit()
        return True
