from pydantic import BaseModel
from typing import Optional
from datetime import date, time

class GovernanceDeleteLogBase(BaseModel):
    deleted_by_user_emp_id: Optional[str]
    deleted_by_user_name: Optional[str]
    deleted_by_user_email_id: Optional[str]
    deleted_project_name: Optional[str]
    deleted_module_name: Optional[str]
    deleted_scenario_name: Optional[str]
    deleted_environment_name: Optional[str]
    deleted_database_type: Optional[str]
    deleted_date: Optional[date]
    deleted_time: Optional[time]

class GovernanceDeleteLogCreate(GovernanceDeleteLogBase):
    pass

class GovernanceDeleteLogUpdate(GovernanceDeleteLogBase):
    pass

class GovernanceDeleteLog(GovernanceDeleteLogBase):
    log_id: int
    deleted_project_id: int
    deleted_environment_id: int

    class Config:
        from_attributes = True  # Pydantic v2
