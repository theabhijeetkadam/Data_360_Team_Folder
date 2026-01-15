from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class SQLTemplateBase(BaseModel):
    workflow_id: int
    sql_name: str
    table_name: Optional[str]
    sql_query: Optional[str]
    query_type: Optional[str]
    param_schema: Optional[Any]
    created_by: Optional[str]

class SQLTemplateCreate(SQLTemplateBase):
    pass

class SQLTemplateUpdate(BaseModel):
    sql_name: Optional[str]
    table_name: Optional[str]
    sql_query: Optional[str]
    query_type: Optional[str]
    param_schema: Optional[Any]
    created_by: Optional[str]

class SQLTemplateResponse(SQLTemplateBase):
    sql_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
