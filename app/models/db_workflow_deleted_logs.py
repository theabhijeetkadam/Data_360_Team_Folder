from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base  # Make sure your Base is imported correctly

class DBWorkflowDeletedLogs(Base):
    __tablename__ = "db_workflow_deleted_logs"

    deleted_log_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, nullable=True)
    project_id = Column(Integer, nullable=True)
    module_id = Column(Integer, nullable=True)
    environment_id = Column(Integer, nullable=True)
    deleted_by = Column(String(100), nullable=False)
    deleted_by_name = Column(String(100), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

