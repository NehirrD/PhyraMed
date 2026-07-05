from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/product",
    tags=["Product"]
)

db_dependency = Annotated[Session, Depends(get_db)]

# Yeni ürün ekleme (bitki/takviye):
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProductResponse)
async def create_product(db: db_dependency, request: schemas.CreateProductRequest):
    product = models.Product(
        name=request.name,
        category_id=request.category_id,
        usage_purpose=request.usage_purpose,
        evidence_level=request.evidence_level,
        evidence_summary=request.evidence_summary,  # Excel'deki formata uyarlandı
        image_url=request.image_url,
        status=request.status
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product