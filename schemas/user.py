
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    user_name: str
    user_emp_id: Optional[str] = None
    user_email_id: Optional[str] = None
    role_id: int
    user_role: str
    emp_name: str
    status: Optional[str] = "ACTIVE"
    updated_at: Optional[datetime] = None       # ✅ New field
    updated_by: Optional[str] = None            # ✅ New field


class UserCreate(UserBase):
    user_password: str

class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True
