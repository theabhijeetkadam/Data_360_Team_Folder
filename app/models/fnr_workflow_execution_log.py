from sqlalchemy import Column, Integer, JSON, TIMESTAMP, ForeignKey, func, UUID
from app.database import Base

class FNRWorkflowExecutionLog(Base):
    __tablename__ = "fnr_workflow_execution_log"
    __table_args__ = {"schema": "clientdb"}

    execution_id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("project_table.module_id", ondelete="CASCADE"), nullable=False)
    environment_id = Column(Integer, ForeignKey("env_details.env_id", ondelete="CASCADE"), nullable=False)
    workflow_id = Column(Integer,    nullable=False)
    input_json = Column(JSON, nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("user_table.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
