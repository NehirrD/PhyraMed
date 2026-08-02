from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session, selectinload
from starlette import status
from starlette.concurrency import run_in_threadpool

import models
import schemas
from ai.identify import IDENTIFY_DISCLAIMER, identify_image
from ai.image_validation import (
    ALLOWED_CONTENT_TYPES,
    MAX_IMAGE_SIZE,
    detect_image_mime,
)
from database import get_db
from models import EvidenceLevel

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)

db_dependency = Annotated[Session, Depends(get_db)]


def product_query(db: Session):
    return db.query(models.Product).options(
        selectinload(models.Product.category),
        selectinload(models.Product.risks),
        selectinload(models.Product.sources),
        selectinload(models.Product.interactions),
    )


# Yeni ürün ekleme:
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ProductResponse,
)
async def create_product(
    db: db_dependency,
    request: schemas.CreateProductRequest,
):
    product = models.Product(
        name=request.name,
        category_id=request.category_id,
        usage_purpose=request.usage_purpose,
        evidence_level=request.evidence_level,
        expert_opinion_summary=request.expert_opinion_summary,
        image_url=request.image_url,
        status=request.status,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


# Ana sayfada en çok aranan ürünleri gösterir:
@router.get(
    "/popular",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ProductResponse],
)
async def list_products_popular(
    db: db_dependency,
    limit: int = 4,
):
    return (
        product_query(db)
        .order_by(models.Product.search_count.desc())
        .limit(limit)
        .all()
    )


# Ürünleri listeler ve filtreler:
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ProductResponse],
)
async def list_products(
    db: db_dependency,
    q: str = None,
    category_id: int = None,
    evidence_level: EvidenceLevel = None,
    sort_by: str = "name",
    order: str = "asc",
):
    query = product_query(db)

    if q:
        query = query.filter(models.Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    if evidence_level:
        query = query.filter(models.Product.evidence_level == evidence_level)

    allowed_sort_fields = {
        "name": models.Product.name,
        "evidence_level": models.Product.evidence_level,
    }
    sort_column = allowed_sort_fields.get(sort_by, models.Product.name)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    return query.all()


# Görsel tanıma — fotoğraftan bitki tahmini ve katalog eşleştirmesi:
@router.post(
    "/identify",
    status_code=status.HTTP_200_OK,
    response_model=schemas.IdentifyResponse,
)
async def identify_product(file: UploadFile = File(...)):
    declared_type = (file.content_type or "").lower()

    if declared_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Sadece JPEG, PNG veya WEBP görsel yükleyebilirsiniz.",
        )

    try:
        image_bytes = await file.read(MAX_IMAGE_SIZE + 1)
    finally:
        await file.close()

    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yüklenen görsel boş.",
        )

    if len(image_bytes) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Görsel boyutu 5 MB'ı geçemez.",
        )

    detected_type = detect_image_mime(image_bytes)
    if detected_type is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosyanın gerçek biçimi JPEG, PNG veya WEBP değil.",
        )

    if detected_type != declared_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dosya türü ile görsel içeriği uyuşmuyor.",
        )

    # OpenAI/Groq istemcisi senkron çalıştığı için event loop'u bloklamaz.
    result = await run_in_threadpool(
        identify_image,
        image_bytes,
        detected_type,
    )

    return {
        **result,
        "disclaimer": IDENTIFY_DISCLAIMER,
    }


# Arama sonucunda kullanıcı tarafından seçilen ürünü bir kez sayar:
@router.post(
    "/{product_id}/search-selection",
    status_code=status.HTTP_200_OK,
    response_model=dict[str, int],
)
async def track_search_selection(
    db: db_dependency,
    product_id: int,
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.search_count = int(product.search_count or 0) + 1
    db.commit()
    db.refresh(product)

    return {
        "product_id": int(product.id),
        "search_count": int(product.search_count),
    }


# Seçilen ürün bilgisini döner:
@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProductResponse,
)
async def get_product_info(
    db: db_dependency,
    product_id: int,
):
    product = (
        product_query(db)
        .filter(models.Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product


# Ürün güncellemesi:
@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ProductResponse,
)
async def update_product(
    db: db_dependency,
    product_id: int,
    request: schemas.CreateProductRequest,
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    product.name = request.name
    product.category_id = request.category_id
    product.usage_purpose = request.usage_purpose
    product.evidence_level = request.evidence_level
    product.expert_opinion_summary = request.expert_opinion_summary
    product.image_url = request.image_url
    product.status = request.status

    db.commit()
    db.refresh(product)
    return product


# Ürünü siler:
@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    db: db_dependency,
    product_id: int,
):
    product = (
        db.query(models.Product)
        .filter(models.Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    db.delete(product)
    db.commit()
