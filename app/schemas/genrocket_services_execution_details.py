from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional

class GenRocketServicesExecutionDetailsBase(BaseModel):
    tool_id: str
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

class GenRocketServicesExecutionDetailsUpdate(GenRocketServicesExecutionDetailsBase):
    pass

class GenRocketServicesExecutionDetailsResponse(GenRocketServicesExecutionDetailsBase):
    job_id: int
    model_config = {"from_attributes": True}  # Pydantic v2