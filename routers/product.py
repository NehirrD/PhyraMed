from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from starlette import status
import models
import schemas
from database import get_db
from fastapi_cache.decorator import cache  # 🚀 Cache kütüphanesi eklendi

router = APIRouter(
    prefix="/product",  # Seeder.py ile uyumlu kalması için tekil bırakıldı
    tags=["Products"]
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
        evidence_summary=request.evidence_summary,  # Bizim düzeltmemiz
        image_url=request.image_url,
        status=request.status
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.ProductResponse])
@cache(expire=60) 
async def list_products(db: db_dependency, q: str = None, category_id: int = None, evidence_level: str = None, sort_by: str = "name", order: str = "asc"):
    query = db.query(models.Product)
    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if evidence_level:
        query = query.filter(models.Product.evidence_level == evidence_level)
    
    allowed_sort_fields = {
        "name": models.Product.name,
        "evidence_level": models.Product.evidence_level
    }
    sort_column = allowed_sort_fields.get(sort_by, models.Product.name)
    
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
        

    products = query.options(
        selectinload(models.Product.risks),
        selectinload(models.Product.sources),
        selectinload(models.Product.comments)
    ).all()
    
    return products


@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.ProductResponse)
async def get_product_info(db: db_dependency, product_id: int):

    product = db.query(models.Product).options(
        selectinload(models.Product.risks),
        selectinload(models.Product.sources),
        selectinload(models.Product.comments) 
    ).filter(models.Product.id == product_id).first()
    
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.put("/{product_id}", status_code=status.HTTP_200_OK, response_model=schemas.ProductResponse)
async def update_product(db: db_dependency, product_id: int, request: schemas.CreateProductRequest):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        
    product.name = request.name
    product.category_id = request.category_id
    product.usage_purpose = request.usage_purpose
    product.evidence_level = request.evidence_level
    product.evidence_summary = request.evidence_summary  
    product.image_url = request.image_url
    product.status = request.status

    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(db: db_dependency, product_id: int):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    db.delete(product)
    db.commit()