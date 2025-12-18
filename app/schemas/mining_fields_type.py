from pydantic import BaseModel

class MiningFieldsTypeBase(BaseModel):
    type_of_field: str

class MiningFieldsTypeCreate(MiningFieldsTypeBase):
    pass

class MiningFieldsTypeUpdate(MiningFieldsTypeBase):
    pass

class MiningFieldsTypeResponse(MiningFieldsTypeBase):
    field_id: int

    class Config:
        orm_mode = True
