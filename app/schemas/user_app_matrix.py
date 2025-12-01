from pydantic import BaseModel
from typing import Optional

class UserAppMatrixBase(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    project_id: int

class UserAppMatrixCreate(UserAppMatrixBase):
    pass

class UserAppMatrix(UserAppMatrixBase):
    matrix_id: int

    class Config:
        from_attributes = True
