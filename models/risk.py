from sqlalchemy import Column, Integer, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database import Base
import enum

class Severity(str,enum.Enum):
    LOW="Düşük"
    MIDDLE="Orta"
    HIGH="Yüksek"

class Risk(Base):
    __tablename__ = "risk"
    id=Column(Integer, primary_key=True,index=True)
    product_id=Column(Integer,ForeignKey("products.id"),nullable=False)
    description=Column(Text,nullable=False)
    severity=Column(Enum(Severity),nullable=True)

    product = relationship("Product", back_populates="risks")