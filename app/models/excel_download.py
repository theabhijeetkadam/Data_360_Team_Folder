from pydantic import BaseModel
from typing import Optional

class ExportRequest(BaseModel):
    workflow_id: int
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    environment_id: Optional[int] = None
    execution_id: Optional[str] = None
