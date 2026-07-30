from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/products/{product_id}/summary", status_code=status.HTTP_200_OK)
async def get_product_summary(db: db_dependency, product_id: int):
    """Ürün için detaylı analiz özeti"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    return {
        "product_id": product.id,
        "name": product.name,
        "category": product.category.name if product.category else None,
        "evidence_level": product.evidence_level,
        "usage_purpose": product.usage_purpose,
        "expert_opinion_summary": product.expert_opinion_summary,
        "risks_count": len(product.risks),
        "sources_count": len(product.sources),
        "interactions_count": len(product.interactions),
        "comments_count": len(product.comments)
    }