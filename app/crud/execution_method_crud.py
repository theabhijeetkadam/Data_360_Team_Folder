
# app/crud/execution_method_crud.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from app.models.execution_method_model import GenRocketServiceDetail
from app.models.genrocket_services_execution_details import GenRocketServicesExecutionDetails


def get_service_by_workflow_id(db: Session, workflow_id: int) -> Optional[GenRocketServiceDetail]:
    if db is None:
        return None
    return (
        db.query(GenRocketServiceDetail)
        .filter(GenRocketServiceDetail.workflow_id == workflow_id)
        .first()
    )


def log_genrocket_service_execution(
    db: Session,
    tool_id: str,
    tool_name: str,
    workflow_id: int,
    start_time: datetime,
    end_time: datetime,
    runtime,
    created_by: str,
    status: str,
    output_json: str
) -> GenRocketServicesExecutionDetails:
    """
    Persists one execution log row. NOTE: The DB should auto-generate job_id (PK/identity).
    Ensure your GenRocketServicesExecutionDetails model has:
        job_id (PK), tool_id, tool_name, workflow_id, start_time, end_time,
        runtime, created_by, status, output_json
    """
    log = GenRocketServicesExecutionDetails(
        tool_id=tool_id,
        tool_name=tool_name,
        workflow_id=workflow_id,
        start_time=start_time,
        end_time=end_time,
        runtime=runtime,
        created_by=created_by,
        status=status,
        output_json=output_json
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_execution_log_by_workflow_and_job(
    db: Session, workflow_id: int, job_id: int
) -> Optional[GenRocketServicesExecutionDetails]:
    """
    Returns the execution log row for (workflow_id, job_id).
    Assumes GenRocketServicesExecutionDetails has columns: job_id, workflow_id, status, output_json.
    """
    if db is None:
        return None
    return (
        db.query(GenRocketServicesExecutionDetails)
        .filter(
            GenRocketServicesExecutionDetails.workflow_id == workflow_id,
            GenRocketServicesExecutionDetails.job_id == job_id
        )
        .first()
    )
