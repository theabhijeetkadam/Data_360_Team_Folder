from pydantic import BaseModel

class FeatureRoleAccessMatrixBase(BaseModel):
    feature_id: int
    feature_name: str
    role: str
    action_type: str
    action_flag: bool

class FeatureRoleAccessMatrixCreate(FeatureRoleAccessMatrixBase):
    pass

class FeatureRoleAccessMatrix(FeatureRoleAccessMatrixBase):
    matrix_id: int

    class Config:
        from_attributes = True
