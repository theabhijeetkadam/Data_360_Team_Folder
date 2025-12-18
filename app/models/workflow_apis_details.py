from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from app.database import Base


class WorkflowAPIDetail(Base):
    __tablename__ = "workflow_apis_details"

    api_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project_table.project_id"), nullable=False)
    module_id = Column(Integer, ForeignKey("project_table.module_id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("env_details.env_id"), nullable=False)
    scenario_id = Column(String(100), nullable=False)
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id"), nullable=False)
    api_name = Column(String(100), nullable=False)
    endpoint_url = Column(String(100), nullable=False)
    http_method = Column(String(10), nullable=False)
    headers = Column(JSON, nullable=True)
    payload_template = Column(String(100), nullable=True)
    auth_type = Column(String(50), nullable=True)
    auth_details = Column(JSON, nullable=True)
    timeout = Column(Integer, nullable=True)
    retry_policy = Column(String(100), nullable=True)

workflow = relationship("Workflows", back_populates="workflow_apis_details")
