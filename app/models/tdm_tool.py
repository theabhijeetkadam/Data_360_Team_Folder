from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, func

from app.database import Base

class TdmToolName(Base):
    __tablename__ = "tdm_tool_names"
    __table_args__ = {"schema": "public"} 

    tool_id = Column(String,  primary_key=True, index=True)
    tool_name = Column(String(100), nullable=False, unique=True)
    tool_type = Column(String(50))
    active_flag = Column(String(50), default=True)
    