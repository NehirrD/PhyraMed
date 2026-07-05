from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from models import EvidenceLevel, ProductStatus
from schemas.risk import RiskResponse
from schemas.source import SourceResponse


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
<<<<<<< HEAD
    category_id: int
    usage_purpose: Optional[str] = None
    evidence_level: Optional[str] = None
    evidence_summary: Optional[str] = None  
    image_url: Optional[str] = None
    status: Optional[str] = None
=======
    category_id:int
    usage_purpose: str
    evidence_level:EvidenceLevel
    expert_opinion_summary:str
    image_url:str
    status:ProductStatus
    created_at:datetime
    updated_at:Optional[datetime]=None
    risks: List[RiskResponse] = []
    sources: List[SourceResponse] = []
>>>>>>> b1dbbe10e4c024620df903163a2c566fa618aa45

    class Config:
        from_attributes = True
        orm_mode = True





