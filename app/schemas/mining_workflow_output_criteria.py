
from typing import Optional, Annotated
from pydantic import BaseModel, Field

# Allow only letters, numbers, spaces, hyphens, underscores, and dots
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
    # Project/Module/Env/Workflow identifiers (names + id)
    project_name: str
    module_name: str
    environment_name: str
    workflow_name: str
    workflow_id: int

    # Field meta
    business_name: BusinessName
    source_table: Optional[str] = None
    source_column: Optional[str] = None

    # ✅ New flag in payloads (default False)
    is_parameter_flag: Optional[bool] = False

class MiningWorkflowOutputCriteriaCreate(MiningWorkflowOutputCriteriaBase):
    pass

# For updates, allow partial updates
class MiningWorkflowOutputCriteriaUpdate(BaseModel):
    project_name: Optional[str] = None
    module_name: Optional[str] = None
    environment_name: Optional[str] = None
    workflow_name: Optional[str] = None
    workflow_id: Optional[int] = None

    business_name: Optional[BusinessName] = None
    source_table: Optional[str] = None
    source_column: Optional[str] = None

    # ✅ Toggle flag in update
    is_parameter_flag: Optional[bool] = None

class MiningWorkflowOutputCriteriaOut(MiningWorkflowOutputCriteriaBase):
    output_criteria_id: int

    class Config:
        orm_mode = True  # pydantic v1; for v2: from_attributes = True
