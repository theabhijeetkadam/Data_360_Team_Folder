from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class MiningAccessMatrix(Base):
    __tablename__ = "mining_access_matrix"
    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50))
    sub_functionality_name = Column(String(100))
    action_type = Column(String(50))
    action_flag = Column(Boolean)