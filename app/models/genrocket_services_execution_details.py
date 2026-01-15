
# app/models/genrocket_services_execution_details.py
from sqlalchemy import Column, Integer, String, TIMESTAMP, Interval, Text, ForeignKey
from app.database import Base

class GenRocketServicesExecutionDetails(Base):
    __tablename__ = "genrocket_services_execution_details"

    job_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ✅ CHANGED: tool_id now Integer (matching DB)
    tool_id = Column(Integer, index=True, nullable=False)

    tool_name = Column(String(100), nullable=False)
    workflow_id = Column(Integer, ForeignKey("genrocket_services_details.workflow_id"), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    runtime = Column(Interval, nullable=False)
    created_by = Column(String(100), nullable=False)
    status = Column(String, default="PENDING", nullable=False)  # keep as-is; consider String(20) later
    output_json = Column(Text, nullable=True)
