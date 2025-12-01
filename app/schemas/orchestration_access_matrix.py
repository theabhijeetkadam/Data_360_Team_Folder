from pydantic import BaseModel
from typing import Optional

class AccessMatrixBase(BaseModel):

    role_name: Optional[str]
    sub_functionality_name: Optional[str]
    action_type: Optional[str]
    action_flag: Optional[str]

class AccessMatrixCreate(AccessMatrixBase):
    pass

class AccessMatrixUpdate(AccessMatrixBase):
    pass

class AccessMatrixResponse(AccessMatrixBase):
    id: int

  #  class Config:
  #      orm_mode = True
model_config = {
        "from_attributes": True  # replaces orm_mode in Pydantic v2
    }