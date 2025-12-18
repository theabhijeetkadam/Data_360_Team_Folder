from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WorkflowBase(BaseModel):
    workflow_name: str
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    module_id: Optional[int] = None
    module_name: Optional[str] = None
    environment_id: Optional[int] = None
    environment_name: Optional[str] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = True

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(WorkflowBase):
    #workflow_id: int
    pass

class WorkflowResponse(WorkflowBase):
    workflow_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # replaces orm_mode in Pydantic v2
