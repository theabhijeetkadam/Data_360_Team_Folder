
# app/middleware/api_call_logging.py
from datetime import datetime
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.api_call import ApiCall

class ApiCallLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Skip docs/static routes
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc") \
           or request.url.path.startswith("/openapi.json") or request.url.path.startswith("/static"):
            return response

        db: Session = SessionLocal()
        try:
            entry = ApiCall(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                timestamp=datetime.utcnow(),  # store as UTC
                user_id=getattr(request.state, "user_id", None)  # if you set it elsewhere
            )
            db.add(entry)
            db.commit()
        except Exception:
            db.rollback()
            # Don't break the request; keep logging best-effort
        finally:
            db.close()

        return response
