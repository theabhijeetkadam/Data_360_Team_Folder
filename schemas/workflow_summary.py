# app/schemas/workflow_summary.py
from typing import List
from pydantic import BaseModel

class WorkflowItem(BaseModel):
    workflow_id: int
    workflow_name: str

    class Config:
        orm_mode = True

class WorkflowSummaryResponse(BaseModel):
    project_name: str
    project_id: int
    workflows: List[WorkflowItem]

    class Config:
        orm_mode = True
