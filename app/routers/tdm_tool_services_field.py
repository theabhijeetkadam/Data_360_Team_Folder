
# app/routers/tdm_tool_services_field.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.crud import tdm_tool_services_field as crud
from app.schemas.tdm_tool_services_field import (
    TDMToolWorkflowFieldCreate,
    TDMToolWorkflowFieldUpdate,
    TDMToolWorkflowFieldResponse,
)

router = APIRouter(
    prefix="/tdm_tool_workflow_field",
    tags=["TDM Tool Workflow Field"]
)

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Read all tools (typed response for clearer docs; keep dict if you prefer)
@router.get(
    "/",
    response_model=List[TDMToolWorkflowFieldResponse],
    operation_id="tdm_tool_workflow_field_list_all"
)
def read_tools(db: Session = Depends(get_db)):
    tools = crud.get_all_tools(db)
    return tools  # FastAPI will serialize ORM objects using model_config.from_attributes=True

# ✅ Read tool by ID (tool_id as int)
@router.get(
    "/{tool_id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_get_by_id"
)
def read_tool(tool_id: int, db: Session = Depends(get_db)):
    db_tool = crud.get_tool_by_id(db, tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool

# ✅ Create tool
@router.post(
    "/",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_create"
)
def create_tool(tool: TDMToolWorkflowFieldCreate, db: Session = Depends(get_db)):
    db_tool = crud.create_tool(db, tool)
    return db_tool

# ✅ Update tool (tool_id as int)
@router.put(
    "/{tool_id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_update"
)
def update_tool(tool_id: int, tool: TDMToolWorkflowFieldUpdate, db: Session = Depends(get_db)):
    db_tool = crud.update_tool(db, tool_id, tool)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool

# ✅ Delete tool (tool_id as int)
@router.delete(
    "/{tool_id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_delete"
)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    db_tool = crud.delete_tool(db, tool_id)
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return db_tool
