from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router= APIRouter(
    prefix="/sources",
    tags=["Source"]
)

db_dependency=Annotated[Session,Depends(get_db)]

#Yeni kaynak oluşturur:
@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.SourceResponse)
async def create_source(db:db_dependency,request:schemas.CreateSourceRequest):
    product=db.query(models.Product).filter(models.Product.id==request.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Product not found")
    source=models.Source(
        product_id=request.product_id,
        type=request.type,
        url=request.url,
        title=request.title
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source

#Tek kaynak detaylarını döner:
@router.get("/{source_id}",status_code=status.HTTP_200_OK,response_model=schemas.SourceResponse)
async def get_source(source_id:int,db:db_dependency):
    source=db.query(models.Source).filter(models.Source.id==source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Source not found")
    return source

#Kaynak bilgilerini günceller:
@router.put("/{source_id}",status_code=status.HTTP_200_OK,response_model=schemas.SourceResponse)
async def update_source(db:db_dependency,source_id:int,request:schemas.CreateSourceRequest):
    source=db.query(models.Source).filter(models.Source.id==source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Source not found")
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    source.product_id=request.product_id
    source.type=request.type
    source.url=request.url
    source.title=request.title

    db.commit()
    db.refresh(source)
    return source

#Kaynak kaydını sil:
@router.delete("/{source_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(db:db_dependency,source_id:int):
    source=db.query(models.Source).filter(models.Source.id==source_id).first()
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Source not found")
    db.delete(source)
    db.commit()

