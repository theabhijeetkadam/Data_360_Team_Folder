from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import db_workflow_deleted_logs as schemas
from app.crud import db_workflow_deleted_logs as crud

router = APIRouter(
    prefix="/db workflow_deleted_logs",
    tags=["DB Workflow Deleted Logs"]
)

@router.post("/", response_model=schemas.DeletedLogResponse)
def create_deleted_log(log: schemas.DeletedLogCreate, db: Session = Depends(get_db)):
    return crud.create_deleted_log(db, log)
