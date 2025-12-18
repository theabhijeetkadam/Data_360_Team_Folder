from sqlalchemy import Column, Integer, String
from ..database import Base  # Assuming you have a Base from SQLAlchemy declarative_base()

class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # 'project', 'user', 'environment'
    status_value = Column(String(50), nullable=False)  # 'active', 'closed', 'inactive'