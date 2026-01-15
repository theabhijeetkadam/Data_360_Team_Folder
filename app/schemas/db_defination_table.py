from pydantic import BaseModel
from typing import Optional

class DBDefinationTableBase(BaseModel):
    db_name: str
    db_p1_name: Optional[str] = None
    db_p2_name: Optional[str] = None
    db_p3_name: Optional[str] = None
    db_p4_name: Optional[str] = None
    db_p5_name: Optional[str] = None
    db_p6_name: Optional[str] = None
    db_p7_name: Optional[str] = None

class DBDefinationTableCreate(DBDefinationTableBase):
    pass

class DBDefinationTable(DBDefinationTableBase):
    db_id: int

    class Config:
        from_attributes = True
