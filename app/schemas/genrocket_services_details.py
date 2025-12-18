
# app/schemas/genrocket_services_details.py
from pydantic import BaseModel
from typing import Optional

class GenRocketServicesDetailsBase(BaseModel):
    workflow_name: str  # ✅ Updated field
    tool_id: int        # ✅ CHANGED to int
    project_name: str
    domain_name: str
    environment: str
    clientappid: str
    clientuserid: str
    scenario: str
    module_name: str
    username: str
    password: str
    scenariopath: str
    keepfilename: bool

class GenRocketServicesDetailsCreate(GenRocketServicesDetailsBase):
    pass

# For updates, make fields optional to support partial updates (safer),
# or keep as-is if you require full payload. I’m preserving your existing style,
# but changing tool_id type to int.
class GenRocketServicesDetailsUpdate(GenRocketServicesDetailsBase):
    pass

class GenRocketServicesDetailsResponse(GenRocketServicesDetailsBase):
    workflow_id: int
    project_id: int
    module_id: int
    scenario_id: int

    class Config:
        from_attributes = True  # Pydantic v2
