
# app/schemas/fnr_project_summary.py
from pydantic import BaseModel
from typing import Optional, List

# -----------------------------
# Project Summary (one row per project; aggregated across environments)
# -----------------------------
class FnrProjectSummaryOut(BaseModel):
    project_id: int
    project_name: str
    number_of_modules: int
    number_of_workflows: int

    class Config:
        # If you're on Pydantic v2, use: from_attributes = True
        orm_mode = True

# ---------------------------------
# Workflow Summary (unchanged; keyed by project_id via query)
# ---------------------------------
class FnrWorkflowSummaryItem(BaseModel):
    workflow_id: int
    workflow_name: str

class FnrWorkflowSummaryOut(BaseModel):
    project_name: str
    project_id: Optional[int] = None  # echoed from query param / resolved via helper
    workflows: List[FnrWorkflowSummaryItem]

    class Config:
           orm_mode = True