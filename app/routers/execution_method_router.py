from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import requests
from datetime import datetime
import os
import logging
from typing import Any, Dict, Optional, List
from app.schemas import execution_method_schema
from app.crud.execution_method_crud import get_service_by_workflow_id, log_genrocket_service_execution
from app.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Helpers ---------------------------------------------------------------

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

def _extract_filename(response_json: Dict[str, Any], scenario_name: str) -> Optional[str]:
    """
    Attempt to extract a filename from GenRocket response in a robust way.

    Expected patterns seen so far:
    response_json["fileNameStore"][<scenario>][<Receiver>][0] -> "file.ext"
    But we avoid hardcoding Receiver names and fall back to scanning.
    """
    # 1) Preferred: scenario-specific lookup
    try:
        file_store = response_json.get("fileNameStore", {})
        scenario_block = file_store.get(scenario_name)
        if scenario_block:
            # scenario_block may be: { "DelimitedFileReceiver": ["a.csv"], "XlsxFileReceiver": ["b.xlsx"] }
            # Iterate receivers and pick the first filename string.
            if isinstance(scenario_block, dict):
                for _receiver_name, maybe_list in scenario_block.items():
                    # values are often lists; get first string
                    if isinstance(maybe_list, list) and maybe_list:
                        if isinstance(maybe_list[0], str):
                            return maybe_list[0]
                        # If nested, try to scan
                        found = _find_first_string_in_nested(maybe_list)
                        if found:
                            return found
                    # If dict or nested deep
                    found = _find_first_string_in_nested(maybe_list)
                    if found:
                        return found
            # If block isn't dict, still scan
            found = _find_first_string_in_nested(scenario_block)
            if found:
                return found
    except Exception as e:
        logger.warning(f"Filename extraction (scenario path) failed: {e}")

    # 2) Fallback: scan entire fileNameStore
    try:
        file_store = response_json.get("fileNameStore")
        if file_store:
            found = _find_first_string_in_nested(file_store)
            if found:
                return found
    except Exception as e:
        logger.warning(f"Filename extraction (global fileNameStore) failed: {e}")

    # 3) Ultimate fallback: scan full response
    return _find_first_string_in_nested(response_json)

def _guess_mime_type(filename: str) -> str:
    """Return an appropriate Content-Type from the file extension."""
    ext = os.path.splitext(filename.lower())[1]
    if ext in (".csv",):
        return "text/csv"
    if ext in (".xlsx",):
        return "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    if ext in (".xls",):
        return "application/vnd.ms-excel"
    if ext in (".json",):
        return "application/json"
    if ext in (".txt",):
        return "text/plain"
    # fallback: binary stream
    return "application/octet-stream"

# --- Endpoint --------------------------------------------------------------

def get_file_path(base_path, file_name): 
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isfile(item_path) and item == file_name:
            return item_path
 
    for root, dirs, files in os.walk(base_path):
        if file_name in files:
            return os.path.join(root, file_name)
    return None        
    
