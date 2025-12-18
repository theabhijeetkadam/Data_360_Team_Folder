from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class SelectedRow(BaseModel):
    source_table: str
    data_key: str
    field_values: Dict[str, str]
    is_reserved: bool

class SaveSelectionRequest(BaseModel):
    project_id: int
    module_id: int
    environment_id: int
    workflow_id: int
    execution_id: str
    selections: List[SelectedRow]

