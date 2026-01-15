from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import runtime_logs as schemas
from app.crud import runtime_logs as crud

router = APIRouter(
    prefix="/runtime-logs",
    tags=["Runtime Logs"]
)

@router.post("/", response_model=schemas.RuntimeLogResponse)
def create_runtime_log(log: schemas.RuntimeLogCreate, db: Session = Depends(get_db)):
    return crud.create_runtime_log(db, log)

@router.get("/", response_model=list[schemas.RuntimeLogResponse])
def get_all_runtime_logs(db: Session = Depends(get_db)):
    return crud.get_all_runtime_logs(db)

@router.get("/{execution_id}", response_model=schemas.RuntimeLogResponse)
def get_runtime_log(execution_id: int, db: Session = Depends(get_db)):
    db_log = crud.get_runtime_log_by_id(db, execution_id)
    if not db_log:
        raise HTTPException(status_code=404, detail="Runtime log not found")
    return db_log

@router.put("/{execution_id}", response_model=schemas.RuntimeLogResponse)
def update_runtime_log(execution_id: int, log: schemas.RuntimeLogUpdate, db: Session = Depends(get_db)):
    updated = crud.update_runtime_log(db, execution_id, log)
    if not updated:
        raise HTTPException(status_code=404, detail="Runtime log not found")
    return updated

@router.delete("/{execution_id}")
def delete_runtime_log(execution_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_runtime_log(db, execution_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Runtime log not found")
    return {"message": "Runtime log deleted successfully"}
