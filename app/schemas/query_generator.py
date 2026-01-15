
# app/schemas/query_generator.py
from pydantic import BaseModel, field_validator
from typing import List, Union, Literal

# Keep these in sync with router
ALLOWED_SCHEMAS = {"gold_copy"}
ALLOWED_TABLES = {"Customer", "Customer_cards","Customer_address","Customer_rewards","Customer_payments"}

ALLOWED_OPERATORS = {
    "=", "!=", ">", "<", ">=", "<=",
    "IN", "NOT IN",
    "LIKE", "ILIKE"
}

def decode_operator(op: str) -> str:
    """Decode HTML entities and normalize to uppercase SQL operators."""
    o = op.strip()
    html_map = {
        "&amp;gt;": ">",
        "&amp;lt;": "<",
        "&amp;gt;=": ">=",
        "&amp;lt;=": "<=",
        "&gt;": ">",
        "&lt;": "<",
        "&gt;=": ">=",
        "&lt;=": "<=",
    }
    o = html_map.get(o, o)
    # Normalize words like 'in' to 'IN'
    return o.upper()

class Condition(BaseModel):
    field: str  # "schema.table.column"
    operator: str
    value: Union[str, int, float, bool, List[Union[str, int, float, bool]]]

    @field_validator("field")
    def validate_field(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid field format: {v}. Expected 'schema.table.column'")
        schema, table, column = parts
        if schema not in ALLOWED_SCHEMAS:
            raise ValueError(f"Unsupported schema: {schema}")
        if table not in ALLOWED_TABLES:
            raise ValueError(f"Unsupported table: {table}")
        if not column:
            raise ValueError("Column name cannot be empty")
        # Do NOT check columns here; let the router/DB handle missing columns
        return v

    @field_validator("operator")
    def validate_operator(cls, v: str) -> str:
        op = decode_operator(v)
        if op not in ALLOWED_OPERATORS:
            raise ValueError(f"Unsupported operator: {v}")
        return op

class Group(BaseModel):
    logical: Literal["AND", "OR"]
    conditions: List[Condition]

class UserSelection(BaseModel):
    workflow_id: int
    groups: List[Group]
    group_operator: Literal["AND", "OR"]  # between groups
    data_volume: int
   
