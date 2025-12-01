from pydantic import BaseModel

class ExcelMappingsBase(BaseModel):
    workflow_id: int
    api_id: int
    excel_column_name: str
    payload_field_path: str
    data_type: str

class ExcelMappingsCreate(ExcelMappingsBase):
    pass

class ExcelMappingsUpdate(ExcelMappingsBase):
    pass

class ExcelMappingsOut(ExcelMappingsBase):
    excel_mapping_id: int

    class Config:
        from_attributes = True  # For Pydantic V2
