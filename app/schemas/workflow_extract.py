
# app/schemas/workflow_extract.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class WorkflowSelection(BaseModel):
    data_key: str
    field_values: Optional[Dict[str, Any]] = None   # optional if server re-fetches by key
    is_selected: bool = Field(default=False)        # first column checkbox
    is_reserved: bool = Field(default=False)        # reserve checkbox

class ExtractRequest(BaseModel):
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    environment_id: Optional[int] = None
    execution_id: Optional[str] = None

    source_table: str
    confirm_no_reserve: bool = False

    selections: List[WorkflowSelection]
