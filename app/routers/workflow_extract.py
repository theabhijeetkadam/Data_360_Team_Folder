
# app/routers/workflow_extract.py
import logging
import json
import pandas as pd
from io import BytesIO
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field

from app.database import get_db

router = APIRouter(prefix="/workflow", tags=["Workflow Data"])
logger = logging.getLogger(__name__)

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

# --- Schemas used by this endpoint ---
class WorkflowSelection(BaseModel):
    data_key: str
    # UI provides the selected row as JSON fields; we will export these directly.
    field_values: Dict[str, Any] = Field(default_factory=dict)
    is_selected: bool = Field(default=False)        # first column checkbox on UI
    is_reserved: bool = Field(default=False)        # reserve checkbox on UI

class ExtractRequest(BaseModel):
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    environment_id: Optional[int] = None
    execution_id: Optional[str] = None
    selections: List[WorkflowSelection]

@router.post("/{workflow_id}/extract")
def extract_workflow_data(
    workflow_id: int,
    request: ExtractRequest,
    db: Session = Depends(get_db),
):
    start_ts = datetime.now()

    # 1) Filter only selected rows
    selected_rows = [s for s in request.selections if s.is_selected]
    if len(selected_rows) == 0:
        logger.info("Extract: no selected rows", extra={"workflow_id": workflow_id})
        raise HTTPException(status_code=400, detail="No rows selected to extract")

    # 2) Determine reserved subset
    reserved_rows = [s for s in selected_rows if s.is_reserved]
    reserved_count = len(reserved_rows)

    # 3) Build export rows directly from UI selections (NO DB fetch)
    export_rows: List[Dict[str, Any]] = []
    now = datetime.now()

    for s in selected_rows:
        # Ensure field_values is a dict; if UI mistakenly sends a string, parse JSON
        fv = s.field_values
        if isinstance(fv, str):
            try:
                fv = json.loads(fv)
            except Exception:
                fv = {}
        elif not isinstance(fv, dict):
            fv = {}

        export_rows.append({
            "workflow_id": workflow_id,
            "data_key": s.data_key,
            **fv
        })

    # 4) Create Excel in memory
    output = BytesIO()
    df = pd.DataFrame(export_rows)
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="SelectedData")
    output.seek(0)

    # 5) Insert only reserved rows into DB
    if reserved_count > 0:
        # Validate required identifiers for reservation
        if request.project_id is None:
            raise HTTPException(status_code=400, detail="project_id is required when reserving data")
        if request.module_id is None:
            raise HTTPException(status_code=400, detail="module_id is required when reserving data")
        if request.environment_id is None:
            raise HTTPException(status_code=400, detail="environment_id is required when reserving data")

        insert_sql = text("""
            INSERT INTO clientdb.extracted_data_table (
                project_id, module_id, environment_id, workflow_id, execution_id,
                source_table, data_key, field_values, is_reserved, reserved_at, extracted_at
            ) VALUES (
                :project_id, :module_id, :environment_id, :workflow_id, :execution_id,
                :source_table, :data_key, :field_values, :is_reserved, :reserved_at, :extracted_at
            )
        """)

        reserved_at = now
        inserted_count = 0

        for s in selected_rows:
            fv = s.field_values
            if isinstance(fv, str):
                try:
                    fv = json.loads(fv)
                except Exception:
                    fv = {}
            elif not isinstance(fv, dict):
                fv = {}

            params = {
                "project_id": request.project_id,
                "module_id": request.module_id,
                "environment_id": request.environment_id,
                "workflow_id": workflow_id,
                "execution_id": request.execution_id,
                # As per requirement: no source/canonical fetch; store an informational source label if needed.
                "source_table": "ui_selected_rows",
                "data_key": s.data_key,
                "field_values": json.dumps(fv, ensure_ascii=False),
                "is_reserved": True,
                "reserved_at": reserved_at,
                "extracted_at": now
            }
            db.execute(insert_sql, params)
            inserted_count += 1

        db.commit()
        logger.info("Extract: reservations committed", extra={
            "workflow_id": workflow_id,
            "reserved_count": inserted_count
        })

    # 6) Return Excel response regardless of reservation
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"selected_data_wf_{workflow_id}_{timestamp_str}.xlsx"
    headers = {"Content-Disposition": f'attachment; filename=\"{filename}\"'}

    elapsed_ms = int((datetime.now() - start_ts).total_seconds() * 1000)
    
    logger.info("Extract: success", extra={
    "workflow_id": workflow_id,
    "selected_count": len(selected_rows),
    "reserved_count": reserved_count,
    "elapsed_ms": elapsed_ms,
    "export_filename": filename,   # <-- renamed from 'filename'
    })


    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers
    )
