from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TDMToolBase(BaseModel):
    tool_id: str
    tool_name: str
    tool_type: Optional[str] = None
    active_flag: Optional[str] = str

class TDMToolCreate(TDMToolBase):
    pass

class TDMToolUpdate(TDMToolBase):
    pass

class TDMToolResponse(TDMToolBase):
    tool_id: str
    

    class Config:
        from_attributes = True
