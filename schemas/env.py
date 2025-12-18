from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EnvironmentBase(BaseModel):
    env_name: Optional[str] = None
    env_instance: Optional[str] = None
    env_app_name: Optional[str] = None
    env_db_type: Optional[str] = None
    db_p1_name: Optional[str] = None
    db_p2_name: Optional[str] = None
    db_p3_name: Optional[str] = None
    db_p4_name: Optional[str] = None
    db_p5_name: Optional[str] = None
    db_p6_name: Optional[str] = None
    db_p7_name: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    updated_at: Optional[datetime] = None       # ✅ New field
    updated_by: Optional[str] = None            # ✅ New field



class EnvironmentCreate(EnvironmentBase):
    pass

class Environment(EnvironmentBase):
    env_id: int

    class Config:
        from_attributes = True
