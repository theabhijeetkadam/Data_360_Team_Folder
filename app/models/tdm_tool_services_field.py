
# app/models/tdm_tool_services_field.py
from sqlalchemy import Column, Integer, String
from app.database import Base  # import your Base

class TDMToolWorkflowField(Base):
    __tablename__ = "tdm_tool_services_field"  # Table name unchanged

    # ✅ CHANGED: tool_id is Integer PK
    tool_id = Column(Integer, primary_key=True, index=True, nullable=False)

    tool_name = Column(String(100))
    workflow_field_1 = Column(String(50))
    workflow_field_2 = Column(String(50))
    workflow_field_3 = Column(String(50))
    workflow_field_4 = Column(String(50))
    workflow_field_5 = Column(String(50))
    workflow_field_6 = Column(String(50))
    workflow_field_7 = Column(String(50))
    workflow_field_8 = Column(String(50))
    workflow_field_9 = Column(String(50))
    workflow_field_10 = Column(String(50))
