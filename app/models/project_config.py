from sqlalchemy import Column, Integer, String
from app.database import Base

class ProjectConfig(Base):
    __tablename__ = "project_config"
    config_id = Column(Integer, primary_key=True, index=True)
    config_type = Column(String(50), nullable=False)