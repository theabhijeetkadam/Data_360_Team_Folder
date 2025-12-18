from pydantic import BaseModel
from typing import Optional

class APISequenceBase(BaseModel):
    workflow_id: Optional[int]
    api_id: Optional[int]
    execution_order: Optional[int]

class APISequenceCreate(APISequenceBase):
    workflow_id: int
    
    execution_order: int

class APISequenceUpdate(APISequenceBase):
    pass

class APISequence(APISequenceBase):
    sequence_id: int

    class Config:
        from_attributes = True  # For Pydantic v2