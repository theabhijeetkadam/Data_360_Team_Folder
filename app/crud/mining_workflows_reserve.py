
# app/crud/mining_workflows_reserve.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, union, func, and_
from fastapi import HTTPException

from app.models.mining_workflows_reserve import MiningWorkflowsReserve
from app.models.project import Project
from app.models.env import Environment
from app.models.mining_workflow_input_criteria import MiningWorkflowInputCriteria
# ✅ Explicit import to avoid ambiguity
from app.models.mining_workflow_output_criteria import MiningWorkflowOutputCriteria

from app.schemas.mining_workflows_reserve import (
    MiningWorkflowsReserveCreate,
    MiningWorkflowsReserveUpdate,
)

def _validate_project(db: Session, project_id: Optional[int], project_name: Optional[str]) -> Optional[Project]:
    """
    Validates project existence with strict matching rules:
    - If both id and name provided: they must point to the same row.
    - If only id provided: id must exist.
    - If only name provided: name must exist.
    Returns the Project row (for hydration) if valid, else raises 404.
    """
    if project_id is not None and project_name is not None:
        row = db.query(Project).filter(Project.project_id == project_id).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Project not found for project_id={project_id}")
        if row.project_name != project_name:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Project name mismatch: project_id={project_id} is '{row.project_name}', not '{project_name}'"
            )
        return row

    if project_id is not None:
        row = db.query(Project).filter(Project.project_id == project_id).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Project not found for project_id={project_id}")
        return row

    if project_name is not None:
        row = db.query(Project).filter(Project.project_name == project_name).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Project not found for project_name='{project_name}'")
        return row

    # Neither provided
    return None


def _validate_environment(db: Session, env_id: Optional[int], environment_name: Optional[str]) -> Optional[Environment]:
    """
    Validates environment existence with strict matching rules (same pattern as project).
    """
    if env_id is not None and environment_name is not None:
        row = db.query(Environment).filter(Environment.env_id == env_id).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Environment not found for env_id={env_id}")
        if row.env_name != environment_name:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Environment name mismatch: env_id={env_id} is '{row.env_name}', not '{environment_name}'"
            )
        return row

    if env_id is not None:
        row = db.query(Environment).filter(Environment.env_id == env_id).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Environment not found for env_id={env_id}")
        return row

    if environment_name is not None:
        row = db.query(Environment).filter(Environment.env_name == environment_name).first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=404, detail=f"Environment not found for environment_name='{environment_name}'")
        return row

    return None


# ---- List / Get ----

def get_all_workflows(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(MiningWorkflowsReserve)
          .offset(skip)
          .limit(limit)
          .all()
    )


def get_workflow_by_id(db: Session, workflow_id: int) -> Optional[MiningWorkflowsReserve]:
    return (
        db.query(MiningWorkflowsReserve)
          .filter(MiningWorkflowsReserve.workflow_id == workflow_id)
          .first()
    )


def get_workflow_with_names_by_id(db: Session, workflow_id: int) -> Optional[MiningWorkflowsReserve]:
    stmt = (
        select(
            MiningWorkflowsReserve,
            Project.project_name,
            Environment.env_name
        )
        .join(Project, Project.project_id == MiningWorkflowsReserve.project_id)       # inner join
        .join(Environment, Environment.env_id == MiningWorkflowsReserve.env_id)       # inner join
        .where(MiningWorkflowsReserve.workflow_id == workflow_id)
    )
    row = db.execute(stmt).first()
    if not row:
        return None
    wf, project_name, env_name = row
    setattr(wf, "project_name", project_name)
    setattr(wf, "environment_name", env_name)
    return wf


# ---- Create / Update ----

def create_workflow(db: Session, workflow: MiningWorkflowsReserveCreate) -> MiningWorkflowsReserve:
    # Validate & resolve project/environment
    proj_row = _validate_project(db, workflow.project_id, workflow.project_name)
    env_row  = _validate_environment(db, workflow.env_id, workflow.env_name)

    # Resolve IDs if only names were provided
    resolved_project_id = workflow.project_id if workflow.project_id is not None else (proj_row.project_id if proj_row else None)
    resolved_env_id     = workflow.env_id if workflow.env_id is not None else (env_row.env_id if env_row else None)

    new_workflow = MiningWorkflowsReserve(
        workflow_name=workflow.workflow_name,
        project_id=resolved_project_id,
        env_id=resolved_env_id,
    )

    # Hydrate denormalized names from DB
    new_workflow.project_name = proj_row.project_name if proj_row else None
    new_workflow.env_name     = env_row.env_name if env_row else None

    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)
    return new_workflow


