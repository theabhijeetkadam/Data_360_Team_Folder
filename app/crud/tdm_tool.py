
# app/crud/tdm_tool.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.tdm_tool import TdmToolName
from app.schemas.tdm_tool import TDMToolCreate, TDMToolUpdate
from app.exceptions import DuplicateEntryError, NotFoundError, DBInsertError, DBUpdateError, DBDeleteError, DBReadError

def get_tools(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(TdmToolName).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading tools: {str(e)}")

def get_tool(db: Session, tool_id: int):
    try:
        tool = db.query(TdmToolName).filter(TdmToolName.tool_id == tool_id).first()
        if not tool:
            raise NotFoundError(message="Tool not found", code="404")
        return tool
    except SQLAlchemyError as e:
        raise DBReadError(message=f"DB operation failed while reading tool: {str(e)}")


def create_tool(db: Session, tool: TDMToolCreate):
    try:
        # Check duplicates on tool_name (unique)
        if db.query(TdmToolName).filter(TdmToolName.tool_name == tool.tool_name).first():
            raise DuplicateEntryError(message="Tool name already exists", code="409")

        # tool_id is not provided; DB will auto-generate it
        db_tool = TdmToolName(**tool.dict())
        db.add(db_tool)
        db.commit()
        db.refresh(db_tool)
        return db_tool

    except DuplicateEntryError:
        raise
    except IntegrityError as e:
        db.rollback()
        # If uniqueness fails, bubble a DuplicateEntryError
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBInsertError(message=f"DB operation failed while creating tool: {str(e)}", code="500")

def update_tool(db: Session, tool_id: int, tool: TDMToolUpdate):
    try:
        db_tool = db.query(TdmToolName).filter(TdmToolName.tool_id == tool_id).first()
        if not db_tool:
            raise NotFoundError(message="Tool not found", code="404")

        # Apply only provided fields; tool_id is NOT updatable
        for key, value in tool.dict(exclude_unset=True).items():
            setattr(db_tool, key, value)

        db.commit()
        db.refresh(db_tool)
        return db_tool

    except NotFoundError:
        raise
    except IntegrityError as e:
        db.rollback()
        # Name uniqueness violation, etc.
        raise DuplicateEntryError(message="Duplicate entry detected", code="409")
    except SQLAlchemyError as e:
        db.rollback()
        raise DBUpdateError(message=f"DB operation failed while updating tool: {str(e)}", code="500")

def delete_tool(db: Session, tool_id: int):
    try:
        db_tool = db.query(TdmToolName).filter(TdmToolName.tool_id == tool_id).first()
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
