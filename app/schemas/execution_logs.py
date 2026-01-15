from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ExecutionLogBase(BaseModel):
    workflow_id: int
    api_id: int
    status: str
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    end_time: Optional[datetime] = None
    executed_by: Optional[str] = None

class ExecutionLogCreate(ExecutionLogBase):
    pass

class ExecutionLogUpdate(ExecutionLogBase):
    pass

class ExecutionLogOut(ExecutionLogBase):
    execution_id: int
    executed_at: datetime

    class Config:
        from_attributes = True   # Pydantic v2 equivalent of orm_mode
