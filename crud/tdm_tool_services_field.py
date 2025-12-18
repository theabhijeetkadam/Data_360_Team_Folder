
# app/crud/tdm_tool_services_field.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.tdm_tool_services_field import TDMToolWorkflowField
from app.schemas.tdm_tool_services_field import TDMToolWorkflowFieldCreate, TDMToolWorkflowFieldUpdate
from app.exceptions import NotFoundError, DuplicateEntryError, DBInsertError, DBUpdateError, DBDeleteError, DBReadError

def get_all_tools(db: Session):
    try:
        return db.query(TDMToolWorkflowField).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading tools: {str(e)}")

def get_tool_by_id(db: Session, tool_id: int):  # ✅ CHANGED: int
    try:
        tool = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == tool_id).first()
        if not tool:
            raise NotFoundError(message="Tool not found", code="404")
        return tool
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading tool: {str(e)}")

def create_tool(db: Session, tool: TDMToolWorkflowFieldCreate):
    try:
        # Optional: Check for duplicate tool_id
        if db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == tool.tool_id).first():
            raise DuplicateEntryError(message="Tool ID already exists", code="409")

        db_tool = TDMToolWorkflowField(**tool.model_dump())
        db.add(db_tool)
        db.commit()
        db.refresh(db_tool)
        return db_tool
    except DuplicateEntryError:
        raise
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"DB operation failed while creating tool: {str(e)}", code="500")

def update_tool(db: Session, tool_id: int, tool: TDMToolWorkflowFieldUpdate):  # ✅ CHANGED: int
    try:
        db_tool = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == tool_id).first()
        if not db_tool:
            raise NotFoundError(message="Tool not found", code="404")

        for key, value in tool.model_dump(exclude_unset=True).items():
            setattr(db_tool, key, value)

        db.commit()
        db.refresh(db_tool)
        return db_tool
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(message=f"DB operation failed while updating tool: {str(e)}", code="500")

def delete_tool(db: Session, tool_id: int):  # ✅ CHANGED: int
    try:
        db_tool = db.query(TDMToolWorkflowField).filter(TDMToolWorkflowField.tool_id == tool_id).first()
        if not db_tool:
            raise NotFoundError(message="Tool not found", code="404")

        db.delete(db_tool)
        db.commit()
        return db_tool
    except NotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        raise DBDeleteError(message=f"DB operation failed while deleting tool: {str(e)}", code="500")
