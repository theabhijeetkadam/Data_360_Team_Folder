
# app/schemas/mining_workflow_output_criteria.py
from pydantic import BaseModel
from typing import Optional
from typing import Annotated, Optional
from pydantic import BaseModel, Field


# Allow only letters, numbers, spaces, hyphens, underscores, and dots (tweak as needed)
# Disallow leading/trailing spaces and consecutive special characters if needed.
BUSINESS_NAME_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9 _\.-]*[A-Za-z0-9]$"

BusinessName = Annotated[
    str,
    Field(
        min_length=2,
        max_length=100,
        pattern=BUSINESS_NAME_PATTERN,
        description="Only letters, numbers, spaces, hyphens (-), underscores (_), and dots (.) allowed. Must start and end with an alphanumeric."
    )
]


class MiningWorkflowOutputCriteriaBase(BaseModel):
    business_name: BusinessName
    # add other shared fields here (if any)



class MiningWorkflowOutputCriteriaBase(BaseModel):
    project_name: str
    module_name: str
    environment_name: str
    workflow_name: str
    # ✅ Include workflow_id in payloads and responses
    workflow_id: int

    business_name: BusinessName
    source_table: Optional[str] = None
    source_column: Optional[str] = None

class MiningWorkflowOutputCriteriaCreate(MiningWorkflowOutputCriteriaBase):
    pass

class MiningWorkflowOutputCriteriaUpdate(MiningWorkflowOutputCriteriaBase):
    pass

class MiningWorkflowOutputCriteriaOut(MiningWorkflowOutputCriteriaBase):
    output_criteria_id: int

    class Config:
        orm_mode = True  # keep as-is to avoid broader changes
