from sqlalchemy import Column, Integer, String
from app.database import Base

class DBDefinationTable(Base):
    __tablename__ = "db_defination_table"
    db_id = Column(Integer, primary_key=True, index=True)
    db_name = Column(String(50), nullable=False)
    db_p1_name = Column(String(50))
    db_p2_name = Column(String(50))
    db_p3_name = Column(String(50))
    db_p4_name = Column(String(50))
    db_p5_name = Column(String(50))
    db_p6_name = Column(String(50))
    db_p7_name = Column(String(50))