from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas import execution_logs as schemas
from app.crud import execution_logs as crud
from app.database import get_db

router = APIRouter(prefix="/execution-logs", tags=["Execution Logs"])

@router.post("/", response_model=schemas.ExecutionLogOut)
def create_log(log: schemas.ExecutionLogCreate, db: Session = Depends(get_db)):
    return crud.create_execution_log(db, log)

@router.get("/", response_model=List[schemas.ExecutionLogOut])
def read_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_execution_logs(db, skip=skip, limit=limit)

@router.get("/{execution_id}", response_model=schemas.ExecutionLogOut)
def read_log(execution_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_execution_log(db, execution_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    return db_log

@router.put("/{execution_id}", response_model=schemas.ExecutionLogOut)
def update_log(execution_id: int, log: schemas.ExecutionLogUpdate, db: Session = Depends(get_db)):
    db_log = crud.update_execution_log(db, execution_id, log)
    if not db_log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    return db_log

@router.delete("/{execution_id}", response_model=schemas.ExecutionLogOut)
def delete_log(execution_id: int, db: Session = Depends(get_db)):
    db_log = crud.delete_execution_log(db, execution_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Execution log not found")
    return db_log
