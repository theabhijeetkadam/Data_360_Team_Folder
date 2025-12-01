
from sqlalchemy import Column, Integer, String, Date, Time
from app.database import Base

class DeleteLog(Base):
    __tablename__ = "delete_logs"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    deleted_by_userid = Column(Integer, nullable=False)
    deleted_by_username = Column(String(100), nullable=False)
    deleted_date = Column(Date, nullable=False)
    deleted_time = Column(Time, nullable=False)
    module_name = Column(String(100), nullable=False)  # New column
    record_id = Column(Integer, nullable=False)        # New column
