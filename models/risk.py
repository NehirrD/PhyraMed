from sqlalchemy import Column, Integer, Text, ForeignKey, Enum
from database import Base
import enum

class Severity(str,enum.Enum):
    LOW="Düşük"
    MIDDLE="Orta"
    HIGH="Yüksek"

class Risk(Base):
    __tablename__ = "risk"
    id=Column(Integer, primary_key=True,index=True)
    product_id=Column(Integer,ForeignKey("product.id"),nullable=False)
    description=Column(Text,nullable=False)
    severity=Column(Enum(Severity),nullable=True)