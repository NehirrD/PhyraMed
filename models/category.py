from sqlalchemy import Column, Integer, String, Text
from database import Base

class Category(Base):
    __tablename__ = "category"
    id=Column(Integer, primary_key=True, index=True)
    name=Column(String, nullable=False)
    description=Column(Text, nullable=False)
