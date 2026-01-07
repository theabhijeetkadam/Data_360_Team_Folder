
# app/routers/dashboard.py
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.project import Project            # project_table
from app.models.env import Environment            # env_details
from app.models.user import User                  # user_table
from app.models.api_call import ApiCall           # api_call_log

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db)):
    # 1) Active projects count (case-insensitive "active")
    active_project_count = (
        db.query(func.count(Project.project_id))
        .filter(func.lower(Project.status) == "active")
        .scalar()
        or 0
    )

    # 2) Environment count
    environment_count = (
        db.query(func.count(Environment.env_id))
        .scalar()
        or 0
    )

    # 3) Total user count
    total_user_count = (
        db.query(func.count(User.user_id))
        .scalar()
        or 0
    )

    # 4) API calls today (UTC day range)
    # Define UTC day boundaries: [00:00:00, 24:00:00)
    now_utc = datetime.utcnow()
    start_utc = datetime(now_utc.year, now_utc.month, now_utc.day, 0, 0, 0)
    end_utc = start_utc + timedelta(days=1)

    api_calls_today = (
        db.query(func.count(ApiCall.id))
        .filter(ApiCall.timestamp >= start_utc, ApiCall.timestamp < end_utc)
        .scalar()
        or 0
    )

    # 5) Last updated user's datetime (max updated_at)
    last_user_update_dt = db.query(func.max(User.updated_at)).scalar()
    last_user_update_iso = (
        last_user_update_dt.isoformat() if isinstance(last_user_update_dt, datetime) else None
    )

    return {
        "metrics": {
            "active_projects": active_project_count,
            "environments": environment_count,
            "api_calls_today": api_calls_today,
        },
        "users": {
            "total": total_user_count,
            "last_updated_at": last_user_update_iso  # e.g., "2026-01-06T10:52:14.123456"
        }
    }