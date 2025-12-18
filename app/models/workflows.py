from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from app.database import Base  # your Base from database.py

class Workflows(Base):
    __tablename__ = "workflows"

    workflow_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id"))
    project_name = Column(String(100))
    module_id = Column(Integer, ForeignKey("project_table.module_id"))
    module_name = Column(String(100))
    environment_id = Column(Integer, ForeignKey("env_details.env_id"))
    environment_name = Column(String(100))
    scenario_id = Column(Integer)
    scenario_name = Column(String(100))
    created_by = Column(String(100))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    # relationships
workflow_apis_details = relationship("WorkflowAPIDetail", back_populates="workflow")