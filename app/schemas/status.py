from pydantic import BaseModel

class StatusBase(BaseModel):
    entity_type: str
    status_value: str

class StatusCreate(StatusBase):
    pass

class StatusUpdate(StatusBase):
    pass

class StatusOut(StatusBase):
    status_id: int

    class Config:
        from_attributes = True