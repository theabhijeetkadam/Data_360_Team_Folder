from sqlalchemy import Column, Integer, String
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column("User_ID", Integer, primary_key=True, index=True)
    name = Column("User_Name", String, index=True)
    email = Column(String, unique=True, index=True)
