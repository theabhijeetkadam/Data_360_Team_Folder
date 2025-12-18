
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MiningWorkflowInputCriteria(Base):
    __tablename__ = "mining_workflow_input_criteria_1"
    __table_args__ = {"schema": "clientdb"}  # ✅ lowercase schema

    input_criteria_id = Column(Integer, primary_key=True, index=True)
    # ✅ Qualify FKs to their actual schema. Adjust if these live in clientdb instead of public.
    project_id     = Column(Integer, ForeignKey("public.project_table.project_id"))
    module_id      = Column(Integer, ForeignKey("public.project_table.module_id"))
    environment_id = Column(Integer, ForeignKey("public.env_details.env_id"))
    workflow_id    = Column(Integer, ForeignKey("public.mining_workflows_reserve.workflow_id"))

    param_id       = Column(Integer)
    business_name  = Column(String(255))
    source_table   = Column(String(100))
    source_column  = Column(String(100))
    type_of_field  = Column(String(100), nullable=True)
