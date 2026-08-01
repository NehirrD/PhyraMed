from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.product import Product
from models.comment import Comment
from schemas.comment import CommentCreate, CommentResponse
from typing import List

router = APIRouter(prefix="/comment", tags=["Comments"])

@router.get("/{product_id}", status_code=status.HTTP_200_OK, response_model=List[CommentResponse])
async def list_comments(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    comments = (
        db.query(Comment)
        .filter(Comment.product_id == product_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return comments
@router.post("/{product_id}", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def add_comment(product_id: int, request: CommentCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    new_comment = Comment(
        product_id=product_id,
        user_name=request.user_name,
        text=request.text,
        rating=request.rating
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment