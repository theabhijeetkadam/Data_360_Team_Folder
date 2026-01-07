
# app/schemas/api_call.py
from datetime import datetime
from pydantic import BaseModel

class ApiCallBase(BaseModel):
    path: str
    method: str
    status_code: int
    timestamp: datetime  # ISO-8601, stored as UTC
    user_id: int | None = None

class ApiCallCreate(ApiCallBase):
    pass

class ApiCallOut(ApiCallBase):
    id: int

    class Config:
        orm_mode = True
