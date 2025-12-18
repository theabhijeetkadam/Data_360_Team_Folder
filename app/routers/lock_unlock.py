from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import JSONResponse
from app.database import SessionLocal
#from app.database import get_db
from app.models.lock_unlock import ExtractedData
from app.schemas.lock_unlock import UnreserveRequest

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
router = APIRouter(prefix="/unreserve", tags=["Unreserve Data"])

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.put("/data/")
def unreserve_data(request: UnreserveRequest, db: Session = Depends(get_db)):
    try:
        if request.execution_id:
            rows = db.query(ExtractedData).filter(ExtractedData.execution_id.in_(request.execution_id)).all()
        else:
            # Bulk unreserve all reserved records
            rows = db.query(ExtractedData).filter(ExtractedData.is_reserved == True).all()

        if not rows:
            return {"message": "No records found to unreserve"}

        for row in rows:
            row.is_reserved = False
            row.updated_by = request.updated_by
            row.updated_at = datetime.utcnow()

        db.commit()
        return {"message": f"Unreserved {len(rows)} records successfully"}

    except Exception as e:
        return JSONResponse(status_code=400, content=error_response(400, str(e)))
