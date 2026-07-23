from pydantic import BaseModel
from typing import List, Optional

from schemas.product import ProductResponse


class IdentifyResponse(BaseModel):
    identified_name: str
    identified_name_en: Optional[str] = None
    confidence: str
    description: str
    matched_products: List[ProductResponse] = []
    disclaimer: str

    class Config:
        from_attributes = True