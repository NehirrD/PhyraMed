from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base
import enum


class EvidenceLevel(str, enum.Enum):
    HIGH = "Yüksek"
    MEDIUM = "Orta"
    LOW = "Sadece geleneksel kullanım"


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    usage_purpose = Column(Text)
    evidence_level = Column(Enum(EvidenceLevel))
    expert_opinion_summary = Column(Text)
    image_url = Column(String, nullable=True)
    status = Column(String, default="active")

    category = relationship("Category", back_populates="products")
    risks = relationship("Risk", back_populates="product")
    sources = relationship("Source", back_populates="product")
    interactions = relationship("Interaction", back_populates="product")
    comments = relationship("Comment", back_populates="product")


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    description = Column(Text)
    severity = Column(String)

    product = relationship("Product", back_populates="risks")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    title = Column(String)
    url = Column(String)

    product = relationship("Product", back_populates="sources")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    interacts_with = Column(String)
    description = Column(Text)

    product = relationship("Product", back_populates="interactions")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_name = Column(String)
    content = Column(Text)
    rating = Column(Integer)
    created_at = Column(String)

    product = relationship("Product", back_populates="comments")