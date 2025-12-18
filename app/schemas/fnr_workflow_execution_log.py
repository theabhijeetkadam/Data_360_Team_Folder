from pydantic import BaseModel
from typing import Optional, Dict

class WorkflowExecutionLogCreate(BaseModel):
    project_id: int
    module_id: int
    environment_id: int
    workflow_id: int
    input_json: Optional[Dict] = None
    created_by_user_id: int
