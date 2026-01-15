
# app/schemas/genrocket_services_details.py
from pydantic import BaseModel, field_validator, model_validator
from typing import Optional

class GenRocketServicesDetailsBase(BaseModel):
    # Core fields
    workflow_name: str          # must be unique
    tool_id: int                # validated in CRUD to exist in tdm_tool_names

    # Project fields - either project_id OR project_name must be provided on create
    project_id: Optional[int] = None
    project_name: Optional[str] = None

    # Other service fields (adjust types/optionality as per your DB model)
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

    # Normalize blank strings to None for optional fields
    @field_validator("project_name", mode="before")
    def _normalize_project_name(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v if v != "" else None
        return v

class GenRocketServicesDetailsCreate(GenRocketServicesDetailsBase):
    """
    For create, require at least one of project_id or project_name.
    The backend will resolve the canonical project in CRUD and sync both fields.
    """
    @model_validator(mode="after")
    def _require_project_id_or_name(self):
        if self.project_id is None and (self.project_name is None or self.project_name == ""):
            raise ValueError("Either 'project_id' or 'project_name' must be provided.")
        return self

class GenRocketServicesDetailsUpdate(BaseModel):
    """
    Partial update – all fields optional. If project_id/project_name is present,
    CRUD will resolve and sync canonical id+name.
    """
    workflow_name: Optional[str] = None
    tool_id: Optional[int] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None

    domain_name: Optional[str] = None
    environment: Optional[str] = None
    clientappid: Optional[str] = None
    clientuserid: Optional[str] = None
    scenario: Optional[str] = None
    module_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    scenariopath: Optional[str] = None
    keepfilename: Optional[bool] = None

    @field_validator("project_name", mode="before")
    def _normalize_project_name(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v if v != "" else None
        return v

class GenRocketServicesDetailsResponse(GenRocketServicesDetailsBase):
    workflow_id: int
    project_id: int      # resolved/synced canonical project_id
    project_name: str    # resolved/synced canonical project_name
    module_id: int
    scenario_id: int

    class Config:
        from_attributes = True  # Pydantic v2
