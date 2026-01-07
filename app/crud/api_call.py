
# app/crud/api_call.py
from sqlalchemy.orm import Session
from app.models.api_call import ApiCall
from app.schemas.api_call import ApiCallCreate
from typing import List, Optional

def create_api_call(db: Session, payload: ApiCallCreate) -> ApiCall:
    entry = ApiCall(**payload.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

def list_api_calls(
    db: Session,
    limit: int = 100,
    offset: int = 0,
    path: Optional[str] = None,
    method: Optional[str] = None,
) -> List[ApiCall]:
    q = db.query(ApiCall)
    if path:
        q = q.filter(ApiCall.path == path)
    if method:
        q = q.filter(ApiCall.method == method)
    return q.order_by(ApiCall.timestamp.desc()).offset(offset).limit(limit).all()

def count_calls_in_range(db: Session, start_ts, end_ts) -> int:
    return db.query(ApiCall).filter(
        ApiCall.timestamp >= start_ts,
        ApiCall.timestamp < end_ts
    ).count()
