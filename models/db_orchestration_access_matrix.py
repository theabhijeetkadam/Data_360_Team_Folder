from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class DBOrchestrationAccessMatrix(Base):
    __tablename__ = "db_orchestration_access_matrix"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), nullable=False)
    sub_functionality_name = Column(String(100), nullable=True)
    action_type = Column(String(100), nullable=True)
    action_flag = Column(Boolean, default=False)
