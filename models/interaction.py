from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Interaction(Base):
    __tablename__ = "interaction"
    id=Column(Integer,primary_key=True,index=True)
    product_id=Column(Integer,ForeignKey("product.id"),nullable=False)
    interacts_with=Column(Integer,nullable=False)
    description=Column(Text)
