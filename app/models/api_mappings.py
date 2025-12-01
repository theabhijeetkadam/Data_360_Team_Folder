from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class ApiMappings(Base):
    __tablename__ = "api_mappings"

    mapping_id = Column(Integer, primary_key=True, index=True)
    source_api_id = Column(Integer, ForeignKey("workflow_apis_details.api_id"), nullable=False)
    target_api_id = Column(Integer, ForeignKey("workflow_apis_details.api_id"), nullable=False)
    source_field_path = Column(String(100), nullable=False)
    target_field_path = Column(String(100), nullable=False)
    transformation_logic = Column(String(100), nullable=True)
