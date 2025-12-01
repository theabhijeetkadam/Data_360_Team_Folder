from pydantic import BaseModel

class ProjectConfigBase(BaseModel):
    config_type: str

class ProjectConfigCreate(ProjectConfigBase):
    pass

class ProjectConfig(ProjectConfigBase):
    config_id: int

    class Config:
        from_attributes = True
