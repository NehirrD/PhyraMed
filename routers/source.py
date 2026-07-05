#routers/source.py
# POST/sources Yeni kaynak/atıf ekle
# #GET/products/{product_id}/sources Bir ürünün kaynaklarını listele
# #GET/sources/{source_id}Tek kaynak detay
# #PUT/sources/{source_id}Kaynak güncelle
# #DELETE/sources/{source_id}Kaynak sil

from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db
from routers.risk import db_dependency

router= APIRouter(
    prefix="/source",
    tags=["Source"]
)

db_dependency=Annotated[Session,Depends(get_db)]

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.SourceResponse)
async def create_source(db:db_dependency,product_id:int,request:schemas.CreateSourceRequest):
    product=db.query(models.Product).filter(models.Product.id==product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    source=models.Source(
        product_id=request.product.id,
        type=request.type,
        url=request.url,
        title=request.title
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


