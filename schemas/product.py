from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from models import EvidenceLevel, ProductStatus


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
    usage_purpose: str
    evidence_level:EvidenceLevel
    expert_opinion_summary:str
    image_url:str
    status:ProductStatus
    created_at:datetime
    updated_at:Optional[datetime]=None

    class Config:
        from_attributes = True





