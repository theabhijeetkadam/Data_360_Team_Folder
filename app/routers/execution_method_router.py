# app/routers/execution_method_router.py
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional
import os
import json
import ast
import re
import logging
import shutil
import requests
from datetime import datetime
from uuid import uuid4
from app.schemas import execution_method_schema

from app.database import get_db
from app.crud.execution_method_crud import (
    get_service_by_workflow_id,                 # for execution endpoint
    log_genrocket_service_execution,            # for execution logging
    get_execution_log_by_workflow_and_job       # for download endpoint
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["GenRocket Execution"])

SUPPORTED_EXTS = {".csv", ".xlsx", ".xls", ".json"}  # .xml is unsupported

# ------------------------- Common Helpers -----------------------------------

def _find_first_string_in_nested(obj: Any) -> Optional[str]:
    """Safely search any nested dict/list for the first string (e.g., a filename)."""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, dict):
        for v in obj.values():
            found = _find_first_string_in_nested(v)
            if found:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _find_first_string_in_nested(v)
            if found:
                return found
    return None

def _safe_parse_json(response: requests.Response) -> Dict[str, Any]:
    """Parse JSON body safely; raise a descriptive error for non-JSON responses."""
    try:
        return response.json()
    except ValueError as e:
        raise HTTPException(status_code=400, detail="The GenRocket file is not correct") from e

def _extract_filename(response_json: Dict[str, Any], scenario_name: str) -> Optional[str]:
    """
    Attempt to extract a filename from GenRocket response in a robust way.

    Expected:
        response_json["fileNameStore"][<scenario>][<Receiver>][0] -> "file.ext"
    """
    try:
        file_store = response_json.get("fileNameStore", {})
        scenario_block = file_store.get(scenario_name)
        if scenario_block:
            if isinstance(scenario_block, dict):
                for _receiver_name, maybe_list in scenario_block.items():
                    if isinstance(maybe_list, list) and maybe_list:
                        if isinstance(maybe_list[0], str):
                            return maybe_list[0]
                        found = _find_first_string_in_nested(maybe_list)
                        if found:
                            return found
                    found = _find_first_string_in_nested(maybe_list)
                    if found:
                        return found
            found = _find_first_string_in_nested(scenario_block)
            if found:
                return found
    except Exception as e:
        logger.warning(f"Filename extraction (scenario path) failed: {e}")

    try:
        file_store = response_json.get("fileNameStore")
        if file_store:
            found = _find_first_string_in_nested(file_store)
            if found:
                return found
    except Exception as e:
        logger.warning(f"Filename extraction (global fileNameStore) failed: {e}")

    return _find_first_string_in_nested(response_json)

def _validate_filename_or_raise(file_name: Optional[str]) -> str:
    """
    Validate presence and supported extension of file_name.
    Raises HTTPException with:
      - 400 "File Name not found"
      - 415 "Unsupported File format"
    """
    if not file_name or not isinstance(file_name, str) or file_name.strip() == "":
        raise HTTPException(status_code=400, detail="File Name not found")

    _, ext = os.path.splitext(file_name.strip().lower())

    if ext == ".xml":
        # Explicitly unsupported per requirement
        raise HTTPException(status_code=415, detail="Unsupported File format")

    if ext not in SUPPORTED_EXTS:
        raise HTTPException(status_code=415, detail="Unsupported File format")

    return file_name.strip()


def _guess_mime_type(filename: str) -> str:
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".csv":
        return "text/csv"
    if ext == ".json":
        return "application/json"
    if ext == ".xlsx":
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if ext == ".xls":
        return "application/vnd.ms-excel"
    return "application/octet-stream"


def get_file_path(base_path: str, file_name: str | None) -> Optional[str]:
    """Search the base path and subdirectories for the given file_name."""
    if not file_name:
        return None

    try:
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isfile(item_path) and item == file_name:
                return item_path
    except Exception as e:
        logger.warning(f"Base path listing failed: {e}")

    for root, _dirs, files in os.walk(base_path):
        if file_name in files:
            return os.path.join(root, file_name)

    return None

