from sqlalchemy.orm import Session
from app.schemas import fnr_workflow_execution_log as schemas
from app.crud import fnr_workflow_execution_log as crud
from app.models import fnr_workflow_execution_log as models
import uuid
from sqlalchemy import text


def create_workflow_execution_log(payload: schemas.WorkflowExecutionLogCreate, db: Session):

    result = db.execute(text("select project_id, env_id from clientdb.mining_workflows_reserve where workflow_id = :wid"), {"wid": payload.workflow_id})
    project_id, environment_id = result.fetchone()
    module_id = 11 #TODO hardcoded
    db_log = models.FNRWorkflowExecutionLog(
        execution_id = uuid.uuid4(),
        project_id=project_id,
        module_id=module_id,
        environment_id=environment_id,
        workflow_id=payload.workflow_id,
        input_json=payload.input_json,
        created_by_user_id=payload.created_by_user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log