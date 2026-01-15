from pydantic import BaseModel
from typing import Optional

class AccessMatrixBase(BaseModel):
    role_name: str
    sub_functionality_name: Optional[str]
    action_type: Optional[str]
    action_flag: Optional[bool] = False

class AccessMatrixCreate(AccessMatrixBase):
    pass

class AccessMatrixUpdate(BaseModel):
    role_name: Optional[str]
    sub_functionality_name: Optional[str]
    action_type: Optional[str]
    action_flag: Optional[bool]

class AccessMatrixResponse(AccessMatrixBase):
    id: int

    class Config:
        orm_mode = True
