
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
# Ensure these imports exist so mappers can resolve the target tables
from app.models.project import Project
from app.models.env import Environment

class MiningWorkflowsReserve(Base):
    __tablename__ = "mining_workflows_reserve"
    __table_args__ = {"schema": "clientdb"}  # table is in clientdb

    workflow_id   = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String(255), nullable=False)

    # --- FK columns (cross-schema) ---
    project_id = Column(
        Integer, nullable=False
        #ForeignKey("public.project_table.project_id", onupdate="CASCADE", ondelete="SET NULL"),
        #nullable=True, index=True
    )
    env_id = Column(
        Integer, nullable=False
        #ForeignKey("public.env_details.env_id", onupdate="CASCADE", ondelete="SET NULL"),
        #nullable=True, index=True
    )

    # --- Denormalized names (optional) ---
    project_name = Column(String(255), nullable=True)
    env_name     = Column(String(255), nullable=True)

    # --- Relationships (explicit primaryjoin + foreign_keys) ---
    #project = relationship(
       # Project,
       # primaryjoin="MiningWorkflowsReserve.project_id == Project.project_id",
       # foreign_keys=[project_id],
       # backref="workflows",
       # lazy="joined",
   # )

    #environment = relationship(
       # Environment,
       # primaryjoin="MiningWorkflowsReserve.env_id == Environment.env_id",
       # foreign_keys=[env_id],
       # backref="workflows",
       # lazy="joined",
    #)