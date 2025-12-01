from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.crud.governance_delete_logs import create_log, get_logs, get_log, update_log, delete_log
from app.schemas.governance_delete_logs import GovernanceDeleteLogCreate, GovernanceDeleteLog, GovernanceDeleteLogUpdate
from app.database import get_db

router = APIRouter(prefix="/governance-delete-logs", tags=["Governance Delete Logs"])

@router.get("/", response_model=List[GovernanceDeleteLog])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_logs(db, skip=skip, limit=limit)

@router.get("/{log_id}", response_model=GovernanceDeleteLog)
def read_log(log_id: int, db: Session = Depends(get_db)):
    db_log = get_log(db, log_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

@router.post("/", response_model=GovernanceDeleteLog)
def create_new_log(log: GovernanceDeleteLogCreate, db: Session = Depends(get_db)):
    return create_log(db, log)

@router.put("/{log_id}", response_model=GovernanceDeleteLog)
def update_existing_log(log_id: int, log: GovernanceDeleteLogUpdate, db: Session = Depends(get_db)):
    db_log = update_log(db, log_id, log)
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

@router.delete("/{log_id}", response_model=GovernanceDeleteLog)
def delete_existing_log(log_id: int, db: Session = Depends(get_db)):
    db_log = delete_log(db, log_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log
