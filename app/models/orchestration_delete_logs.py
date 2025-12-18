from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base

class OrchestrationDeleteLogs(Base):
    __tablename__ = "orchestration_delete_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    record_id = Column(Integer, index=True, autoincrement=True)
    deleted_by_user_name = Column(String(100))
    deleted_date = Column(Date)
    deleted_time = Column(Time)
    service_id = Column(Integer, autoincrement=True)
    deleted_project_id = Column(Integer, autoincrement=True)
    deleted_project_name = Column(String(100))
    deleted_module_name = Column(String(100))
    deleted_scenario_name = Column(String(100))