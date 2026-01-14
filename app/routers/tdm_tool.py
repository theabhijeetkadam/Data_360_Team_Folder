
# app/routers/tdm_tool.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.schemas.tdm_tool import TDMToolCreate, TDMToolUpdate
from app.crud import tdm_tool
from app.database import get_db
from app.exceptions import NotFoundError

router = APIRouter(prefix="/tdm-tools", tags=["TDM Tools"])

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

@router.get("/", response_model=dict)
def read_tools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tools = tdm_tool.get_tools(db=db, skip=skip, limit=limit)
    return {"message": "Tools retrieved successfully", "data": [to_dict(t) for t in tools], "code": "200"}

@router.get("/{tool_id}", response_model=dict)
def read_tool(tool_id: int, db: Session = Depends(get_db)):
    db_tool = tdm_tool.get_tool(db, tool_id)
    if not db_tool:
        raise NotFoundError(message="Tool not found", code="404")
    return {"message": "Tool details retrieved successfully", "data": to_dict(db_tool), "code": "200"}

@router.post("/", response_model=dict)
def create_tool(tool: TDMToolCreate, db: Session = Depends(get_db)):
    db_tool = tdm_tool.create_tool(db=db, tool=tool)
    return {"message": "Tool created successfully", "data": to_dict(db_tool), "code": "200"}

@router.put("/{tool_id}", response_model=dict)
def update_tool(tool_id: int, tool: TDMToolUpdate, db: Session = Depends(get_db)):
    db_tool = tdm_tool.update_tool(db=db, tool_id=tool_id, tool=tool)
    return {"message": "Tool updated successfully", "data": to_dict(db_tool), "code": "200"}

@router.delete("/{tool_id}", response_model=dict)
def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    db_tool = tdm_tool.delete_tool(db=db, tool_id=tool_id)
    return {"message": "Tool deleted successfully", "data": to_dict(db_tool), "code": "200"}