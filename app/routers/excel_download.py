from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse
import pandas as pd
from io import BytesIO
import json
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/export", tags=["Export"])

# Request model
class ExportRequest(BaseModel):
    workflow_id: int
    project_id: Optional[int] = None
    module_id: Optional[int] = None
    environment_id: Optional[int] = None
    execution_id: Optional[str] = None

def error_response(code: int, message: str):
    return {"code": str(code), "message": message}

@router.post("/reserved-data/")
def export_reserved_data(request: ExportRequest, db: Session = Depends(get_db)):
    try:
        # Base WHERE clause
        where_conditions = ["is_reserved = TRUE", "workflow_id = :workflow_id"]
        values = {"workflow_id": request.workflow_id}

        # Optional filters
        if request.project_id is not None:
            where_conditions.append("project_id = :project_id")
            values["project_id"] = request.project_id
        if request.module_id is not None:
            where_conditions.append("module_id = :module_id")
            values["module_id"] = request.module_id
        if request.environment_id is not None:
            where_conditions.append("environment_id = :environment_id")
            values["environment_id"] = request.environment_id
        if request.execution_id is not None:
            where_conditions.append("execution_id = :execution_id")
            values["execution_id"] = request.execution_id

        where_sql = " AND ".join(where_conditions)

        # SQLAlchemy execute
        query = f"""
            SELECT source_table, data_key, field_values, reserved_at, extracted_at
            FROM clientdb.extracted_data_table
            WHERE {where_sql}
        """
        result = db.execute(query, values)
        rows = result.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No reserved data found")

        # Convert rows into DataFrame
        data_list = []
        for row in rows:
            source_table, data_key, field_values, reserved_at, extracted_at = row

            # Ensure field_values is a dict
            if isinstance(field_values, str):
                try:
                    field_values_dict = json.loads(field_values)
                except:
                    field_values_dict = {}
            elif isinstance(field_values, dict):
                field_values_dict = field_values
            else:
                field_values_dict = {}

            # Convert timezone-aware datetimes to naive
            if reserved_at is not None and hasattr(reserved_at, "tzinfo"):
                reserved_at = reserved_at.replace(tzinfo=None)
            if extracted_at is not None and hasattr(extracted_at, "tzinfo"):
                extracted_at = extracted_at.replace(tzinfo=None)

            combined = {
                "source_table": source_table,
                "data_key": data_key,
                "reserved_at": reserved_at,
                "extracted_at": extracted_at,
                **field_values_dict
            }
            data_list.append(combined)

        df = pd.DataFrame(data_list)

        # Create Excel in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="ReservedData")
        output.seek(0)

        headers = {
            "Content-Disposition": "attachment; filename=reserved_data.xlsx"
        }

        return Response(
            content=output.read(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers=headers
        )

    except Exception as e:
        return JSONResponse(status_code=500, content=error_response(500, "Error Exporting data"))
