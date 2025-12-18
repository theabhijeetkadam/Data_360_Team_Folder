from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base

class FeatureRoleAccessMatrix(Base):
    __tablename__ = "feature_role_access_matrix"
    matrix_id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("feature_names.feature_id"))
    feature_name = Column(String(100))
    role = Column(String(50))
    action_type = Column(String(50))
    action_flag = Column(Boolean)