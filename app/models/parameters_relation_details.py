from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class ParametersRelationDetails(Base):
    __tablename__ = "parameters_relation_details_1"
    __table_args__ = {"schema": "clientdb"}

    relation_id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("project_table.project_id"), nullable=False)
    project_name = Column(String(255), ForeignKey("project_table.project_name"), nullable=False)
    module_id = Column(Integer, ForeignKey("project_table.module_id"), nullable=False)
    module_name = Column(String(255), ForeignKey("project_table.module_name"), nullable=False)
    environment_id = Column(Integer, ForeignKey("env_details.env_id"), nullable=False)
    environment_name = Column(String(100), ForeignKey("env_details.env_name"), nullable=False)
    workflow_id = Column(Integer, ForeignKey("clientdb.mining_workflows_reserve.workflow_id"), nullable=False)
    workflow_name = Column(String(255), ForeignKey("clientdb.mining_workflows_reserve.workflow_name"), nullable=False)

    primary_table_name = Column(String(100))
    primary_column_name = Column(String(100))
    secondary_table_name = Column(String(100))
    secondary_column_name = Column(String(100))
