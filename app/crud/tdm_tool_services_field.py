
# app/crud/tdm_tool_services_field.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.tdm_tool_services_field import TDMToolWorkflowField
from app.models.tdm_tool import TdmToolName
from app.schemas.tdm_tool_services_field import TDMToolWorkflowFieldCreate, TDMToolWorkflowFieldUpdate
from app.exceptions import NotFoundError, DuplicateEntryError, DBInsertError, DBUpdateError, DBDeleteError, DBReadError

def get_all_tools(db: Session):
    try:
        return db.query(TDMToolWorkflowField).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading workflow fields: {str(e)}")

def get_by_id(db: Session, id: int):
    try:
        return db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.id == id).first()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading workflow field: {str(e)}")

def get_by_tool_id(db: Session, tool_id: int):
    try:
        return db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == tool_id).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading workflow fields by tool_id: {str(e)}")

def create_tool(db: Session, payload: TDMToolWorkflowFieldCreate):
    try:
        # Ensure tool_id exists (FK will enforce, but this gives a friendlier error)
        if not db.query(TdmToolName).filter(TdmToolName.tool_id == payload.tool_id).first():
            raise NotFoundError(message="Referenced tool_id does not exist in tdm_tool_names", code="404")

        # If one record per tool_id, enforce uniqueness manually (optional)
        existing = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == payload.tool_id).first()
        if existing:
            raise DuplicateEntryError(message="Workflow fields for this tool_id already exist", code="409")

        obj = TDMToolWorkflowField(**payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    except NotFoundError:
        raise
    except DuplicateEntryError:
        raise
    except IntegrityError as e:
        db.rollback()
        # Can be FK or unique violation
        raise DBInsertError(message=f"IntegrityError while creating workflow field: {str(e.orig)}", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"DB operation failed while creating workflow field: {str(e)}", code="500")

def update_tool(db: Session, id: int, payload: TDMToolWorkflowFieldUpdate):
    try:
        obj = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.id == id).first()
        if not obj:
            raise NotFoundError(message="Workflow field not found", code="404")

        # Do NOT allow tool_id changes here (keep referential integrity simpler)
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)

        db.commit()
        db.refresh(obj)
        return obj

    except NotFoundError:
        raise
    except IntegrityError as e:
        db.rollback()
        raise DBUpdateError(message=f"IntegrityError while updating workflow field: {str(e.orig)}", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(message=f"DB operation failed while updating workflow field: {str(e)}", code="500")

def delete_tool(db: Session, id: int):
    try:
        obj = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.id == id).first()
        if not obj:
            raise NotFoundError(message="Workflow field not found", code="404")

        db.delete(obj)
        db.commit()
        return obj

    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBDeleteError(message=f"DB operation failed while deleting workflow field: {str(e)}", code="500")
