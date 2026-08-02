from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from models.category import Category
from models.product import Product
from schemas.search import SearchResponse


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=SearchResponse,
)
async def search(
    db: db_dependency,
    q: str = "",
):
    """Kategori ve ürün adında arama yapar; görüntüleme sayacını değiştirmez."""

    clean_query = str(q or "").strip()
    if not clean_query:
        return SearchResponse(
            categories=[],
            products=[],
        )

    categories = (
        db.query(Category)
        .filter(Category.name.ilike(f"%{clean_query}%"))
        .all()
    )
    products = (
        db.query(Product)
        .filter(Product.name.ilike(f"%{clean_query}%"))
        .all()
    )

    return SearchResponse(
        categories=categories,
        products=products,
    )
