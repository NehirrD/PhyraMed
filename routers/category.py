from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db


router = APIRouter(
    prefix="/category",
    tags=["Category"]
)

db_dependency= Annotated[Session,Depends(get_db)]

#Yeni kategori oluşturan endpoint:
@router.post("/", status_code=status.HTTP_201_CREATED,response_model= schemas.CategoryResponse)
async def create_category(db: db_dependency,request: schemas.CreateCategoryRequest):
    category=models.Category(
        name=request.name,
        description=request.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

#Tüm kategorileri listeler:
@router.get("/",status_code=status.HTTP_200_OK,response_model=List[schemas.CategoryResponse])
async def list_categories(db:db_dependency):
    categories=db.query(models.Category).all()
    return categories

@router.get("/popular", status_code=status.HTTP_200_OK,response_model=List[schemas.CategoryResponse])
async def list_categories_popular(db: db_dependency,limit:int=4):
    popular_categories=db.query(models.Category).order_by(models.Category.search_count.desc()).limit(limit).all()
    return popular_categories





