from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base
from datetime import datetime

class GenRocketServiceDetail(Base):
    __tablename__ = "genrocket_services_details"
    __table_args__ = {'extend_existing': True}
    
    workflow_id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    clientappid = Column(String)
    clientuserid = Column(String)
    scenario = Column(String)
    scenariopath = Column(String)
    keepfilename = Column(Boolean)

