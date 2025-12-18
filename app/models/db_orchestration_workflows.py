from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, func
from app.database import Base

class DBOrchestrationWorkflows(Base):
    __tablename__ = "db_orchestration_workflows"

    workflow_id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(100), nullable=False)

    project_id = Column(Integer, ForeignKey("project_table.project_id", ondelete="CASCADE"))
    project_name = Column(String(100))

    module_id = Column(Integer, ForeignKey("project_table.module_id", ondelete="CASCADE"))
    module_name = Column(String(100))

    environment_id = Column(Integer, ForeignKey("env_details.env_id", ondelete="CASCADE"))
    environment_name = Column(String(100))

    created_by = Column(String(100))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
