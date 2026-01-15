# app/schemas/common.py
from pydantic import BaseModel

class MessageResponse(BaseModel):
    message: str