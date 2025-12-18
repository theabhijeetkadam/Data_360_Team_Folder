
# app/models/genrocket_services_details.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class GenRocketServicesDetails(Base):
    __tablename__ = "genrocket_services_details"

    workflow_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_name = Column(String(100), unique=True)  # ✅ Updated column

    # ✅ CHANGED: tool_id is now Integer; add FK if tdm_tool_names.tool_id is INT
    tool_id = Column(Integer, index=True, nullable=False)
    # If you have a tools table and want to enforce linkage:
    # tool_id = Column(Integer, ForeignKey("tdm_tool_names.tool_id"), index=True, nullable=False)

    project_name = Column(String(100))
    domain_name = Column(String(100))
    environment = Column(String(50))
    clientappid = Column(String(100))
    clientuserid = Column(String(100))
    scenario = Column(String(100))
    project_id = Column(Integer, autoincrement=True)
    module_name = Column(String(100))
    module_id = Column(Integer, index=True, autoincrement=True)
    scenario_id = Column(Integer, index=True, autoincrement=True)
    username = Column(String(100))
    password = Column(String(100))
    scenariopath = Column(String(100))
    keepfilename = Column(Boolean)
