from sqlalchemy.orm import Session
from app.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate

def create_user_role(db: Session, user_role: UserRoleCreate):
    db_user_role = UserRole(**user_role.dict())
    db.add(db_user_role)
    db.commit()
    db.refresh(db_user_role)
    return db_user_role

def get_user_role(db: Session, role_id: int):
    return db.query(UserRole).filter(UserRole.role_id == role_id).first()

def get_user_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserRole).offset(skip).limit(limit).all()

def update_user_role(db: Session, role_id: int, user_role: UserRoleCreate):
    db_user_role = db.query(UserRole).filter(UserRole.role_id == role_id).first()
    if db_user_role:
        for key, value in user_role.dict().items():
            setattr(db_user_role, key, value)
        db.commit()
        db.refresh(db_user_role)
    return db_user_role

def delete_user_role(db: Session, role_id: int):
    db_user_role = db.query(UserRole).filter(UserRole.role_id == role_id).first()
    if db_user_role:
        db.delete(db_user_role)
        db.commit()
    return db_user_role