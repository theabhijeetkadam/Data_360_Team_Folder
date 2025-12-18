from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class RuntimeLogBase(BaseModel):
    workflow_id: int
    sql_id: int
    status: Optional[str]
    ended_at: Optional[datetime]
    executed_by: Optional[str]

class RuntimeLogCreate(RuntimeLogBase):
    pass

class RuntimeLogUpdate(BaseModel):
    status: Optional[str]
    ended_at: Optional[datetime]
    executed_by: Optional[str]

class RuntimeLogResponse(RuntimeLogBase):
    execution_id: int
    started_at: datetime

    class Config:
        orm_mode = True
