from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class OrchestrationDeleteLogBase(BaseModel):
    deleted_by_user_name: Optional[str]
    deleted_date: Optional[date]
    deleted_time: Optional[time]
    deleted_project_name: Optional[str]
    deleted_module_name: Optional[str]
    deleted_scenario_name: Optional[str]

class OrchestrationDeleteLogCreate(OrchestrationDeleteLogBase):
    pass

class OrchestrationDeleteLogUpdate(OrchestrationDeleteLogBase):
    pass

class OrchestrationDeleteLog(OrchestrationDeleteLogBase):
    log_id: int
    record_id: int
    deleted_project_id:int
    service_id:int

    class Config:
        from_attributes = True