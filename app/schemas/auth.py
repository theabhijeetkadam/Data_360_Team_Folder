
# app/schemas/auth.py
from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class UserDetails(BaseModel):
    user_id: int
    user_name: str
    user_email_id: str
    user_role: str
    emp_name: Optional[str] = None

    class Config:
        orm_mode = True  # allows reading directly from SQLAlchemy model objects

class LoginResponse(BaseModel):
    message: str
    username:str
