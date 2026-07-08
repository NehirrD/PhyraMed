from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    user_name: Optional[str] = "Anonim Kullanıcı"
    text: str
    rating: int

class CommentResponse(BaseModel):
    id: int
    product_id: int
    user_name: str
    text: str
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True