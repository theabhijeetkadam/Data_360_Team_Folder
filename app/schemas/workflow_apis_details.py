from pydantic import BaseModel
from typing import Optional, Dict

class WorkflowAPIDetailsBase(BaseModel):
    project_id: int
    module_id: int
    environment_id: int
    scenario_id: str
    workflow_id: int
    api_name: str
    endpoint_url: str
    http_method: str
    headers: Optional[Dict] = None
    payload_template: Optional[str] = None
    auth_type: Optional[str] = None
    auth_details: Optional[Dict] = None
    timeout: Optional[int] = None
    retry_policy: Optional[str] = None

class WorkflowAPIDetailsCreate(WorkflowAPIDetailsBase):
    pass

class WorkflowAPIDetailsUpdate(BaseModel):
    api_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    http_method: Optional[str] = None
    headers: Optional[Dict] = None
    payload_template: Optional[str] = None
    auth_type: Optional[str] = None
    auth_details: Optional[Dict] = None
    timeout: Optional[int] = None
    retry_policy: Optional[str] = None

class WorkflowAPIDetailsResponse(WorkflowAPIDetailsBase):
    api_id: int

    class Config:
        from_attributes = True  # for SQLAlchemy ORM compatibility
