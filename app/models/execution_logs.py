from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    execution_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id"), nullable=False)
    api_id = Column(Integer, ForeignKey("workflow_apis_details.api_id"), nullable=False)
    status = Column(String(100), nullable=False)
    response_code = Column(Integer, nullable=True)
    response_body = Column(String(100), nullable=True)
    error_message = Column(String(100), nullable=True)
    executed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    executed_by = Column(String(100), nullable=True)
