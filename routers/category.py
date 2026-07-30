from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.CategoryResponse])
async def get_categories(db: db_dependency):
    categories = db.query(models.Category).all()
    return categories

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CategoryResponse)
async def create_category(db: db_dependency, request: schemas.CategoryCreate):
    category = models.Category(name=request.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category