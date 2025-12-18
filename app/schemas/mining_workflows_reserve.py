
# app/schemas/mining_workflows_reserve.py
from pydantic import BaseModel, ConfigDict
from typing import Optional

# Base
class MiningWorkflowsReserveBase(BaseModel):
    workflow_name: str
    project_id: Optional[int] = None
    env_id: Optional[int] = None
    # names are optional and can be derived from relationships or denormalized columns
    project_name: Optional[str] = None
    env_name: Optional[str] = None

# Create
class MiningWorkflowsReserveCreate(MiningWorkflowsReserveBase):
    pass

# Update
class MiningWorkflowsReserveUpdate(BaseModel):
    workflow_name: Optional[str] = None
    project_id: Optional[int] = None
    env_id: Optional[int] = None
    project_name: Optional[str] = None
    environment_name: Optional[str] = None

# Response
class MiningWorkflowsReserveResponse(BaseModel):
    workflow_id: int
    workflow_name: str
    project_id: Optional[int] = None
    env_id: Optional[int] = None
    project_name: Optional[str] = None
    environment_name: Optional[str] = None

    # For Pydantic v2:
    model_config = ConfigDict(from_attributes=True)
    # If you're on Pydantic v1, use:
    # class Config:
    #     orm_mode = True