@router.post("/execute-genrocket-service/{workflow_id}")
def execute_genrocket_service(
    workflow_id: int,
    x_user_id: str = Header(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    logger.info(f"Starting GenRocket execution for workflow_id={workflow_id}")

    # Fetch service details
    service = get_service_by_workflow_id(db, workflow_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Prepare payload sent to GenRocket
    payload = execution_method_schema.Genrocket_mirror_payload(
        username=service.username,
        password=service.password,
        clientAppId=service.clientappid,
        clientUserId=service.clientuserid,
        scenario=service.scenario,         # e.g., "TestExecutionScenario"
        scenarioPath=service.scenariopath, # e.g., "C:\\Shared_Folder\\02 Tools\\Genrocket Output\\Scenarios"
        keepFileName=service.keepfilename
    ).dict()

    # Execute and time it
    start_time = datetime.utcnow()
    try:
        # NOTE: if this host/port changes per env, move to config
        response = requests.post("http://10.100.242.133:8088/rest/scenario", json=payload, timeout=600)
        response.raise_for_status()
        status = "SUCCESS"
        response_json = response.json()
        logger.info(f"GenRocket API response: {response_json}")
    except requests.exceptions.RequestException as e:
        status = "FAILED"
        response_json = {"error": str(e)}
        logger.error(f"GenRocket API call failed: {e}")

    end_time = datetime.utcnow()
    runtime = end_time - start_time

    # Extract filename without hardcoding scenario/receiver names
    file_name: Optional[str] = None
    if status == "SUCCESS":
        # Prefer the exact scenario name given to GenRocket
        scenario_name = service.scenario or ""
        file_name = _extract_filename(response_json, scenario_name)
        logger.info(f"Extracted file name: {file_name}")

    if not file_name:
        # Log and store diagnostics for quick troubleshooting
        diag = {
            "payload": payload,
            "response": response_json,
            "hint": "Expected response_json['fileNameStore'][<scenario>][<Receiver>][0] containing a filename"
        }
        # Log the execution with failure status for traceability
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
            output_json=str(diag)
        )
        raise HTTPException(status_code=400, detail="File name not found in GenRocket response")

    # Resolve full file path (Windows-safe join)
    base_path = r"C:\Shared_Folder\02 Tools\Genrocket Output"
    file_path = get_file_path(base_path, file_name) if file_name else None
    #file_path = os.path.join(base_path, file_name)
    logger.info(f"Resolved file path: {file_path}")

    # Persist execution log
    output_json = {"api_response": response_json, "file_path": file_path}
    log_genrocket_service_execution(
        db=db,
        tool_id=service.tool_id,
        tool_name="GenRocket",
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=service.username,
        status=status,
        output_json=str(output_json)
    )

    # If scenario failed, return JSON (no streaming)
    if status != "SUCCESS":
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "message": "Scenario Failed",
                "error": response_json.get("error", "Unknown error")
            }
        )

    # Verify the file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found at {file_path}")

    # Stream response with appropriate Content-Type based on extension
    def iterfile():
        with open(file_path, mode="rb") as f:
            yield from f

    content_type = _guess_mime_type(file_name)
    headers = {"Content-Disposition": f'attachment; filename="{os.path.basename(file_name)}"'}

    return StreamingResponse(iterfile(), media_type=content_type, headers=headers)


