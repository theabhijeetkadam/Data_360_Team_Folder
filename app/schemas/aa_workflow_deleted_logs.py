from pydantic import BaseModel
from datetime import datetime

class AAWorkflowDeletedLogsBase(BaseModel):
    project_id: int
    project_name: str
    module_id: int
    module_name: str
    environment_id: int
    environment_name: str
    scenario_id: int
    scenario_name: str
    workflow_id: int
    deleted_by_user_id: int
    deleted_by_user_name: str

class AAWorkflowDeletedLogsCreate(AAWorkflowDeletedLogsBase):
    pass

class AAWorkflowDeletedLogsOut(AAWorkflowDeletedLogsBase):
    deleted_log_id: int
    deleted_at: datetime

    class Config:
        from_attributes = True  # Updated for Pydantic v2
