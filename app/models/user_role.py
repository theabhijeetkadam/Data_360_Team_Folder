from sqlalchemy import Column, Integer, String
from app.database import Base

class UserRole(Base):
    __tablename__ = "user_role"
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), unique=True, nullable=False)