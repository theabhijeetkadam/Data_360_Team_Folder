from pydantic import BaseModel
from typing import List, Optional

class UnreserveRequest(BaseModel):
    execution_id: Optional[List[int]] = []
    updated_by: str
