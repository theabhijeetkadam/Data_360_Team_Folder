
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class MiningWorkflowOutputCriteria(Base):
    __tablename__ = "mining_workflow_output_criteria_1"
    __table_args__ = {"schema": "clientdb"}

    output_criteria_id = Column(Integer, primary_key=True, index=True)

    project_id = Column(Integer, ForeignKey("project_table.project_id"), nullable=False)
    project_name = Column(String(255), ForeignKey("project_table.project_name"), nullable=False)
    module_id = Column(Integer, ForeignKey("project_table.module_id"), nullable=False)
    module_name = Column(String(255), ForeignKey("project_table.module_name"), nullable=False)
    environment_id = Column(Integer, ForeignKey("env_details.env_id"), nullable=False)
    environment_name = Column(String(100), ForeignKey("env_details.env_name"), nullable=False)
    workflow_id = Column(Integer, nullable=False)
    workflow_name = Column(String(255), nullable=False)

    business_name = Column(String(255))
    source_table = Column(String(100))
    source_column = Column(String(100))

    # ✅ New flag column (rename or add per migration)
    is_parameter_flag = Column(Boolean, default=False, nullable=False)
    # If you keep legacy:
    # is_reserved = Column(Boolean, default=False)