def _log_and_return_json_failure(
    db: Session,
    service,
    workflow_id: int,
    start_time: datetime,
    end_time: datetime,
    runtime,
    status_message: str,
    output_json: Dict[str, Any] | str,
    http_status: int,
) -> JSONResponse:
    """Utility to log FAILED status and return JSON error consistently."""
    log_genrocket_service_execution(
        db=db,
        tool_id=service.tool_id,
        tool_name="GenRocket",
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=service.username,
        status="FAILED",
        output_json=str(output_json),
    )
    return JSONResponse(status_code=http_status, content={"code": str(http_status), "message": status_message})

# unique destination per run (prevents overwrites)
def _build_unique_destination(base_path: str, workflow_id: int, scenario_name: str, original_name: str) -> str:
    base, ext = os.path.splitext(original_name)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    suffix = uuid4().hex[:6]
    dest_dir = os.path.join(base_path, "runs", str(workflow_id))
    os.makedirs(dest_dir, exist_ok=True)
    stem = (scenario_name or base).replace(" ", "_")
    unique_name = f"{stem}_{ts}_{suffix}{ext}"
    return os.path.join(dest_dir, unique_name)

# ------------------------- Helpers for download -----------------------------

def _extract_file_path_from_output_json_text(text: str) -> Optional[str]:
    """
    Robustly extract 'file_path' from output_json column, which may be stored as:
      - JSON string: {"api_response": {...}, "file_path": "C:\\path\\file.xlsx"}
      - Python dict string: {'api_response': {...}, 'file_path': 'C:\\path\\file.xlsx'}
      - Mixed/escaped content
    Returns the file_path or None if not found.
    """
    if not text or not isinstance(text, str):
        return None

    # Try JSON
    try:
        obj = json.loads(text)
        fp = obj.get("file_path")
        if isinstance(fp, str) and fp.strip():
            return fp.strip()
    except Exception:
        pass

    # Try Python literal
    try:
        obj = ast.literal_eval(text)
        if isinstance(obj, dict):
            fp = obj.get("file_path")
            if isinstance(fp, str) and fp.strip():
                return fp.strip()
    except Exception:
        pass

    # Regex fallback (supports "file_path": "..." and 'file_path': '...')
   
    m = re.search(r"""['"]file_path['"]\s*:\s*'"['"]""", text)
    if m:
         return m.group(1).strip()


    return None

def _validate_extension_or_raise_path(path: str) -> None:
    _, ext = os.path.splitext(path.strip().lower())
    if ext == ".xml":
        raise HTTPException(status_code=415, detail="Unsupported File format")
    if ext not in SUPPORTED_EXTS:
        raise HTTPException(status_code=415, detail="Unsupported File format")

# ---------------------- Download endpoint (NO re-execution) -----------------

@router.get("/execute-genrocket-service/{workflow_id}/jobs/{job_id}/download")
def download_genrocket_output(
    workflow_id: int,
    job_id: int,
    x_user_id: str = Header(..., description="User ID for authentication"),
    db: Session = Depends(get_db),
):
    """
    Streams the previously generated output file for the given (workflow_id, job_id).
    This endpoint DOES NOT call GenRocket; it reads the file path from the execution log.
    """
    # 1) Fetch execution log
    log_row = get_execution_log_by_workflow_and_job(db, workflow_id=workflow_id, job_id=job_id)
    if not log_row:
        raise HTTPException(status_code=404, detail="Execution log not found for given workflow_id and job_id")

    # 2) Validate status
    status_val = getattr(log_row, "status", None)
    if status_val and str(status_val).upper() != "SUCCESS":
        return JSONResponse(
            status_code=400,
            content={"code": "400", "message": f"Scenario Failed. Last status: {status_val}"}
        )

    # 3) Extract file_path from output_json
    output_json_text = getattr(log_row, "output_json", "") or ""
    file_path = _extract_file_path_from_output_json_text(output_json_text)
    if not file_path:
        raise HTTPException(status_code=400, detail="File path missing in execution log")

    # 4) Validate extension
    _validate_extension_or_raise_path(file_path)

    # 5) Check file exists
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail="Output file not found at recorded path (execution completed, but output file was not downloaded)"
        )

    # 6) Stream file
    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f

    content_type = _guess_mime_type(file_path)
    headers = {
        "Content-Disposition": f'attachment; filename="{os.path.basename(file_path)}"',
        "X-Execution-Message": "Download from previous run"
    }

    return StreamingResponse(iterfile(), media_type=content_type, headers=headers)

