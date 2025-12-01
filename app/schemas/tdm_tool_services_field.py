
from pydantic import BaseModel

class TDMToolWorkflowFieldBase(BaseModel):
    tool_id: str
    tool_name: str
    workflow_field_1: str | None = None
    workflow_field_2: str | None = None
    workflow_field_3: str | None = None
    workflow_field_4: str | None = None
    workflow_field_5: str | None = None
    workflow_field_6: str | None = None
    workflow_field_7: str | None = None
    workflow_field_8: str | None = None
    workflow_field_9: str | None = None
    workflow_field_10: str | None = None

class TDMToolWorkflowFieldCreate(TDMToolWorkflowFieldBase):
    pass

class TDMToolWorkflowFieldUpdate(TDMToolWorkflowFieldBase):
    pass

class TDMToolWorkflowFieldResponse(TDMToolWorkflowFieldBase):
    model_config = {"from_attributes": True}  # ✅ Pydantic v2 replacement for orm_mode
