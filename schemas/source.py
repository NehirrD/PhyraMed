from pydantic import BaseModel
from typing import Optional

class CreateSourceRequest(BaseModel):
    product_id:int
    type:str
    url:str
    title:Optional[str]

class SourceResponse(BaseModel):
    id:int
    product_id:int
    type:str
    url:str
    title:Optional[str]

    class Config:
        from_attributes=True
