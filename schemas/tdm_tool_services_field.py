
# app/schemas/tdm_tool_services_field.py
from pydantic import BaseModel
from typing import Optional

class TDMToolWorkflowFieldBase(BaseModel):
    # ✅ CHANGED: tool_id is int
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

class TDMToolWorkflowFieldCreate(TDMToolWorkflowFieldBase):
    pass

class TDMToolWorkflowFieldUpdate(TDMToolWorkflowFieldBase):
    pass

class TDMToolWorkflowFieldResponse(TDMToolWorkflowFieldBase):
    model_config = {"from_attributes": True}  # Pydantic v2 replacement for orm_mode
