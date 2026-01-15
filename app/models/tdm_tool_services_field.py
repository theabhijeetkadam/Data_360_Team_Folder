
# app/models/tdm_tool_services_field.py
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.tdm_tool import TdmToolName  # for relationship

class TDMToolWorkflowField(Base):
    __tablename__ = "tdm_tool_services_field"
    __table_args__ = (
        # If you want exactly ONE workflow-fields row per tool, keep this unique constraint.
        # If you want MULTIPLE rows per tool, REMOVE this UniqueConstraint line.
        UniqueConstraint("tool_id", name="uq_tdm_tool_services_field_tool_id"),
        {"schema": "public"},
    )

    # New auto-increment PK
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)

    # Foreign key to tdm_tool_names.tool_id
    tool_id = Column(
        Integer,
        ForeignKey("public.tdm_tool_names.tool_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    tool_name = Column(String(100))
    workflow_field_1 = Column(String(50))
    workflow_field_2 = Column(String(50))
    workflow_field_3 = Column(String(50))
    workflow_field_4 = Column(String(50))
    workflow_field_5 = Column(String(50))
    workflow_field_6 = Column(String(50))
    workflow_field_7 = Column(String(50))
    workflow_field_8 = Column(String(50))
    workflow_field_9 = Column(String(50))
    workflow_field_10 = Column(String(50))

    # Optional: ORM relationship to navigate back to the tool
    tool = relationship(TdmToolName, backref="workflow_fields")
