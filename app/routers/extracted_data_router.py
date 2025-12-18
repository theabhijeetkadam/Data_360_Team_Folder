
# app/routers/save_selected_data.py
import logging
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.schemas.extracted_data_schema import SaveSelectionRequest
from app.database import get_db

router = APIRouter(prefix="/save-selected-data", tags=["Extracted Data"])

logger = logging.getLogger(__name__)

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

def _safe_preview(items, n=2) -> str:
    try:
        return json.dumps(items[:n], ensure_ascii=False)
    except Exception:
        return f"<preview unavailable; len={len(items)}>"

@router.post("/")
def save_selected_data(request: SaveSelectionRequest, db: Session = Depends(get_db)):
    start_ts = datetime.now()

    # Filter only reserved rows
    reserved_rows = [row for row in request.selections if getattr(row, "is_reserved", False)]

    logger.info(
        "SaveSelectedData: request received",
        extra={
            "project_id": request.project_id,
            "module_id": request.module_id,
            "environment_id": request.environment_id,
            "workflow_id": request.workflow_id,
            "execution_id": request.execution_id,
            "total_rows": len(request.selections),
            "reserved_rows": len(reserved_rows),
            "preview": _safe_preview([{
                "source_table": r.source_table,
                "data_key": r.data_key,
                "is_reserved": r.is_reserved
            } for r in reserved_rows])
        }
    )

    # If nothing to reserve, return success with zero saved (or change to 400 if desired)
    if len(reserved_rows) == 0:
        elapsed_ms = int((datetime.now() - start_ts).total_seconds() * 1000)
        logger.info(
            "SaveSelectedData: no reserved rows to insert",
            extra={"elapsed_ms": elapsed_ms}
        )
        return {"status": "success", "message": "0 rows saved."}

    try:
        # Prepared insert statement (parameterized)
        insert_sql = text("""
            INSERT INTO clientdb.extracted_data_table (
                project_id, module_id, environment_id, workflow_id, execution_id,
                source_table, data_key, field_values, is_reserved, reserved_at, extracted_at
            ) VALUES (
                :project_id, :module_id, :environment_id, :workflow_id, :execution_id,
                :source_table, :data_key, :field_values, :is_reserved, :reserved_at, :extracted_at
            )
        """)

        now = datetime.now()
        inserted_count = 0

        for row in reserved_rows:
            params = {
                "project_id": request.project_id,
                "module_id": request.module_id,
                "environment_id": request.environment_id,
                "workflow_id": request.workflow_id,
                "execution_id": request.execution_id,
                "source_table": row.source_table,
                "data_key": row.data_key,
                "field_values": json.dumps(row.field_values, ensure_ascii=False),
                "is_reserved": True,          # ✅ force true to be explicit
                "reserved_at": now,           # ✅ only for reserved rows
                "extracted_at": now
            }
            db.execute(insert_sql, params)
            inserted_count += 1

        db.commit()

        elapsed_ms = int((datetime.now() - start_ts).total_seconds() * 1000)
        logger.info(
            "SaveSelectedData: insert committed",
            extra={
                "inserted_count": inserted_count,
                "elapsed_ms": elapsed_ms,
            }
        )
        return {"status": "success", "message": f"{inserted_count} rows saved."}

    except Exception as e:
        db.rollback()
        elapsed_ms = int((datetime.now() - start_ts).total_seconds() * 1000)
        logger.exception(
            "SaveSelectedData: DB error, rolled back",
            extra={
                "elapsed_ms": elapsed_ms,
                "project_id": request.project_id,
                "module_id": request.module_id,
                "environment_id": request.environment_id,
                "workflow_id": request.workflow_id,
                "execution_id": request.execution_id,
            }
        )
        return JSONResponse(status_code=500, content=error_response(500, "DB error"))
