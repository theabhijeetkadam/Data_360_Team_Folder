from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeletedLogCreate(BaseModel):
    workflow_id: Optional[int]
    project_id: Optional[int]
    module_id: Optional[int]
    environment_id: Optional[int]
    deleted_by: str
    deleted_by_name: str

class DeletedLogResponse(DeletedLogCreate):
    deleted_log_id: int
    deleted_at: datetime

    class Config:
        orm_mode = True

