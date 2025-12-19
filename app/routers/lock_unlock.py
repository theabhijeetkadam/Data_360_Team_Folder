# ...existing code...
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
        # If specific execution_ids supplied, fetch those rows (not only reserved) so we can detect already-unreserved
        if request.execution_id:
             rows = db.query(ExtractedData).filter(ExtractedData.execution_id.in_(request.execution_id)).all()

             if not rows:
                return {"message": "No records found to unreserve"}

            # detect any already-unreserved records and return a clear message before any RBAC/other checks
             already_unreserved = [r.execution_id for r in rows if not r.is_reserved]
             if already_unreserved:
                # if multiple, list them; otherwise single message
                ids_display = ", ".join(map(str, already_unreserved))
                raise HTTPException(status_code=400, detail=f"Record(s) already unreserved: {ids_display}")

        else:
            # Bulk unreserve all currently reserved records
            rows = db.query(ExtractedData).filter(ExtractedData.is_reserved == True).all()
            if not rows:
                return {"message": "No records found to unreserve"}

        for row in rows:
            row.is_reserved = False
            row.updated_by = request.updated_by
            row.updated_at = datetime.utcnow()

        db.commit()
        return {"message": f"Unreserved {len(rows)} records successfully"}

    except HTTPException:
        # re-raise HTTPExceptions so FastAPI handles them as intended
        raise
    except Exception as e:
        return JSONResponse(status_code=400, content=error_response(400, str(e)))
# ...existing code...