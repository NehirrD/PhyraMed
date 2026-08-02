from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from models import EvidenceLevel
from schemas.category import CategoryResponse


class IdentifyMatchedProduct(BaseModel):
    id: int
    name: str
    category_id: int
    category: Optional[CategoryResponse] = None
    usage_purpose: Optional[str] = None
    evidence_level: Optional[EvidenceLevel] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


class IdentifyAlternativeCandidate(BaseModel):
    name: str
    scientific_name: Optional[str] = None


class IdentifyVerification(BaseModel):
    accepted: bool
    confidence: Literal["yüksek", "orta", "düşük"]
    observed_supporting_features: List[str] = Field(default_factory=list)
    missing_features: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    needs_second_photo: bool = False
    reason: str


class IdentifyResponse(BaseModel):
    status: Literal["identified", "uncertain", "not_plant", "unavailable"]
    is_plant: bool
    identified_name: str
    identified_name_en: Optional[str] = None
    scientific_name: Optional[str] = None
    confidence: Literal["yüksek", "orta", "düşük"]
    image_quality: Literal["yeterli", "sınırlı", "yetersiz"] = "yetersiz"
    visible_parts: List[str] = Field(default_factory=list)
    distinguishing_features: List[str] = Field(default_factory=list)
    alternative_candidates: List[IdentifyAlternativeCandidate] = Field(default_factory=list)
    requires_additional_photo: bool = False
    catalog_match_status: Literal[
        "matched",
        "not_found",
        "needs_more_evidence",
        "not_applicable",
    ] = "not_applicable"
    match_explanation: str = ""
    description: str
    matched_products: List[IdentifyMatchedProduct] = Field(default_factory=list)
    verification: Optional[IdentifyVerification] = None
    disclaimer: str
