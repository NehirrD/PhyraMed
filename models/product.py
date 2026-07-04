from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime,Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class EvidenceLevel(str,enum.Enum):
    LOW="Zayıf"
    MIDDLE="Orta"
    HIGH="Güçlü"

class ProductStatus(str,enum.Enum):
    verified="Onaylanmış"
    ai_generated="AI"

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"),nullable=False)
    usage_purpose=Column(Text)
    evidence_level=Column(Enum(EvidenceLevel))
    expert_opinion_summary=Column(Text)
    image_url = Column(String)
    status=Column(Enum(ProductStatus))
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True), onupdate=func.now())

    risks = relationship("Risk", back_populates="product")
    sources = relationship("Source", back_populates="product")
