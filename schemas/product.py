from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from models import EvidenceLevel, ProductStatus
from schemas.category import CategoryResponse
from schemas.interaction import InteractionResponse
from schemas.risk import RiskResponse
from schemas.source import SourceResponse


class CreateProductRequest(BaseModel):
    name: str
    category_id:int
    usage_purpose: str
    evidence_level:EvidenceLevel
    expert_opinion_summary:str
    image_url:str
    status:ProductStatus

class ProductResponse(BaseModel):
    id:int
    name: str
    category_id:int
    category: Optional[CategoryResponse] = None
    usage_purpose: str
    evidence_level:EvidenceLevel
    expert_opinion_summary:str
    image_url:str
    status:ProductStatus
    created_at:datetime
    updated_at:Optional[datetime]=None
    risks: List[RiskResponse] = []
    sources: List[SourceResponse] = []
    interactions: List[InteractionResponse] = []

    class Config:
        from_attributes = True





