
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import tdm_tool_services_field as crud  # ✅ Updated import
from app.schemas.tdm_tool_services_field import TDMToolWorkflowFieldCreate, TDMToolWorkflowFieldUpdate  # ✅ Updated schema names
from app.exceptions import NotFoundError

router = APIRouter(prefix="/tdm_tool_workflow_field", tags=["TDM Tool Workflow Field"])  # ✅ Updated prefix and tag

def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Read all tools
@router.get("/", response_model=dict)
def read_tools(db: Session = Depends(get_db)):
    tools = crud.get_all_tools(db)
    return {"message": "Tools retrieved successfully", "data": [to_dict(t) for t in tools], "code": "200"}

# ✅ Read tool by ID
@router.get("/{tool_id}", response_model=dict)
def read_tool(tool_id: str, db: Session = Depends(get_db)):
    db_tool = crud.get_tool_by_id(db, tool_id)
    return {"message": "Tool details retrieved successfully", "data": to_dict(db_tool), "code": "200"}

# ✅ Create tool
@router.post("/", response_model=dict)
def create_tool(tool: TDMToolWorkflowFieldCreate, db: Session = Depends(get_db)):
    db_tool = crud.create_tool(db, tool)
    return {"message": "Tool created successfully", "data": to_dict(db_tool), "code": "200"}

# ✅ Update tool
@router.put("/{tool_id}", response_model=dict)
def update_tool(tool_id: str, tool: TDMToolWorkflowFieldUpdate, db: Session = Depends(get_db)):
    db_tool = crud.update_tool(db, tool_id, tool)
    return {"message": "Tool updated successfully", "data": to_dict(db_tool), "code": "200"}

# ✅ Delete tool
@router.delete("/{tool_id}", response_model=dict)
def delete_tool(tool_id: str, db: Session = Depends(get_db)):
    db_tool = crud.delete_tool(db, tool_id)
    return {"message": "Tool deleted successfully", "data": to_dict(db_tool), "code": "200"}
