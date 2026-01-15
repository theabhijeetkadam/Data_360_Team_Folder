from pydantic import BaseModel
from typing import Optional

class ParametersRelationDetailsBase(BaseModel):
    project_name: str
    module_name: str
    environment_name: str
    workflow_name: str
    primary_table_name: Optional[str] = None
    primary_column_name: Optional[str] = None
    secondary_table_name: Optional[str] = None
    secondary_column_name: Optional[str] = None

class ParametersRelationDetailsCreate(ParametersRelationDetailsBase):
    pass

class ParametersRelationDetailsUpdate(ParametersRelationDetailsBase):
    pass

class ParametersRelationDetailsOut(ParametersRelationDetailsBase):
    relation_id: int
    workflow_id: int
    class Config:
        orm_mode = True
