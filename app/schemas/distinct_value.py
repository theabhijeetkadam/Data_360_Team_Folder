# app/schemas/fetch_values.py

from pydantic import BaseModel

class FetchValuesRequest(BaseModel):
    workflow_id: int
    business_name: str
