from pydantic import BaseModel
from typing import Optional

class CreateInteractionRequest(BaseModel):
    product_id:int
    interacts_with:str
    description:Optional[str]=None

class InteractionResponse(BaseModel):
    id:int
    product_id:int
    interacts_with:str
    description:Optional[str]=None

    class Config:
        from_attributes = True
