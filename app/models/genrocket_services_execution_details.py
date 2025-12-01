from sqlalchemy import Column, Integer, String, TIMESTAMP, Interval, Text, ForeignKey
from app.database import Base

class GenRocketServicesExecutionDetails(Base):
    __tablename__ = "genrocket_services_execution_details"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tool_id = Column(String(10))
    tool_name = Column(String(100))
    workflow_id = Column(Integer, ForeignKey("genrocket_services_details.workflow_id"))
    start_time = Column(TIMESTAMP)
    end_time = Column(TIMESTAMP)
    runtime = Column(Interval)
    created_by = Column(String(100))
    status = Column(String, default="PENDING")
    output_json = Column(Text)
