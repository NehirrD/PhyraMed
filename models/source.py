from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Source(Base):
    __tablename__ = "source"
    id=Column(Integer, primary_key=True, index=True)
    product_id=Column(Integer, ForeignKey("products.id"),nullable=False)
    type=Column(String)
    url=Column(String)
    title=Column(String,nullable=False)
