from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/products", status_code=status.HTTP_200_OK, response_model=List[schemas.ProductResponse])
async def search_products(db: db_dependency, q: str = None, category_id: int = None, evidence_level: models.EvidenceLevel = None):
    """Ürün arama - isim, kategori ve kanıt seviyesine göre"""
    query = db.query(models.Product)
    
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if evidence_level:
        query = query.filter(models.Product.evidence_level == evidence_level)
    
    products = query.all()
    return products