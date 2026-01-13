from pydantic import BaseModel
from typing import Optional, Dict, List

class WorkflowExecutionLogCreate(BaseModel):
    workflow_id: int
    input_json: List[Dict] = None
    created_by_user_id: int
