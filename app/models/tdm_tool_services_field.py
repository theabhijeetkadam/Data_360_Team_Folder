
from sqlalchemy import Column, String
from app.database import Base  # import your Base

class TDMToolWorkflowField(Base):
    __tablename__ = "tdm_tool_services_field"  # Table name remains same unless you renamed it in DB

    tool_id = Column(String(10), primary_key=True, index=True)
    tool_name = Column(String(100))
    workflow_field_1 = Column(String(50))  # ✅ Updated
    workflow_field_2 = Column(String(50))
    workflow_field_3 = Column(String(50))
    workflow_field_4 = Column(String(50))
    workflow_field_5 = Column(String(50))
    workflow_field_6 = Column(String(50))
    workflow_field_7 = Column(String(50))
    workflow_field_8 = Column(String(50))
    workflow_field_9 = Column(String(50))
    workflow_field_10 = Column(String(50))
