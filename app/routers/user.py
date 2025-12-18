
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user import UserCreate
from app.models import User
from app.crud.user import (
    create_user, get_user, get_users,
    update_user, delete_user
)
from app.exceptions import (
    DuplicateEntryError, DBInsertError, DBUpdateError, DBDeleteError
)

router = APIRouter(prefix="/User_Management_Module", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Convert SQLAlchemy object to dict
def to_dict(obj):
    return {column.name: getattr(obj, column.name) for column in obj.__table__.columns}

# ✅ Error response helper
def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.post("/", response_model=dict)
def create(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if not user.status:
            user.status = "ACTIVE"
        db_user = create_user(db, user)
        return {"message": "User created successfully.", "data": to_dict(db_user), "code": "200"}
    except DuplicateEntryError as e:
        return error_response(409, e.message)
    except DBInsertError as e:
        return error_response(400, e.message or "Insert failed")
    except Exception as e:
        return error_response(500, f"Unexpected error: {str(e)}")

@router.get("/{user_id}", response_model=dict)
def read(user_id: int, db: Session = Depends(get_db)):
    try:
        db_user = get_user(db, user_id)
        if not db_user:
            return error_response(404, "User not found")
        return {"message": "User details retrieved successfully.", "data": to_dict(db_user), "code": "200"}
    except Exception as e:
        return error_response(500, f"Unexpected error: {str(e)}")

@router.get("/", response_model=dict)
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        users = get_users(db, skip, limit)
        return {"message": "User list retrieved successfully.", "data": [to_dict(u) for u in users], "code": "200"}
    except Exception as e:
        return error_response(500, f"Unexpected error: {str(e)}")

@router.put("/{user_id}", response_model=dict)
def update(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = update_user(db, user_id, user)
        if not db_user:
            return error_response(404, "Resource to update not found")
        return {"message": "User updated successfully.", "data": to_dict(db_user), "code": "200"}
    except DuplicateEntryError as e:
        return error_response(409, e.message)
    except DBUpdateError as e:
        return error_response(400, e.message or "Update failed")
    except Exception as e:
        return error_response(500, f"Unexpected error: {str(e)}")

@router.delete("/{user_id}", response_model=dict)
def delete(user_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        # Fetch X-User-Id from header
        x_user_id = request.headers.get("X-User-Id")
        deleted_by_userid = int(x_user_id) if x_user_id else 0

        # Fetch username from DB using user_id
        deleted_by_username = "system"
        if deleted_by_userid:
            user = db.query(User).filter(User.user_id == deleted_by_userid).first()
            if user:
                deleted_by_username = user.emp_name

        # Perform delete with logging
        db_user = delete_user(db, user_id, deleted_by_userid, deleted_by_username)
        if not db_user:
            return error_response(404, "Resource to delete not found")

        return {"message": "User deleted successfully.", "data": db_user, "code": "200"}
    except DBDeleteError as e:
        return error_response(400, e.message or "Delete failed")
    except Exception as e:
        return error_response(500, f"Unexpected error: {str(e)}")
