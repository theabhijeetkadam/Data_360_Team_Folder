from pydantic import BaseModel
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WorkflowBase(BaseModel):
    project_id: Optional[int]
    project_name: Optional[str]
    module_id: Optional[int]
    module_name: Optional[str]
    environment_id: Optional[int]
    environment_name: Optional[str]
    scenario_id: Optional[int]
    scenario_name: Optional[str]
    created_by: Optional[str]

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(WorkflowBase):
    pass

class WorkflowResponse(WorkflowBase):
    workflow_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True  # replaces orm_mode=True for Pydantic v2