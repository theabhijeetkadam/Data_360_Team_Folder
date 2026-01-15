from sqlalchemy import Column, Integer, String
from app.database import Base

class OrchestrationAccessMatrix(Base):
    __tablename__ = "orchestration_access_matrix"  # lowercase table name
    __table_args__ = {"schema": "public"}          # since it's in public schema

    id = Column(Integer, primary_key=True, index=True ,autoincrement=True)
    role_name = Column(String(50))
    sub_functionality_name = Column(String(100))
    action_type = Column(String(20))
    action_flag = Column(String(5))