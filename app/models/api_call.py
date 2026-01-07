
# app/models/api_call.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.database import Base

class ApiCall(Base):
    __tablename__ = "api_call_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    path = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False)  # UTC
    user_id = Column(Integer, nullable=True)
