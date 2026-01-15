from pydantic import BaseModel

class EnvironmentInstanceBase(BaseModel):
    name: str

class EnvironmentInstanceCreate(EnvironmentInstanceBase):
    pass

class EnvironmentInstanceResponse(EnvironmentInstanceBase):
    id: int

    class Config:
        from_attributes = True