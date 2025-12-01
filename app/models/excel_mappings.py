from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class ExcelMappings(Base):
    __tablename__ = "excel_mappings"

    excel_mapping_id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id"))
    api_id = Column(Integer, ForeignKey("workflow_apis_details.api_id"))
    excel_column_name = Column(String(100))
    payload_field_path = Column(String(100))
    data_type = Column(String(100))
