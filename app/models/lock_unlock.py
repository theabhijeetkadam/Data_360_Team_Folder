from sqlalchemy import Column, Integer, String, Boolean, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class ExtractedData(Base):
    __tablename__ = "extracted_data_table"
    __table_args__ = {"schema": "clientdb"}
    execution_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=False)
    module_id = Column(Integer, nullable=False)
    environment_id = Column(Integer, nullable=False)
    workflow_id = Column(Integer, nullable=False)
    source_table = Column(String)
    data_key = Column(String)
    field_values = Column(JSON)
    is_reserved = Column(Boolean, default=True)
    reserved_at = Column(TIMESTAMP(timezone=True))
    extracted_at = Column(TIMESTAMP(timezone=True))
    updated_by = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
