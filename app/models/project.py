
from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.database import Base

class Project(Base):
    __tablename__ = "project_table"

    project_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_name = Column(String(100), nullable=False)
    created_by_name = Column(String(100))
    created_by_role = Column(String(50))
    created_by_user_id = Column(Integer)
    module_name = Column(String(100))
    project_description = Column(String(255))
    module_id = Column(Integer, index=True)
    scenario_id = Column(Integer, index=True)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP, nullable=True)       # ✅ Timestamp
    updated_by = Column(String(100), nullable=True)     # ✅ String type
    status = Column(String)
