from sqlalchemy.orm import Session
from app.schemas import fnr_workflow_execution_log as schemas
from app.crud import fnr_workflow_execution_log as crud
from app.models import fnr_workflow_execution_log as models

def create_workflow_execution_log(db: Session, log: schemas.WorkflowExecutionLogCreate):
    db_log = models.FNRWorkflowExecutionLog(
        project_id=log.project_id,
        module_id=log.module_id,
        environment_id=log.environment_id,
        workflow_id=log.workflow_id,
        input_json=log.input_json,
        created_by_user_id=log.created_by_user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log