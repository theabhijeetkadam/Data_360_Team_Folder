from sqlalchemy import Column, Integer, String
from app.database import Base

class GenRocketServicesDetails(Base):
    __tablename__ = "genrocket_services_details"

    service_id = Column(Integer, primary_key=True, index=True)
    tool_id = Column(String(10))
    project_name = Column(String(100))
    domain_name = Column(String(100))
    scenario_name = Column(String(100))
    environment = Column(String(50))
    clientappid = Column(String(100))
    clientuserid = Column(String(100))
    scenario = Column(String(100))