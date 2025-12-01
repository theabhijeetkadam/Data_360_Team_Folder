from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class GenRocketServicesDetails(Base):
    __tablename__ = "genrocket_services_details"

    workflow_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_name = Column(String(100))  # ✅ Updated column
    tool_id = Column(String(10))
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