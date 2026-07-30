from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/sources",
    tags=["Sources"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.SourceResponse])
async def get_sources(db: db_dependency):
    sources = db.query(models.Source).all()
    return sources

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.SourceResponse)
async def create_source(db: db_dependency, request: schemas.SourceCreate):
    source = models.Source(
        product_id=request.product_id,
        title=request.title,
        url=request.url
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source