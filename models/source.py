from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class Source(Base):
    __tablename__ = "source"
<<<<<<< HEAD
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    type = Column(String)
    url = Column(String)
    title = Column(String, nullable=False)


=======
    id=Column(Integer, primary_key=True, index=True)
    product_id=Column(Integer, ForeignKey("products.id"),nullable=False)
    type=Column(String)
    url=Column(String)
    title=Column(String,nullable=True)

>>>>>>> 9c2839c8ed127a634e56ea9db5c77ee3968a6ad7
    product = relationship("Product", back_populates="sources")