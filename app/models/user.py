from sqlalchemy import Column, Integer, String, TIMESTAMP
from app.database import Base

class User(Base):
    __tablename__ = "user_table"
    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    user_emp_id = Column(String)
    user_email_id = Column(String)
    role_id = Column(Integer)
    user_password = Column(String)
    user_role = Column(String)
    emp_name = Column(String)
    status = Column(String)
    updated_at = Column(TIMESTAMP, nullable=True)       # ✅ New column
    updated_by = Column(String(100), nullable=True)     # ✅ New colum
