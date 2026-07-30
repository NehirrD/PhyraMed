from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/comments",
    tags=["Comments"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.CommentResponse])
async def get_comments(db: db_dependency, product_id: int = None):
    query = db.query(models.Comment)
    if product_id:
        query = query.filter(models.Comment.product_id == product_id)
    comments = query.all()
    return comments

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.CommentResponse)
async def create_comment(db: db_dependency, request: schemas.CommentCreate):
    comment = models.Comment(
        product_id=request.product_id,
        user_name=request.user_name,
        content=request.content,
        rating=request.rating,
        created_at=request.created_at
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment