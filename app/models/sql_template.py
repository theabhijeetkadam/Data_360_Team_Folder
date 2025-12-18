from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class SQLTemplate(Base):
    __tablename__ = "sql_template"

    sql_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("db_orchestration_workflows.workflow_id", ondelete="CASCADE"))
    sql_name = Column(String(100), nullable=False)
    table_name = Column(String(100))
    sql_query = Column(Text)
    query_type = Column(String(100))
    param_schema = Column(JSON)
    created_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
