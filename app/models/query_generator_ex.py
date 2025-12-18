from pydantic import BaseModel, validator
from typing import List

class Condition(BaseModel):
    field: str
    operator: str
    value: str

class Group(BaseModel):
    logical: str
    conditions: List[Condition]

    @validator("logical")
    def validate_logical(cls, v):
        if v not in ["AND", "OR"]:
            raise ValueError("Logical must be AND or OR")
        return v

class UserSelection(BaseModel):
    workflow_id: int
    groups: List[Group]
    group_operator: str

    @validator("group_operator")
    def validate_group_operator(cls, v):
        if v not in ["AND", "OR"]:
            raise ValueError("Group operator must be AND or OR")
        return v
