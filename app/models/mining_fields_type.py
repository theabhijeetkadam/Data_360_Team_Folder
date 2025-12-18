from sqlalchemy import Column, Integer, String
from app.database import Base

class MiningFieldsType(Base):
    __tablename__ = "mining_fields_type"
    __table_args__ = {"schema": "clientdb"}

    field_id = Column(Integer, primary_key=True, index=True)
    type_of_field = Column(String(255), unique=True, nullable=False)