# ---------------------- Status-only endpoint (Execution) --------------------

@router.post("/execute-genrocket-service/{workflow_id}/status")
def execute_genrocket_service_status(
    workflow_id: int,
    x_user_id: str = Header(..., description="User ID for authentication"),
    db: Session = Depends(get_db),
):
    """
    Executes the workflow and returns only a minimal JSON status (no streaming).
    Creates a uniquely named copy to avoid overwriting and verifies its presence.
    """
    logger.info(f"Starting GenRocket execution (status only) for workflow_id={workflow_id}")

    # 1) Workflow existence
    service = get_service_by_workflow_id(db, workflow_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 2) Prepare payload
    payload = execution_method_schema.Genrocket_mirror_payload(
        username=service.username,
        password=service.password,
        clientAppId=service.clientappid,
        clientUserId=service.clientuserid,
        scenario=service.scenario,
        scenarioPath=service.scenariopath,
        keepFileName=service.keepfilename
    ).dict()

    # 3) Execute GenRocket
    start_time = datetime.utcnow()
    try:
        response = requests.post(
            "http://10.100.242.133:8088/rest/scenario",
            json=payload,
            timeout=600
        )
        response.raise_for_status()
        try:
            response_json = _safe_parse_json(response)
        except HTTPException as he:
            return _log_and_return_json_failure(
                db=db, service=service, workflow_id=workflow_id,
                start_time=start_time, end_time=datetime.utcnow(),
                runtime=datetime.utcnow() - start_time,
                status_message=he.detail,
                output_json={"payload": payload, "error": he.detail},
                http_status=400,
            )
        status = "SUCCESS"
    except requests.exceptions.RequestException as e:
        status = "FAILED"
        response_json = {"error": str(e)}

    end_time = datetime.utcnow()
    runtime = end_time - start_time

    # 4) Scenario failed
    if status != "SUCCESS":
        return JSONResponse(status_code=400, content={"code": "400", "message": "Scenario Failed"})

    # 5) Extract + validate filename
    scenario_name = service.scenario or ""
    raw_file_name = _extract_filename(response_json, scenario_name)
    try:
        file_name = _validate_filename_or_raise(raw_file_name)
    except HTTPException as he:
        return JSONResponse(status_code=he.status_code, content={"code": str(he.status_code), "message": he.detail})

    # 6) Check file presence
    base_path = r"C:\Shared_Folder\02 Tools\Genrocket Output"
    original_path = get_file_path(base_path, file_name) if file_name else None

    if not original_path or not isinstance(original_path, str) or not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Execution completed, but output file was not downloaded")

    # 7) Copy to unique destination to prevent overwrites
    dest_path = _build_unique_destination(base_path, workflow_id, scenario_name, file_name)
    try:
        shutil.copy2(original_path, dest_path)
    except Exception as e:
        logger.error(f"Copy to unique destination failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create unique output copy")

    # 8) Log execution with unique path
    output_json = {"api_response": response_json, "file_path": dest_path}
    log_genrocket_service_execution(
        db=db,
        tool_id=service.tool_id,
        tool_name="GenRocket",
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=service.username,
        status="SUCCESS",
        output_json=str(output_json),
    )

    # 9) Return success
    return JSONResponse(status_code=200, content={"code": "200 OK", "message": "Execution successful"})