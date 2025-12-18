from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base

class GovernanceDeleteLogs(Base):
    __tablename__ = "governance_delete_logs"

    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    deleted_by_user_emp_id = Column(String(100))
    deleted_by_user_name = Column(String(100))
    deleted_by_user_email_id = Column(String(100))
    deleted_project_id = Column(Integer, autoincrement=True)
    deleted_project_name = Column(String(100))
    deleted_module_name = Column(String(100))
    deleted_scenario_name = Column(String(100))
    deleted_environment_id = Column(Integer, autoincrement=True)
    deleted_environment_name = Column(String(100))
    deleted_database_type = Column(String(100))
    deleted_date = Column(Date)
    deleted_time = Column(Time)
