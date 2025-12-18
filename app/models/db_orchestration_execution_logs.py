from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.database import Base  # Make sure your Base is imported correctly

class DBOrchestrationExecutionLogs(Base):
    __tablename__ = "db_orchestration_execution_logs"

    execution_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("db_orchestration_workflows.workflow_id", ondelete="CASCADE"))
    sql_id = Column(Integer, ForeignKey("sql_template.sql_id", ondelete="CASCADE"))
    status = Column(String(100), nullable=True)
    response_message = Column(String(100), nullable=True)
    error_message = Column(String(1000), nullable=True)
    record_count = Column(Integer, nullable=True)
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ended_at = Column(TIMESTAMP(timezone=True), nullable=True)
    executed_by = Column(String(100), nullable=True)
    environment_id = Column(Integer, ForeignKey("env_details.env_id"))
