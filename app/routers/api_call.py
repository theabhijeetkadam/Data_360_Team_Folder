
# app/routers/api_calls.py
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.api_call import ApiCallOut
from app.crud.api_call import list_api_calls

router = APIRouter(prefix="/api-calls", tags=["API Calls"])

@router.get("/", response_model=list[ApiCallOut])
def get_api_calls(
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    path: str | None = None,
    method: str | None = None,
):
    return list_api_calls(db, limit=limit, offset=offset, path=path, method=method)
