from pydantic import BaseModel

class ApiMappingsBase(BaseModel):
    source_api_id: int
    target_api_id: int
    source_field_path: str
    target_field_path: str
    transformation_logic: str | None = None

class ApiMappingsCreate(ApiMappingsBase):
    pass

class ApiMappingsUpdate(ApiMappingsBase):
    pass

class ApiMappingsOut(ApiMappingsBase):
    mapping_id: int

    class Config:
        from_attributes = True  # Pydantic v2
