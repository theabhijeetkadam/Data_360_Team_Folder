
# app/schemas/tdm_tool_services_field.py
from pydantic import BaseModel
from typing import Optional

class TDMToolWorkflowFieldBase(BaseModel):
    tool_id: int  # required in create (FK to tdm_tool_names)
    tool_name: str
    workflow_field_1: Optional[str] = None
    workflow_field_2: Optional[str] = None
    workflow_field_3: Optional[str] = None
    workflow_field_4: Optional[str] = None
    workflow_field_5: Optional[str] = None
    workflow_field_6: Optional[str] = None
    workflow_field_7: Optional[str] = None
    workflow_field_8: Optional[str] = None
    workflow_field_9: Optional[str] = None
    workflow_field_10: Optional[str] = None

class TDMToolWorkflowFieldCreate(TDMToolWorkflowFieldBase):
    # No `id` here — DB auto-generates it
    pass

class TDMToolWorkflowFieldUpdate(BaseModel):
    # Do NOT allow changing tool_id by default (keeps referential integrity simple)
    tool_name: Optional[str] = None
    workflow_field_1: Optional[str] = None
    workflow_field_2: Optional[str] = None
    workflow_field_3: Optional[str] = None
    workflow_field_4: Optional[str] = None
    workflow_field_5: Optional[str] = None
    workflow_field_6: Optional[str] = None
    workflow_field_7: Optional[str] = None
    workflow_field_8: Optional[str] = None
    workflow_field_9: Optional[str] = None
    workflow_field_10: Optional[str] = None

class TDMToolWorkflowFieldResponse(BaseModel):
    id: int
    tool_id: int
    tool_name: str
    workflow_field_1: Optional[str] = None
    workflow_field_2: Optional[str] = None
    workflow_field_3: Optional[str] = None
    workflow_field_4: Optional[str] = None
    workflow_field_5: Optional[str] = None
    workflow_field_6: Optional[str] = None
    workflow_field_7: Optional[str] = None
    workflow_field_8: Optional[str] = None
    workflow_field_9: Optional[str] = None
    workflow_field_10: Optional[str] = None

    model_config = {"from_attributes": True}  # Pydantic v2
