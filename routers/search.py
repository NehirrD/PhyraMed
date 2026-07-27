from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from models.category import Category
from models.product import Product
from schemas.search import SearchResponse
from database import get_db

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)

db_dependency = Annotated[Session, Depends(get_db)]

#Kategori + ürün adında birleşik arama yapar, ikisini birden döner
@router.get("/", status_code=status.HTTP_200_OK, response_model=SearchResponse)
async def search(db: db_dependency, q: str = ""):
    if not q:
        return SearchResponse(categories=[], products=[])

    categories = db.query(Category).filter(Category.name.ilike(f"%{q}%")).all()
    products = db.query(Product).filter(Product.name.ilike(f"%{q}%")).all()

    return SearchResponse(categories=categories, products=products)