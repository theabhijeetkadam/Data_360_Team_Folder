
# app/routers/mining_workflows_reserve.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.responses import JSONResponse

from app.database import SessionLocal
from app.crud import mining_workflows_reserve
from app.schemas.mining_workflows_reserve import (
    MiningWorkflowsReserveCreate,
    MiningWorkflowsReserveUpdate,
    MiningWorkflowsReserveResponse
)
from app.models.project import Project
from app.models.env import Environment
import re

router = APIRouter(
    prefix="/mining_workflows_reserve",
    tags=["Mining Workflows Reserve"]
)

# Allowed characters for workflow_name (same pattern you used early on)
NAME_PATTERN = re.compile(r'^[A-Za-z0-9 _-]+$')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

# ---------- Helpers (router-level strict validation) ----------

def _get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.project_id == project_id).first()

def _get_project_by_name(db: Session, project_name: str):
    return db.query(Project).filter(Project.project_name == project_name).first()

def _get_env_by_id(db: Session, env_id: int):
    return db.query(Environment).filter(Environment.env_id == env_id).first()

def _get_env_by_name(db: Session, env_name: str):
    return db.query(Environment).filter(Environment.env_name == env_name).first()


# ---------- READ: ALL ----------
@router.get("/", response_model=List[MiningWorkflowsReserveResponse])
def read_all_workflows(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns workflows (includes denormalized project/environment names if present).
    """
    items = mining_workflows_reserve.get_all_workflows(db, skip, limit)
    return items

# ---------- READ: ONE (joins to Project/Environment to populate names) ----------
@router.get("/{workflow_id}", response_model=MiningWorkflowsReserveResponse)
def read_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """
    Returns a single workflow enriched with project_name and environment_name via joins.
    If either the workflow doesn't exist OR its related project/environment is missing, return 404.
    """
    workflow = mining_workflows_reserve.get_workflow_with_names_by_id(db, workflow_id)
    if not workflow:
        return JSONResponse(
            status_code=404,
            content=error_response(404, "Workflow or related project/environment not found")
        )
    return workflow

# ---------- CREATE ----------
@router.post("/", response_model=MiningWorkflowsReserveResponse, status_code=201)
def create_workflow(workflow: MiningWorkflowsReserveCreate, db: Session = Depends(get_db)):
    """
    Creates a workflow.
    Strict rules:
      - If project_id & project_name are both sent, they must match the same row in project_table; else 404.
      - If only project_id is sent, it must exist; else 404.
      - If only project_name is sent, it must exist; else 404 (ID will be resolved from DB).
      - Same rules apply for env_id/environment_name against env_details.
    Denormalized names are NOT overridden by client input; they are hydrated from DB.
    """
    # Basic validations
    if not workflow.workflow_name or not NAME_PATTERN.match(workflow.workflow_name):
        raise HTTPException(
            status_code=400,
            detail="workflow_name contains invalid characters. Allowed: letters, numbers, spaces, underscores, hyphens."
        )
    if workflow.project_id is not None and workflow.project_id <= 0:
        raise HTTPException(status_code=400, detail="project_id must be a positive integer")
    if workflow.env_id is not None and workflow.env_id <= 0:
        raise HTTPException(status_code=400, detail="env_id must be a positive integer")

    # --- Strict project validation ---
    # proj_row = None
    # if workflow.project_id is not None and workflow.project_name is not None:
    #     proj_row = _get_project_by_id(db, workflow.project_id)
    #     if not proj_row:
    #         raise HTTPException(status_code=404, detail=f"Project not found for project_id={workflow.project_id}")
    #     if proj_row.project_name != workflow.project_name:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"Project name mismatch: project_id={workflow.project_id} is '{proj_row.project_name}', not '{workflow.project_name}'"
    #         )
    # elif workflow.project_id is not None:
    #     proj_row = _get_project_by_id(db, workflow.project_id)
    #     if not proj_row:
    #         raise HTTPException(status_code=404, detail=f"Project not found for project_id={workflow.project_id}")
    # elif workflow.project_name is not None:
    #     proj_row = _get_project_by_name(db, workflow.project_name)
    #     if not proj_row:
    #         raise HTTPException(status_code=404, detail=f"Project not found for project_name='{workflow.project_name}'")

    # resolved_project_id = workflow.project_id if workflow.project_id is not None else (proj_row.project_id if proj_row else None)

    # # --- Strict environment validation ---
    # env_row = None
    # if workflow.env_id is not None and workflow.environment_name is not None:
    #     env_row = _get_env_by_id(db, workflow.env_id)
    #     if not env_row:
    #         raise HTTPException(status_code=404, detail=f"Environment not found for env_id={workflow.env_id}")
    #     if env_row.env_name != workflow.environment_name:
    #         raise HTTPException(
    #             status_code=404,
    #             detail=f"Environment name mismatch: env_id={workflow.env_id} is '{env_row.env_name}', not '{workflow.environment_name}'"
    #         )
    # elif workflow.env_id is not None:
    #     env_row = _get_env_by_id(db, workflow.env_id)
    #     if not env_row:
    #         raise HTTPException(status_code=404, detail=f"Environment not found for env_id={workflow.env_id}")
    # elif workflow.environment_name is not None:
    #     env_row = _get_env_by_name(db, workflow.environment_name)
    #     if not env_row:
    #         raise HTTPException(status_code=404, detail=f"Environment not found for environment_name='{workflow.environment_name}'")

    # resolved_env_id = workflow.env_id if workflow.env_id is not None else (env_row.env_id if env_row else None)

    # Sanitize payload to prevent client-side name overrides; let CRUD hydrate names from DB.
    payload = workflow.dict()
    #payload["project_id"] = resolved_project_id
    #payload["env_id"] = resolved_env_id
    #payload["project_name"] = None
    #payload["environment_name"] = None
    print('payload 1', payload)
    workflow_clean = MiningWorkflowsReserveCreate(**payload)
    print('payload 2',workflow_clean)
    # Delegate to CRUD; it will persist and hydrate names from DB
    try:
        created = mining_workflows_reserve.create_workflow(db, workflow_clean)
        print('response', created)
    except HTTPException as exc:
        # Propagate 404 or other errors cleanly
        raise exc
    except Exception:
        return JSONResponse(status_code=500, content=error_response(500, "Create failed"))

    return created

# ---------- UPDATE ----------
@router.put("/{workflow_id}", response_model=MiningWorkflowsReserveResponse)
def update_workflow(workflow_id: int, workflow: MiningWorkflowsReserveUpdate, db: Session = Depends(get_db)):
    """
    Updates a workflow.
    Strict rules identical to create:
      - project_id & project_name must match the same row if both sent; else 404.
      - project_id alone must exist; else 404.
      - project_name alone must exist (ID resolved from DB); else 404.
      - Similarly for environment.
    Denormalized names are NOT overridden by client input; they are hydrated from DB.
    """
    # Optional validations
    if workflow.workflow_name is not None and not NAME_PATTERN.match(workflow.workflow_name):
        raise HTTPException(
            status_code=400,
            detail="workflow_name contains invalid characters. Allowed: letters, numbers, spaces, underscores, hyphens."
        )
    if workflow.project_id is not None and workflow.project_id <= 0:
        raise HTTPException(status_code=400, detail="project_id must be a positive integer")
    if workflow.env_id is not None and workflow.env_id <= 0:
        raise HTTPException(status_code=400, detail="env_id must be a positive integer")

    # Ensure target workflow exists first
    existing = mining_workflows_reserve.get_workflow_by_id(db, workflow_id)
    if not existing:
        return JSONResponse(status_code=404, content=error_response(404, f"Workflow not found for workflow_id={workflow_id}"))

    # --- Strict project validation & resolution for update ---
    proj_row = None
    target_project_id = existing.project_id  # default to current

    if workflow.project_id is not None and workflow.project_name is not None:
        proj_row = _get_project_by_id(db, workflow.project_id)
        if not proj_row:
            raise HTTPException(status_code=404, detail=f"Project not found for project_id={workflow.project_id}")
        if proj_row.project_name != workflow.project_name:
            raise HTTPException(
                status_code=404,
                detail=f"Project name mismatch: project_id={workflow.project_id} is '{proj_row.project_name}', not '{workflow.project_name}'"
            )
        target_project_id = workflow.project_id
    elif workflow.project_id is not None:
        proj_row = _get_project_by_id(db, workflow.project_id)
        if not proj_row:
            raise HTTPException(status_code=404, detail=f"Project not found for project_id={workflow.project_id}")
        target_project_id = workflow.project_id
    elif workflow.project_name is not None:
        proj_row = _get_project_by_name(db, workflow.project_name)
        if not proj_row:
            raise HTTPException(status_code=404, detail=f"Project not found for project_name='{workflow.project_name}'")
        target_project_id = proj_row.project_id

    # --- Strict environment validation & resolution for update ---
    env_row = None
    target_env_id = existing.env_id  # default to current

    if workflow.env_id is not None and workflow.environment_name is not None:
        env_row = _get_env_by_id(db, workflow.env_id)
        if not env_row:
            raise HTTPException(status_code=404, detail=f"Environment not found for env_id={workflow.env_id}")
        if env_row.env_name != workflow.environment_name:
            raise HTTPException(
                status_code=404,
                detail=f"Environment name mismatch: env_id={workflow.env_id} is '{env_row.env_name}', not '{workflow.environment_name}'"
            )
        target_env_id = workflow.env_id
    elif workflow.env_id is not None:
        env_row = _get_env_by_id(db, workflow.env_id)
        if not env_row:
            raise HTTPException(status_code=404, detail=f"Environment not found for env_id={workflow.env_id}")
        target_env_id = workflow.env_id
    elif workflow.environment_name is not None:
        env_row = _get_env_by_name(db, workflow.environment_name)
        if not env_row:
            raise HTTPException(status_code=404, detail=f"Environment not found for environment_name='{workflow.environment_name}'")
        target_env_id = env_row.env_id

    # Sanitize update payload: prevent client-side overrides of names
    payload = workflow.dict(exclude_unset=True)
    payload["project_id"] = target_project_id
    payload["env_id"] = target_env_id
    payload["project_name"] = None
    payload["environment_name"] = None
    workflow_update_clean = MiningWorkflowsReserveUpdate(**payload)

    # Delegate to CRUD
    try:
        updated = mining_workflows_reserve.update_workflow(db, workflow_id, workflow_update_clean)
    except HTTPException as exc:
        # Propagate 404 for missing project/env or mismatch
        raise exc
    except Exception:
        return JSONResponse(status_code=500, content=error_response(500, "Update failed"))

    if not updated:
        return JSONResponse(status_code=404, content=error_response(404, f"Workflow not found for workflow_id={workflow_id}"))
    return updated

# ---------- DELETE ----------
@router.delete("/{workflow_id}")
def delete_workflow(workflow_id: int, db: Session = Depends(get_db)):
    """
    Deletes a workflow.
    """
    result = mining_workflows_reserve.delete_workflow(db, workflow_id)
    if not result:
        return JSONResponse(status_code=404, content=error_response(404, "Workflow not found"))
    return result

# ---------- AUX: SOURCE TABLES ----------
@router.get("/{workflow_id}/source-tables", response_model=List[str])
def list_source_tables(workflow_id: int, db: Session = Depends(get_db)):
    """
    Returns a combined, de-duplicated list of source_table names taken from
    input_criteria and output_criteria for the given workflow_id.
    """
    tables = mining_workflows_reserve.get_all_source_tables_by_workflow(db, workflow_id)
    return tables  # empty list if none
