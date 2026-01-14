
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

@router.get(
    "/",
    response_model=List[TDMToolWorkflowFieldResponse],
    operation_id="tdm_tool_workflow_field_list_all"
)
def list_all(db: Session = Depends(get_db)):
    return crud.get_all_tools(db)

@router.get(
    "/by-tool/{tool_id}",
    response_model=List[TDMToolWorkflowFieldResponse],  # one or many depending on your design
    operation_id="tdm_tool_workflow_field_get_by_tool_id"
)
def get_by_tool_id(tool_id: int, db: Session = Depends(get_db)):
    items = crud.get_by_tool_id(db, tool_id)
    if not items:
        raise HTTPException(status_code=404, detail="No workflow fields found for this tool_id")
    return items

@router.get(
    "/{id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_get_by_id"
)
def get_by_id(id: int, db: Session = Depends(get_db)):
    item = crud.get_by_id(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow field not found")
    return item

@router.post(
    "/",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_create"
)
def create(tool: TDMToolWorkflowFieldCreate, db: Session = Depends(get_db)):
    return crud.create_tool(db, tool)

@router.put(
    "/{id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_update"
)
def update(id: int, tool: TDMToolWorkflowFieldUpdate, db: Session = Depends(get_db)):
    item = crud.update_tool(db, id, tool)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow field not found")
    return item

@router.delete(
    "/{id}",
    response_model=TDMToolWorkflowFieldResponse,
    operation_id="tdm_tool_workflow_field_delete"
)
def delete(id: int, db: Session = Depends(get_db)):
    item = crud.delete_tool(db, id)
    if not item:
        raise HTTPException(status_code=404, detail="Workflow field not found")
    return item