from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TDMToolBase(BaseModel):
    tool_id: int
    tool_name: str
    tool_type: Optional[str] = None
    active_flag: Optional[str] = str

class TDMToolCreate(TDMToolBase):
    pass

class TDMToolUpdate(TDMToolBase):
    pass

class TDMToolResponse(TDMToolBase):
    tool_id: int
    

    class Config:
        from_attributes = True
