from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from models import EvidenceLevel, ProductStatus


class CreateProductRequest(BaseModel):
    name: str
    category_id: int
    usage_purpose: Optional[str] = None
    evidence_level: Optional[str] = None
    evidence_summary: Optional[str] = None
    image_url: Optional[str] = None
    status: Optional[str] = "ai_generated"

class ProductResponse(BaseModel):
    id: int
    name: str
    category_id: int
    usage_purpose: Optional[str] = None
    evidence_level: Optional[str] = None
    evidence_summary: Optional[str] = None  
    image_url: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True





