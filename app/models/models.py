
# app/models.py
from sqlalchemy import Column, Integer, Text, Boolean, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

# -------- Source table in gold_copy schema --------
class GoldCustomer(Base):
    __tablename__  = 'customer'               # exact table name in gold_copy
    __table_args__ = {'schema': 'gold_copy'}

    customer_id       = Column(Integer, primary_key=True)
    customer_name     = Column(Text, nullable=True)
    card_name         = Column(Text, nullable=True)
    customer_city     = Column(Text, nullable=True)
    card_type         = Column(Text, nullable=True)
    card_limit        = Column(Integer, nullable=True)
    customer_balance  = Column(Integer, nullable=True)