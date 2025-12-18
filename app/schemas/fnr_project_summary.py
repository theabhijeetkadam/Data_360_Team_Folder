
# app/schemas/fnr_project_summary.py
from pydantic import BaseModel
from typing import Optional, List

# -----------------------------
# Existing: Project Summary Out
# -----------------------------
class FnrProjectSummaryOut(BaseModel):
    workflow_id: int
    workflow_name: str
    project_id: int                  # ✅ NEW: include project_id in response
    project_name: str
    environment_name: str
    module_name: str
    number_of_modules: int
    number_of_workflows: int

    class Config:
        orm_mode = True

# ---------------------------------
# Workflow Summary response (unchanged shape but now keyed by project_id in query)
# ---------------------------------
class FnrWorkflowSummaryItem(BaseModel):
    workflow_id: int
    workflow_name: str

class FnrWorkflowSummaryOut(BaseModel):
    project_name: str
    project_id: Optional[int] = None   # echoed from query param
    workflows: List[FnrWorkflowSummaryItem]

    class Config:
        orm_mode = True
