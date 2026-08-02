from datetime import datetime
import re

from pydantic import BaseModel, Field, field_validator


_CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class CommentCreate(BaseModel):
    user_name: str = Field(
        default="Anonim Kullanıcı",
        max_length=60,
    )
    text: str = Field(
        min_length=1,
        max_length=500,
    )
    rating: int = Field(
        ge=1,
        le=5,
    )

    @field_validator("user_name", mode="before")
    @classmethod
    def normalize_user_name(cls, value):
        normalized = re.sub(r"\s+", " ", str(value or "").strip())
        if _CONTROL_CHARACTERS.search(normalized):
            raise ValueError("Kullanıcı adı geçersiz kontrol karakterleri içeremez.")
        return normalized or "Anonim Kullanıcı"

    @field_validator("text", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if value is None:
            return value
        normalized = str(value).replace("\r\n", "\n").replace("\r", "\n").strip()
        if _CONTROL_CHARACTERS.search(normalized):
            raise ValueError("Yorum metni geçersiz kontrol karakterleri içeremez.")
        return normalized


class CommentResponse(BaseModel):
    id: int
    product_id: int
    user_name: str
    text: str
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True
