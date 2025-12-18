
# app/schemas/project_mi_view.py
from pydantic import BaseModel

class ProjectSummary(BaseModel):
    project_id: int            # ✅ NEW
    project_name: str
    number_of_modules: int
    number_of_scenarios: int

    class Config:
        orm_mode = True
