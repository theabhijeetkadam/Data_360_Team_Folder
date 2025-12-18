from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base

class SequenceMapping(Base):
    __tablename__ = "sequence_mappings"

    sequence_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("db_orchestration_workflows.workflow_id", ondelete="CASCADE"))
    sql_id = Column(Integer, ForeignKey("sql_template.sql_id", ondelete="CASCADE"))
    execution_order = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
