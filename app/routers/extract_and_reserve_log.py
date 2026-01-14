
# app.py
import uuid
from datetime import datetime
from typing import Any, Dict, List

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from sqlalchemy import (
    Column,
    String,
    DateTime,
    func,
    text
)
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy.types import JSON
from app.database import get_db

Base = declarative_base()

# --- ORM model (maps to clientdb.extract_and_reserve_log) ---
class ExtractAndReserveLog(Base):
    __tablename__ = "extract_and_reserve_log"
    __table_args__ = {"schema": "clientdb"}

    # Keeping execution_id as PK for simplicity (generated in code as UUID)
    execution_id = Column(String(36), primary_key=True, index=True)
    workflow_id = Column(String(100), nullable=False)
    data_keys = Column(JSON, nullable=False)     # stores list of keys (strings)
    data_records = Column(JSON, nullable=False)  # stores list of dicts (dynamic)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_by = Column(String(100), nullable=False)


# --- Pydantic payload models ---
class ExtractAndReservePayload(BaseModel):
    workflow_id: constr(strip_whitespace=True)
    created_by: constr(strip_whitespace=True)
    data_records: List[Dict[str, Any]]

# --- FastAPI app & router ---
app = FastAPI(title="Extract and Reserve Info API", version="1.0.0")
router = APIRouter(prefix="/extract-and-reserve-log", tags=["Extract and Reserve Log"])


@router.post("/", summary="Save Extract and Reserve Log")
def save_extract_and_reserve_log(payload: ExtractAndReservePayload, db: Session = Depends(get_db)):
    """
    Saves a extract and reserve log into clientdb.extract_and_reserve_log.
    - Generates a new execution_id (uuid4).
    - Derives data_keys from union of keys in data_records.
    - Persists workflow_id, execution_id, data_keys, data_records, created_by.
    """

    dk_rows = db.execute(
        text("""
            SELECT source_column
            FROM clientdb.mining_workflow_output_criteria_1
            WHERE workflow_id = :wid
            AND is_parameter_flag = true
        """),
        {"wid": str(payload.workflow_id)},
    ).mappings().all()
    
    data_keys = [r["source_column"] for r in dk_rows]
    
    execution_id = str(uuid.uuid4())

    row = ExtractAndReserveLog(
        workflow_id=payload.workflow_id,
        execution_id=execution_id,
        data_keys=data_keys,
        data_records=payload.data_records,
        created_by=payload.created_by,
        # created_at will be set by DB default (server_default=func.now())
    )

    try:
        db.add(row)
        db.commit()
        db.refresh(row)
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB error: {exc}")

    return {
        "execution_id": execution_id,
        "workflow_id": payload.workflow_id,
        "inserted_count": len(payload.data_records),
        "created_at": row.created_at.isoformat() if row.created_at else datetime.utcnow().isoformat()
    }

@router.get("/", summary="Provide Extract and Reserve Log by workflow id")
def get_extract_and_reserve_log_by_workflow_id(workflow_id: str, db: Session = Depends(get_db)):
    logs = db.query(ExtractAndReserveLog).filter(ExtractAndReserveLog.workflow_id == workflow_id)
    for log in logs:
        breakpoint()
    if not logs:
        raise HTTPException(status_code=404, detail="Log not found")
    return [
        {
            "execution_id": log.execution_id,
            "workflow_id": log.workflow_id,
            "data_keys": log.data_keys,
            "data_records": log.data_records,
            "created_at": log.created_at,
            "created_by": log.created_by,
        }
        for log in logs
    ]
