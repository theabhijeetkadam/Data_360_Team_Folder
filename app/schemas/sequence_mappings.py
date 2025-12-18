from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SequenceMappingBase(BaseModel):
    workflow_id: int
    sql_id: int
    execution_order: int

class SequenceMappingCreate(SequenceMappingBase):
    pass

class SequenceMappingUpdate(BaseModel):
    workflow_id: Optional[int]
    sql_id: Optional[int]
    execution_order: Optional[int]

class SequenceMappingResponse(SequenceMappingBase):
    sequence_id: int
    created_at: datetime

    class Config:
        orm_mode = True
