from sqlalchemy import Column, Integer, String, Boolean
from app.database import Base

class ApplicationAccessMatrix(Base):
    __tablename__ = "application_access_matrix"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(100), nullable=False)
    sub_functionality_name = Column(String(150), nullable=False)
    action_type = Column(String(100), nullable=False)
    action_flag = Column(Boolean, default=False)
