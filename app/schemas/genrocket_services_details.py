from pydantic import BaseModel

class GenRocketServicesDetailsBase(BaseModel):
    workflow_name: str  # ✅ Updated field
    tool_id: str
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

class GenRocketServicesDetailsUpdate(GenRocketServicesDetailsBase):
    pass

class GenRocketServicesDetailsResponse(GenRocketServicesDetailsBase):
    workflow_id: int
    project_id: int
    module_id: int
    scenario_id: int

    class Config:
        from_attributes = True