# models.py
from sqlalchemy import Column, Integer, String
from db import Base

class Member(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    GENERICNAME = Column(String)
