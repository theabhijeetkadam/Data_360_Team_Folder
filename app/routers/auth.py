
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserDetails

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Normalize username
    input_username = request.username.strip()

    # Fetch user
    user = db.query(User).filter(User.user_name == input_username).first()

    if not user or user.user_password != request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # ✅ Return only message and username
    return {
        "message": "Login successful",
        "username": input_username
    }

