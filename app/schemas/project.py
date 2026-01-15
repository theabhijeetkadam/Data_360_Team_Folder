
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProjectBase(BaseModel):
    project_name: str
    project_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None       # ✅ Timestamp
    created_by_name: Optional[str] = None
    created_by_role: Optional[str] = None
    created_by_user_id: Optional[int] = None
    updated_by: Optional[str] = None            # ✅ String type
    module_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    project_id: int
    module_id: int
    scenario_id: int

    class Config:
        from_attributes = True
