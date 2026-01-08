
# app/crud/genrocket_services_details.py
from typing import Union
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func

from app.models.genrocket_services_details import GenRocketServicesDetails
from app.schemas.genrocket_services_details import (
    GenRocketServicesDetailsCreate,
    GenRocketServicesDetailsUpdate,
)
from app.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    DBInsertError,
    DBUpdateError,
    DBDeleteError,
    DBReadError,
)
from app.models import tdm_tool  # expects tdm_tool.TdmToolName model
from app.models.project import Project

class BadRequestError(Exception):
    def __init__(self, message: str, code: str = "400"):
        super().__init__(message)
        self.message = message
        self.code = code

def _normalize_tool_id(raw_tool_id: Union[str, int]) -> int:
    """
    Accepts str/int tool_id from payload and returns normalized INT.
    Raises BadRequestError if non-numeric or missing.
    """
    if raw_tool_id is None:
        raise BadRequestError(message="tool_id is required", code="400")
    if isinstance(raw_tool_id, int):
        return raw_tool_id
    s = str(raw_tool_id).strip()
    if not s.isdigit():
        raise BadRequestError(message=f"Invalid tool_id '{raw_tool_id}': must be numeric", code="400")
    return int(s)

def _assert_tool_exists(db: Session, tool_id_int: int) -> None:
    """
    Raises NotFoundError if tool_id is not present in tdm_tool_names.
    """
    exists = (
        db.query(tdm_tool.TdmToolName)
        .filter(tdm_tool.TdmToolName.tool_id == tool_id_int)
        .first()
    )
    if not exists:
        raise NotFoundError(
            message=f"tool_id '{tool_id_int}' not found in tdm_tool_names",
            code="404",
        )

def _resolve_project(db: Session, project_id: int | None, project_name: str | None) -> Project:
    """
    Resolve the canonical project row from project_table.
    Priority: project_id -> project_name (case-insensitive).
    Raises NotFoundError if no match.
    """
    if project_id is not None:
        p = db.query(Project).filter(Project.project_id == project_id).first()
        if not p:
            raise NotFoundError(message=f"Project with id '{project_id}' not found", code="404")
        return p

    if project_name:
        p = (
            db.query(Project)
            .filter(func.lower(Project.project_name) == func.lower(project_name))
            .first()
        )
        if not p:
            raise NotFoundError(message=f"Project '{project_name}' not found", code="404")
        return p

    raise BadRequestError(message="Either project_id or project_name must be provided", code="400")

def _enforce_project_sync(payload: dict, db_project: Project) -> None:
    """
    Mutates payload so project_id and project_name are synced with the canonical project_table row.
    """
    payload["project_id"] = db_project.project_id
    payload["project_name"] = db_project.project_name

def get_all_services(db: Session):
    try:
        return db.query(GenRocketServicesDetails).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading services: {str(e)}")

def get_service_by_id(db: Session, workflow_id: int):
    try:
        service = (
            db.query(GenRocketServicesDetails)
            .filter(GenRocketServicesDetails.workflow_id == workflow_id)
            .first()
        )
        if not service:
            raise NotFoundError(message="Service not found", code="404")
        return service
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading service: {str(e)}")

def create_service(db: Session, service: GenRocketServicesDetailsCreate):
    try:
        payload = service.model_dump() if hasattr(service, "model_dump") else service.dict()

        # ✅ Normalize & validate tool_id existence
        normalized_tool_id = _normalize_tool_id(payload.get("tool_id"))
        _assert_tool_exists(db, normalized_tool_id)
        payload["tool_id"] = normalized_tool_id

        # ✅ Ensure unique workflow_name
        existing_workflow_name = (
            db.query(GenRocketServicesDetails)
            .filter(GenRocketServicesDetails.workflow_name == payload["workflow_name"])
            .first()
        )
        if existing_workflow_name:
            raise HTTPException(
                status_code=400,
                detail="Workflow with same name already in use. Choose a different one.",
            )

        # ✅ Resolve canonical project and sync id+name (fixes your defect)
        db_project = _resolve_project(
            db,
            project_id=payload.get("project_id"),
            project_name=payload.get("project_name"),
        )
        _enforce_project_sync(payload, db_project)

        # ⛔ DO NOT auto-generate project_id here.
        # Keep your existing auto-gen for module_id & scenario_id if required.
        last_module = (
            db.query(GenRocketServicesDetails)
            .order_by(GenRocketServicesDetails.module_id.desc())
            .first()
        )
        module_id = (last_module.module_id + 1) if last_module else 1

        last_scenario = (
            db.query(GenRocketServicesDetails)
            .order_by(GenRocketServicesDetails.scenario_id.desc())
            .first()
        )
        scenario_id = (last_scenario.scenario_id + 1) if last_scenario else 1

        db_service = GenRocketServicesDetails(
            **payload,
            module_id=module_id,
            scenario_id=scenario_id,
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    except BadRequestError as ve:
        db.rollback()
        raise ve
    except NotFoundError:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(
            message=f"DB operation failed while creating service: {str(e)}", code="500"
        )

def update_service(db: Session, workflow_id: int, service: GenRocketServicesDetailsUpdate):
    try:
        db_service = (
            db.query(GenRocketServicesDetails)
            .filter(GenRocketServicesDetails.workflow_id == workflow_id)
            .first()
        )
        if not db_service:
            raise NotFoundError(message="Service not found", code="404")

        updates = (
            service.model_dump(exclude_unset=True)
            if hasattr(service, "model_dump")
            else service.dict(exclude_unset=True)
        )

        # ✅ Normalize & validate tool_id existence if present
        if "tool_id" in updates and updates["tool_id"] is not None:
            normalized_tool_id = _normalize_tool_id(updates["tool_id"])
            _assert_tool_exists(db, normalized_tool_id)
            updates["tool_id"] = normalized_tool_id

        # ✅ If either project_id or project_name provided, resolve and sync both
        if ("project_id" in updates and updates["project_id"] is not None) or \
           ("project_name" in updates and updates["project_name"] is not None):
            db_project = _resolve_project(
                db,
                project_id=updates.get("project_id"),
                project_name=updates.get("project_name"),
            )
            _enforce_project_sync(updates, db_project)

        for key, value in updates.items():
            setattr(db_service, key, value)

        db.commit()
        db.refresh(db_service)
        return db_service

    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(
            message=f"DB operation failed while updating service: {str(e)}", code="500"
        )

def delete_service(db: Session, workflow_id: int):
    try:
        db_service = (
            db.query(GenRocketServicesDetails)
            .filter(GenRocketServicesDetails.workflow_id == workflow_id)
            .first()
        )
        if not db_service:
            raise NotFoundError(message="Service not found", code="404")

        db.delete(db_service)
        db.commit()
        return db_service

    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBDeleteError(
            message=f"DB operation failed while deleting service: {str(e)}", code="500"
        )
