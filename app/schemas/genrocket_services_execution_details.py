
# app/schemas/genrocket_services_execution_details.py
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class GenRocketServicesExecutionDetailsBase(BaseModel):
    # ✅ CHANGED: tool_id as int
    tool_id: int
    tool_name: str
    workflow_id: int
    start_time: datetime
    end_time: datetime
    runtime: timedelta
    created_by: str
    status: str
    output_json: Optional[str] = None

class GenRocketServicesExecutionDetailsCreate(GenRocketServicesExecutionDetailsBase):
    pass

class GenRocketServicesExecutionDetailsUpdate(BaseModel):
    # For partial updates, make fields optional
    tool_id: Optional[int] = None
    tool_name: Optional[str] = None
    workflow_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    runtime: Optional[timedelta] = None
    created_by: Optional[str] = None
    status: Optional[str] = None
    output_json: Optional[str] = None

class GenRocketServicesExecutionDetailsResponse(GenRocketServicesExecutionDetailsBase):
    job_id: int
    model_config = {"from_attributes": True}  # Pydantic v2