@router.post("/execute-genrocket-service/{workflow_id}/status")
def execute_genrocket_service_status(
    workflow_id: int,
    x_user_id: str = Header(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    """
    Executes the workflow and returns only a minimal JSON status.
    - 404: Workflow not found
    - 200 OK: Execution successful
    - 400: Scenario failed or filename not found
    """
    logger.info(f"Starting GenRocket execution (status only) for workflow_id={workflow_id}")

    # Fetch service details (same as download endpoint)
    service = get_service_by_workflow_id(db, workflow_id)
    if not service:
        # Exactly as requested: explicit 404 when workflow id not found
        raise HTTPException(status_code=404, detail="Service not found")

    # Prepare payload (same as download endpoint)
    payload = execution_method_schema.Genrocket_mirror_payload(
        username=service.username,
        password=service.password,
        clientAppId=service.clientappid,
        clientUserId=service.clientuserid,
        scenario=service.scenario,         # e.g., "TestExecutionScenario"
        scenarioPath=service.scenariopath, # e.g., "C:\\Shared_Folder\\02 Tools\\Genrocket Output\\Scenarios"
        keepFileName=service.keepfilename
    ).dict()

    # Execute and time it (same flow)
    start_time = datetime.utcnow()
    try:
        response = requests.post("http://10.100.242.133:8088/rest/scenario", json=payload, timeout=600)
        response.raise_for_status()
        status = "SUCCESS"
        response_json = response.json()
        logger.info(f"GenRocket API response: {response_json}")
    except requests.exceptions.RequestException as e:
        status = "FAILED"
        response_json = {"error": str(e)}
        logger.error(f"GenRocket API call failed: {e}")

    end_time = datetime.utcnow()
    runtime = end_time - start_time

    # Extract filename (same helper as existing endpoint)
    file_name: Optional[str] = None
    if status == "SUCCESS":
        scenario_name = service.scenario or ""
        file_name = _extract_filename(response_json, scenario_name)
        logger.info(f"Extracted file name: {file_name}")

    # Persist execution details (kept consistent with existing endpoint)
    base_path = r"C:\Shared_Folder\02 Tools\Genrocket Output"
    file_path = get_file_path(base_path, file_name) if file_name else None
    #file_path = os.path.join(base_path, file_name) if file_name else None
    output_json = {"api_response": response_json, "file_path": file_path}
    log_genrocket_service_execution(
        db=db,
        tool_id=service.tool_id,
        tool_name="GenRocket",
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=service.username,
        status=status,
        output_json=str(output_json)
    )

    # Minimal status-only responses (no streaming, no extra content)
    if status != "SUCCESS":
        return JSONResponse(status_code=400, content={
            "code": "400",
            "message": "Scenario Failed"
        })

    if not file_name:
        return JSONResponse(status_code=400, content={
            "code": "400",
            "message": "File name not found in GenRocket response"
        })

    return JSONResponse(status_code=200, content={
        "code": "200 OK",
        "message": "Execution successful"
    })

@router.post("/execute-genrocket-service/{workflow_id}/status")
def execute_genrocket_service_status(
    workflow_id: int,
    x_user_id: str = Header(..., description="User ID for authentication"),
    db: Session = Depends(get_db)
):
    """
    Executes the workflow and returns only a minimal JSON status.
    - 404: Workflow not found
    - 200 OK: Execution successful (only if file exists)
    - 400: Scenario failed or filename not found
    """
    logger.info(f"Starting GenRocket execution (status only) for workflow_id={workflow_id}")

    # 1) Workflow existence
    service = get_service_by_workflow_id(db, workflow_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # 2) Prepare payload (same as download endpoint)
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
        response = requests.post("http://10.100.242.133:8088/rest/scenario", json=payload, timeout=600)
        response.raise_for_status()
        status = "SUCCESS"
        response_json = response.json()
        logger.info(f"GenRocket API response: {response_json}")
    except requests.exceptions.RequestException as e:
        status = "FAILED"
        response_json = {"error": str(e)}
        logger.error(f"GenRocket API call failed: {e}")

    end_time = datetime.utcnow()
    runtime = end_time - start_time

    # 4) Extract filename same way
    file_name: Optional[str] = None
    if status == "SUCCESS":
        scenario_name = service.scenario or ""
        file_name = _extract_filename(response_json, scenario_name)
        logger.info(f"Extracted file name: {file_name}")

    # 5) Log execution (same as download endpoint)
    base_path = r"C:\Shared_Folder\02 Tools\Genrocket Output"
    file_path = get_file_path(base_path, file_name) if file_name else None
    #file_path = os.path.join(base_path, file_name) if file_name else None
    output_json = {"api_response": response_json, "file_path": file_path}
    log_genrocket_service_execution(
        db=db,
        tool_id=service.tool_id,
        tool_name="GenRocket",
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=service.username,
        status=status,
        output_json=str(output_json)
    )

    # 6) Return minimal status, aligned with stream endpoint behavior
    if status != "SUCCESS":
        return JSONResponse(status_code=400, content={
            "code": "400",
            "message": "Scenario Failed"
        })

    if not file_name:
        return JSONResponse(status_code=400, content={
            "code": "400",
            "message": "File name not found in GenRocket response"
        })

    # ✅ Ensure consistency: require the file to exist for success
    if not os.path.exists(file_path):
        # Mirror the semantics of the stream endpoint
        raise HTTPException(status_code=404, detail=f"File not found at {file_path}")

    return JSONResponse(status_code=200, content={
        "code": "200 OK",
        "message": "Execution successful"
    })
