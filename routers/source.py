from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/source",
    tags=["Source"]
)
db_dependency = Annotated[Session, Depends(get_db)]

# --- Geliştirme aşaması ve dokümantasyon için endpointler ---

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schemas.SourceResponse,
    summary="Yeni Kaynak (Makale/Link) Ekle",
    description="**Sistem Notu:** Sisteme bir ürünle (product) ilişkili yeni bir bilimsel kaynak, makale, URL veya literatür bilgisi ekler."
)
async def create_source(db: db_dependency, request: schemas.CreateSourceRequest):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    new_source = models.Source(
        product_id=request.product_id,
        type=request.type,
        url=request.url,
        title=request.title
    )
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source

@router.get(
    "/{source_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=schemas.SourceResponse,
    summary="Kaynak Detayını Getir",
    description="Belirtilen ID'ye sahip kaynağın (URL, başlık, tip) detaylarını veritabanından çeker."
)
async def get_source(db: db_dependency, source_id: int):
    source_item = db.query(models.Source).filter(models.Source.id == source_id).first()
    if source_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source_item

@router.put(
    "/{source_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=schemas.SourceResponse,
    summary="Kaynak Bilgilerini Güncelle",
    description="Mevcut bir kaynak kaydının başlığını, URL'sini veya tipini günceller."
)
async def update_source(db: db_dependency, source_id: int, request: schemas.CreateSourceRequest):
    source_item = db.query(models.Source).filter(models.Source.id == source_id).first()
    if source_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    
    source_item.product_id = request.product_id
    source_item.type = request.type
    source_item.url = request.url
    source_item.title = request.title
    
    db.commit()
    db.refresh(source_item)
    return source_item

@router.delete(
    "/{source_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kaynak Kaydını Sil",
    description="Sistemdeki bir kaynağı kalıcı olarak siler."
)
async def delete_source(db: db_dependency, source_id: int):
    source_item = db.query(models.Source).filter(models.Source.id == source_id).first()
    if source_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    
    db.delete(source_item)
    db.commit()