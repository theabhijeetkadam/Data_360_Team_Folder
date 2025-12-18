from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import db_orchestration_execution_logs as schemas
from app.crud import db_orchestration_execution_logs as crud

router = APIRouter(
    prefix="/db orchestration execution_logs",
    tags=["DB Orchestration Execution Logs"]
)

@router.post("/", response_model=schemas.ExecutionLogResponse)
def create_execution_log(log: schemas.ExecutionLogCreate, db: Session = Depends(get_db)):
    return crud.create_execution_log(db, log)
