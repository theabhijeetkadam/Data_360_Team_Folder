from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class APISequence(Base):
    __tablename__ = "api_sequence"

    sequence_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    workflow_id = Column(Integer, ForeignKey("workflows.workflow_id", ondelete="CASCADE"))
    api_id = Column(Integer, ForeignKey("workflow_apis_details.api_id", ondelete="CASCADE"))
    execution_order = Column(Integer)