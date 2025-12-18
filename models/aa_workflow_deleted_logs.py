from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, text
from app.database import Base

class AAWorkflowDeletedLogs(Base):
    __tablename__ = "aa_workflow_deleted_logs"

    deleted_log_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id"))
    project_name = Column(String(100))
    module_id = Column(Integer, ForeignKey("project_table.module_id"))
    module_name = Column(String(100))
    environment_id = Column(Integer, ForeignKey("env_details.env_id"))
    environment_name = Column(String(100))
    scenario_id = Column(Integer, ForeignKey("project_table.scenario_id"))
    scenario_name = Column(String(100))
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id"))
    deleted_by_user_id = Column(Integer, ForeignKey("user_table.user_id"))
    deleted_by_user_name = Column(String(100))
    deleted_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
