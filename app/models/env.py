from sqlalchemy import Column, Integer, String, UniqueConstraint, TIMESTAMP
from app.database import Base

class Environment(Base):
    __tablename__ = "env_details"

    env_id = Column(Integer, primary_key=True, index=True)
    env_name = Column(String, nullable=False)
    env_instance = Column(String, nullable=False)
    env_app_name = Column(String)
    env_db_type = Column(String)
    db_p1_name = Column(String)
    db_p2_name = Column(String)
    db_p3_name = Column(String)
    db_p4_name = Column(String)
    db_p5_name = Column(String)
    db_p6_name = Column(String)
    db_p7_name = Column(String)
    status = Column(String)
    updated_at = Column(TIMESTAMP, nullable=True)       # ✅ New column
    updated_by = Column(String(100), nullable=True)     # ✅ New column


    # ✅ Add unique constraint for env_name + env_instance
    __table_args__ = (
        UniqueConstraint('env_name', 'env_instance', name='uq_env_name_instance'),
    )
