from sqlalchemy import Column, Integer, String,Text,TIMESTAMP
from sqlalchemy.sql import func
from database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key = True)
    full_name = Column(String)
    email = Column(String,unique = True)
    password_hash = Column(Text)
    avatar = Column(Text)
    created_at = Column(TIMESTAMP,server_default = func.now())