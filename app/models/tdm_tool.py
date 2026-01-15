
# app/models/tdm_tool.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class TdmToolName(Base):
    __tablename__ = "tdm_tool_names"
    __table_args__ = {"schema": "public"} 

    tool_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    tool_name = Column(String(100), nullable=False, unique=True)
    tool_type = Column(String(50), nullable=True)
    # NOTE: You had Boolean imported but the column is a String. Keeping it as String to avoid breaking changes.
    # If you want Boolean instead, let me know and I’ll adjust schemas + data.
    active_flag = Column(String(50), default="True")
