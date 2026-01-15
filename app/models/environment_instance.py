from sqlalchemy import Column, Integer, String
from app.database import Base

class EnvironmentInstance(Base):
    __tablename__ = "environment_instance"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)