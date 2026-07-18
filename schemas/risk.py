from pydantic import BaseModel
from typing import Optional
from models import Severity

class CreateRiskRequest(BaseModel):
    product_id:int
    description:str
    severity:Optional[Severity]=None

class RiskResponse(BaseModel):
    id: int
    product_id: int
    description: str
    severity: Optional[Severity] = None


    class Config:
        from_attributes=True