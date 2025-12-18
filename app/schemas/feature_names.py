from pydantic import BaseModel, Field

class FeatureNamesCreate(BaseModel):
    feature_name: str = Field(..., min_length=3, max_length=100)

class FeatureNames(BaseModel):
    feature_id: int
    feature_name: str

    class Config:
        from_attributes = True
