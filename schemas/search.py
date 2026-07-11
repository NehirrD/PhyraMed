from pydantic import BaseModel
from typing import List
from schemas.category import CategoryResponse
from schemas.product import ProductResponse


class SearchResponse(BaseModel):
    categories: List[CategoryResponse]
    products: List[ProductResponse]

    class Config:
        from_attributes = True