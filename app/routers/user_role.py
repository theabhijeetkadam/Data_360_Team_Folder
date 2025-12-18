from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user_role import UserRole, UserRoleCreate
from app import schemas
from app import crud
from app.crud.user_role import (
    create_user_role, get_user_role, get_user_roles,
    update_user_role, delete_user_role
)

router = APIRouter(prefix="/user_roles", tags=["User Roles"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserRole)
def create(role: UserRoleCreate, db: Session = Depends(get_db)):
    return create_user_role(db, role)

@router.get("/{role_id}", response_model=UserRole)
def read(role_id: int, db: Session = Depends(get_db)):
    db_role = get_user_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.get("/", response_model=list[UserRole])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_user_roles(db, skip, limit)

@router.put("/{role_id}", response_model=UserRole)
def update(role_id: int, role: UserRoleCreate, db: Session = Depends(get_db)):
    db_role = update_user_role(db, role_id, role)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/{role_id}", response_model=UserRole)
def delete(role_id: int, db: Session = Depends(get_db)):
    db_role = delete_user_role(db, role_id)
    if not db_role:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role