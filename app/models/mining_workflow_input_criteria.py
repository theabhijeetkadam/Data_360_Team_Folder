from sqlalchemy import Column, Integer, String, ForeignKey, text
from app.database import Base

class MiningWorkflowInputCriteria(Base):
    __tablename__ = "mining_workflow_input_criteria_1"
    __table_args__ = {"schema": "clientdb"}

    input_criteria_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # param_id auto-generated via sequence
    param_id = Column(Integer, nullable=False, unique=True, server_default=text("nextval('clientdb.mining_workflow_input_criteria_1_param_id_seq')"))

    # Foreign Keys
    project_id = Column(Integer, ForeignKey("project_table.project_id"), nullable=False)
    module_id = Column(Integer, ForeignKey("project_table.module_id"), nullable=False)
    environment_id = Column(Integer, ForeignKey("env_details.env_id"), nullable=False)
    workflow_id = Column(Integer, ForeignKey("clientdb.mining_workflows_reserve.workflow_id"))
    type_of_field = Column(String(100), ForeignKey("clientdb.mining_fields_type.type_of_field"))

    # Regular columns
    project_name = Column(String(255), nullable=False)
    module_name = Column(String(255), nullable=False)
    environment_name = Column(String(100), nullable=False)
    workflow_name = Column(String(255), nullable=False)
    business_name = Column(String(255))
    source_table = Column(String(100))
    source_column = Column(String(100))
    source_schema= Column(String(100))
