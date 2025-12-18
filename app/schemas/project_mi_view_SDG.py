from pydantic import BaseModel

class ProjectSummarySDG(BaseModel):
    project_name: str
    number_of_modules: int
    number_of_scenarios: int

    class Config:
        from_attributes = True
