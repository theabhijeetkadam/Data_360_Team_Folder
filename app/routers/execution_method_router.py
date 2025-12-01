from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import requests
from datetime import datetime
import os
import logging
from app.schemas import execution_method_schema
from app.crud.execution_method_crud import get_service_by_workflow_id, log_genrocket_service_execution
from app.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/execute-genrocket-service/{workflow_id}")
def execute_genrocket_service(workflow_id: int, x_user_id: str = Header(..., description="User ID for authentication"), db: Session = Depends(get_db)):
    logger.info(f"Starting GenRocket execution for workflow_id={workflow_id}")

    # Fetch service details
    service = get_service_by_workflow_id(db, workflow_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Prepare payload
    payload = execution_method_schema.Genrocket_mirror_payload(
        username=service.username,
        password=service.password,
        clientAppId=service.clientappid,
        clientUserId=service.clientuserid,
        scenario=service.scenario,
        scenarioPath=service.scenariopath,
        keepFileName=service.keepfilename
    ).dict()

    start_time = datetime.utcnow()
    try:
        response = requests.post("http://10.100.242.133:8088/rest/scenario", json=payload)
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

    # Extract file name from nested response
    
    file_name = None
    if status == "SUCCESS":
        try:
            file_name = response_json.get("fileNameStore", {}) \
            .get("TestScenario", [{}])[0] \
            .get("DelimitedFileReceiver", [None])[0]
            logger.info(f"Extracted file name: {file_name}")
        except Exception as e:
            logger.error(f"Failed to extract file name: {e}")

    if not file_name:
        raise HTTPException(status_code=400, detail="File name not found in GenRocket response")

    # Build full file path
    base_path = r"C:\Shared_Folder\02 Tools\Genrocket Output"
    file_path = os.path.join(base_path, file_name)
    logger.info(f"Resolved file path: {file_path}")

    # Log execution details
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

    # If scenario failed, return JSON response
    if status != "SUCCESS":
        return {
            "success": False,
            "message": "Scenario Failed",
            "error": response_json.get("error", "Unknown error")
        }

    # Check if file exists
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found at {file_path}")

    # ✅ Return CSV file as downloadable response
    def iterfile():
        with open(file_path, mode="rb") as file:
            yield from file

    headers = {
        "Content-Disposition": f'attachment; filename="{file_name}"'
    }

    return StreamingResponse(iterfile(), media_type="text/csv", headers=headers)