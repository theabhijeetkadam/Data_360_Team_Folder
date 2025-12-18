from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ExecutionLogCreate(BaseModel):
    workflow_id: int
    sql_id: int
    status: Optional[str] = None
    response_message: Optional[str] = None
    error_message: Optional[str] = None
    record_count: Optional[int] = None
    ended_at: Optional[datetime] = None
    executed_by: Optional[str] = None
    environment_id: Optional[int] = None

class ExecutionLogResponse(ExecutionLogCreate):
    execution_id: int
    started_at: datetime

    class Config:
        orm_mode = True
