from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import StatusCreate, StatusUpdate, StatusOut
from ..crud.status import create_status, get_status, get_all_status, update_status, delete_status

router = APIRouter(prefix="/status", tags=["Status"])

@router.post("/", response_model=StatusOut)
def create_status_endpoint(status: StatusCreate, db: Session = Depends(get_db)):
    return create_status(db, status)

@router.get("/{status_id}", response_model=StatusOut)
def get_status_endpoint(status_id: int, db: Session = Depends(get_db)):
    db_status = get_status(db, status_id)
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return db_status

@router.get("/", response_model=list[StatusOut])
def get_all_status_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_all_status(db, skip, limit)

@router.put("/{status_id}", response_model=StatusOut)
def update_status_endpoint(status_id: int, status: StatusUpdate, db: Session = Depends(get_db)):
    db_status = update_status(db, status_id, status)
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return db_status

@router.delete("/{status_id}")
def delete_status_endpoint(status_id: int, db: Session = Depends(get_db)):
    db_status = delete_status(db, status_id)
    if not db_status:
        raise HTTPException(status_code=404, detail="Status not found")
    return {"detail": "Status deleted successfully"}