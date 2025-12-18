from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class UserAppMatrix(Base):
    __tablename__ = "user_app_matrix"
    matrix_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_table.user_id"))
    user_name = Column(String(100))
    user_role = Column(String(50))
    project_id = Column(Integer, ForeignKey("project_table.project_id"))