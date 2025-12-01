from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class RuntimeLog(Base):
    __tablename__ = "runtime_logs"

    execution_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("db_orchestration_workflows.workflow_id", ondelete="CASCADE"))
    sql_id = Column(Integer, ForeignKey("sql_template.sql_id", ondelete="CASCADE"))
    status = Column(String(100))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    executed_by = Column(String(100))
