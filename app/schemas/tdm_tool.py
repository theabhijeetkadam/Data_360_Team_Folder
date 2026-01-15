
# app/schemas/tdm_tool.py
from pydantic import BaseModel
from typing import Optional

class TDMToolBase(BaseModel):
    tool_name: str
    tool_type: Optional[str] = None
    active_flag: Optional[str] = None  # Keep as str to match model

class TDMToolCreate(TDMToolBase):
    # No tool_id here – it's auto-generated.
    pass

class TDMToolUpdate(BaseModel):
    # tool_id must not be part of update payload.
    tool_name: Optional[str] = None
    tool_type: Optional[str] = None
    active_flag: Optional[str] = None

class TDMToolResponse(BaseModel):
    tool_id: int
    tool_name: str
    tool_type: Optional[str] = None
    active_flag: Optional[str] = None

    class Config:
        from_attributes = True  # FastAPI / SQLAlchemy compatibility
