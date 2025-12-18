from sqlalchemy import Column, Integer, String
from app.database import Base

class FeatureNames(Base):
    __tablename__ = "feature_names"
    feature_id = Column(Integer, primary_key=True, index=True)
    feature_name = Column(String(100), unique=True, nullable=False)