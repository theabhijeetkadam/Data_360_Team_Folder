from sqlalchemy.orm import Session
#from app.models.execution_method_model import ExecutionMethod  # <-- SQLAlchemy model
#from app.models.execution_method import ExecutionMethodCreate
from app.models.execution_method_model import GenRocketServiceDetail
from app.models.genrocket_services_execution_details import GenRocketServicesExecutionDetails
from datetime import datetime

def get_service_by_workflow_id(db: Session, workflow_id: int):
    return db.query(GenRocketServiceDetail).filter(GenRocketServiceDetail.workflow_id == workflow_id).first()


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
):
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

