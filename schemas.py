from pydantic import BaseModel
from typing import Optional
from models import EvidenceLevel


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class RiskBase(BaseModel):
    product_id: int
    description: str
    severity: str


class RiskCreate(RiskBase):
    pass


class RiskResponse(RiskBase):
    id: int

    class Config:
        from_attributes = True


class SourceBase(BaseModel):
    product_id: int
    title: str
    url: str


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int

    class Config:
        from_attributes = True


class InteractionBase(BaseModel):
    product_id: int
    interacts_with: str
    description: str


class InteractionCreate(InteractionBase):
    pass


class InteractionResponse(InteractionBase):
    id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    product_id: int
    user_name: str
    content: str
    rating: int
    created_at: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    category_id: int
    usage_purpose: str
    evidence_level: EvidenceLevel
    expert_opinion_summary: str
    image_url: Optional[str] = None
    status: str = "active"


class CreateProductRequest(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    category: Optional[CategoryResponse] = None
    risks: list[RiskResponse] = []
    sources: list[SourceResponse] = []
    interactions: list[InteractionResponse] = []
    comments: list[CommentResponse] = []

    class Config:
        from_attributes = True


class IdentifyResponse(BaseModel):
    identified_name: str
    identified_name_en: Optional[str] = None
    confidence: float
    description: str
    matched_products: list[dict]
    disclaimer: str