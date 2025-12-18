
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.models.deletelog import DeleteLog
from datetime import datetime
from app.models.user_role import UserRole
from app.schemas.user import UserCreate
from app.exceptions import (
    DuplicateEntryError, DBInsertError, DBReadError,
    DBUpdateError, DBDeleteError
)

# ✅ Validate role_id and user_role consistency
def validate_role(db: Session, role_id: int, user_role: str):
    role = db.query(UserRole).filter(UserRole.role_name == user_role).first()
    if not role:
        raise DBInsertError(message=f"Invalid role name: {user_role}")
    if role_id != role.role_id:
        raise DBInsertError(message=f"Role ID mismatch for '{user_role}'. Expected {role.role_id}")
    return True

def create_user(db: Session, user: UserCreate):
    try:
        if db.query(User).filter(User.user_emp_id == user.user_emp_id).first():
            raise DuplicateEntryError(message="Employee ID already in use")

        validate_role(db, user.role_id, user.user_role)

        db_user = User(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except (DuplicateEntryError, DBInsertError):
        raise
    except IntegrityError:
        db.rollback()
        raise DuplicateEntryError(message="Duplicate entry detected")
    except Exception as e:
        db.rollback()
        raise DBInsertError(message=f"Unexpected DB error: {str(e)}")

def get_user(db: Session, user_id: int):
    try:
        return db.query(User).filter(User.user_id == user_id).first()
    except Exception:
        raise DBReadError(message="DB operation failed while reading user")

def get_user_by_username(db: Session, username: str):
    try:
        # normalize input
        username = (username or "").strip()
        if not username:
            return None
        # Case-insensitive equality (no wildcards)
        return db.query(User).filter(User.user_name.ilike(username)).first()
        # If you want strict equality instead, use:
        # return db.query(User).filter(User.username == username).first()
    except Exception as e:
        raise DBReadError(message=f"DB operation failed while reading user by username: {str(e)}")

def get_users(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(User).offset(skip).limit(limit).all()
    except Exception:
        raise DBReadError(message="DB operation failed while reading users")

def update_user(db: Session, user_id: int, user: UserCreate):
    try:
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return None

        if db.query(User).filter(User.user_emp_id == user.user_emp_id, User.user_id != user_id).first():
            raise DuplicateEntryError(message="Employee ID already in use")

        validate_role(db, user.role_id, user.user_role)
        db_user.status = user.status
        for key, value in user.dict().items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    except (DuplicateEntryError, DBInsertError):
        raise
    except Exception as e:
        db.rollback()
        raise DBUpdateError(message=f"Unexpected DB error: {str(e)}")

# ✅ Delete user with logging
def delete_user(db: Session, user_id: int, deleted_by_userid: int, deleted_by_username: str):
    try:
        db_user = db.query(User).filter(User.user_id == user_id).first()
        if not db_user:
            return None

        # Capture details before deletion
        deleted_data = {col.name: getattr(db_user, col.name) for col in db_user.__table__.columns}

        # Delete user
        db.delete(db_user)
        db.commit()

        # Log deletion
        log = DeleteLog(
            deleted_by_userid=deleted_by_userid,
            deleted_by_username=deleted_by_username,
            deleted_date=datetime.utcnow().date(),
            deleted_time=datetime.utcnow().time(),
            module_name="User_Management_Module",
            record_id=user_id
        )
        db.add(log)
        db.commit()

        return deleted_data
    except IntegrityError:
        db.rollback()
        raise DBDeleteError(message="Resource is in use (FK constraint)")
    except Exception as e:
        db.rollback()
        raise DBDeleteError(message=f"DB operation failed while deleting user: {str(e)}")
