from pydantic import BaseModel

class ProjectSummaryDB(BaseModel):
    project_name: str
    number_of_modules: int
    number_of_workflows: int

    class Config:
        orm_mode = True