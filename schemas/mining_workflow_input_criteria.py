
# app/schemas/mining_workflow_input_criteria.py
from typing import Annotated, Optional
from pydantic import BaseModel, Field

# Allow only letters, numbers, spaces, hyphens, underscores, and dots (tweak as needed)
# Must start and end with alphanumeric (prevents leading/trailing spaces/separators).
BUSINESS_NAME_PATTERN = r"^[A-Za-z0-9][A-Za-z0-9 _\.-]*[A-Za-z0-9]$"

BusinessName = Annotated[
    str,
    Field(
        min_length=2,
        max_length=100,
        pattern=BUSINESS_NAME_PATTERN,
        description=(
            "Only letters, numbers, spaces, hyphens (-), underscores (_), and dots (.) allowed. "
            "Must start and end with an alphanumeric."
        ),
    ),
]


class MiningWorkflowInputCriteriaCreate(BaseModel):
    project_name: str
    module_name: str
    environment_name: str
    workflow_name: str
    business_name: BusinessName
    source_table: Optional[str] = None
    source_column: Optional[str] = None
    # ✅ Accept workflow_id in create
    workflow_id: int
    # ✅ (Optional) allow clients to send type_of_field; CRUD already supports it
    type_of_field: Optional[str] = None


class MiningWorkflowInputCriteriaUpdate(BaseModel):
    project_name: Optional[str] = None
    module_name: Optional[str] = None
    environment_name: Optional[str] = None
    workflow_name: Optional[str] = None
    business_name: Optional[str] = None
    source_table: Optional[str] = None
    source_column: Optional[str] = None
    # ✅ Allow changing workflow_id in update (optional)
    workflow_id: Optional[int] = None
    # ✅ (Optional) allow updating type_of_field
    type_of_field: Optional[str] = None


class MiningWorkflowInputCriteriaOut(BaseModel):
    input_criteria_id: int
    param_id: int
    project_id: int
    module_id: int
    environment_id: int
    # ✅ Ensure it’s in the response
    workflow_id: int

    project_name: str
    module_name: str
    environment_name: str
    workflow_name: str
    business_name: Optional[str] = None
    source_table: Optional[str] = None
    source_column: Optional[str] = None

    # ✅ NEW: include type_of_field in the response payload
    type_of_field: Optional[str] = None

    class Config:
        # Pydantic v2 (replacement for orm_mode)
        from_attributes = True