def update_workflow(db: Session, workflow_id: int, workflow: MiningWorkflowsReserveUpdate) -> Optional[MiningWorkflowsReserve]:
    db_workflow = get_workflow_by_id(db, workflow_id)
    if not db_workflow:
        return None

    # Validate according to what's being changed
    proj_row = _validate_project(
        db,
        workflow.project_id if workflow.project_id is not None else db_workflow.project_id if workflow.project_name is not None else None,
        workflow.project_name
    )
    env_row = _validate_environment(
        db,
        workflow.env_id if workflow.env_id is not None else db_workflow.env_id if workflow.environment_name is not None else None,
        workflow.environment_name
    )

    if workflow.workflow_name is not None:
        db_workflow.workflow_name = workflow.workflow_name

    if workflow.project_id is not None or workflow.project_name is not None:
        db_workflow.project_id = workflow.project_id if workflow.project_id is not None else proj_row.project_id
        db_workflow.project_name = proj_row.project_name if proj_row else None

    if workflow.env_id is not None or workflow.environment_name is not None:
        db_workflow.env_id = workflow.env_id if workflow.env_id is not None else env_row.env_id
        db_workflow.env_name = env_row.env_name if env_row else None

    db.commit()
    db.refresh(db_workflow)
    return db_workflow


def delete_workflow(db: Session, workflow_id: int):
    db_workflow = get_workflow_by_id(db, workflow_id)
    if not db_workflow:
        return None
    db.delete(db_workflow)
    db.commit()
    return {"detail": "Workflow deleted successfully"}


# ---- Source tables / columns helpers ----

def get_all_source_tables_by_workflow(db: Session, workflow_id: int) -> List[str]:
    """
    Returns distinct source tables used in this workflow from:
      - Input criteria (always)
      - Output criteria (ONLY rows flagged via is_parameter_flag = TRUE)
    """
    s_in = (
        select(func.trim(MiningWorkflowInputCriteria.source_table).label("source_table"))
        .where(
            MiningWorkflowInputCriteria.workflow_id == workflow_id,
            MiningWorkflowInputCriteria.source_table.isnot(None),
            func.length(func.trim(MiningWorkflowInputCriteria.source_table)) > 0,
        )
        .distinct()
    )

    # ✅ Only include output criteria that are flagged
    s_out = (
        select(func.trim(MiningWorkflowOutputCriteria.source_table).label("source_table"))
        .where(
            MiningWorkflowOutputCriteria.workflow_id == workflow_id,
            MiningWorkflowOutputCriteria.is_parameter_flag.is_(True),
            MiningWorkflowOutputCriteria.source_table.isnot(None),
            func.length(func.trim(MiningWorkflowOutputCriteria.source_table)) > 0,
        )
        .distinct()
    )

    union_stmt = union(s_in, s_out)
    raw_rows: List[str] = db.execute(union_stmt).scalars().all()

    # Case-insensitive unique-ify, but preserve original casing of first occurrence
    seen_ci = {}
    for val in raw_rows:
        key = val.lower()
        if key not in seen_ci:
            seen_ci[key] = val
    return list(seen_ci.values())


# ✅ NEW: Return flagged output columns for a workflow
def get_flagged_output_columns_by_workflow(db: Session, workflow_id: int) -> List[str]:
    """
    Returns distinct source_column values from output criteria flagged as parameters.
    """
    q = (
        select(func.trim(MiningWorkflowOutputCriteria.source_column).label("source_column"))
        .where(
            MiningWorkflowOutputCriteria.workflow_id == workflow_id,
            MiningWorkflowOutputCriteria.is_parameter_flag.is_(True),
            MiningWorkflowOutputCriteria.source_column.isnot(None),
            func.length(func.trim(MiningWorkflowOutputCriteria.source_column)) > 0,
        )
        .distinct()
    )
    rows = db.execute(q).scalars().all()

    # Case-insensitive unique-ify
    seen_ci = {}
    for val in rows:
        key = val.lower()
        if key not in seen_ci:
            seen_ci[key] = val
    return list(seen_ci.values())


# ✅ NEW: Return full flagged rows for a workflow
def get_flagged_output_criteria_by_workflow(db: Session, workflow_id: int) -> List[MiningWorkflowOutputCriteria]:
    return (
        db.query(MiningWorkflowOutputCriteria)
        .filter(
            MiningWorkflowOutputCriteria.workflow_id == workflow_id,
            MiningWorkflowOutputCriteria.is_parameter_flag.is_(True),
        )
        .all()
    )
