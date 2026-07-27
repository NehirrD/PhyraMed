from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/category",
    tags=["Category"]
)

db_dependency = Annotated[Session, Depends(get_db)]

# 1. Yeni kategori oluşturan endpoint
@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schemas.CategoryResponse,
    summary="Yeni Kategori Oluştur",
    description="Sisteme yeni bir sağlık şikayeti veya ihtiyaç kategorisi ekler (Örn: Sindirim, Uyku/Stres)."
)
async def create_category(db: db_dependency, request: schemas.CreateCategoryRequest):
    category = models.Category(
        name=request.name,
        description=request.description,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

# 2. Tüm kategorileri listeler
@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.CategoryResponse],
    summary="Tüm Kategorileri Listele",
    description="Sistemde kayıtlı olan tüm kategorileri liste halinde frontend'e döndürür."
)
async def list_categories(db: db_dependency):
    categories = db.query(models.Category).all()
    return categories

# 3. Ana sayfada popüler kategorileri gösterir
@router.get(
    "/popular", 
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.CategoryResponse],
    summary="Popüler Kategorileri Getir (Vitrin)",
    description="Kullanıcılar tarafından en çok tıklanan kategorileri, arama sayısına (search_count) göre çoktan aza doğru sıralar. Frontend ana sayfasındaki popüler kartlar için kullanılır."
)
async def list_categories_popular(db: db_dependency, limit: int = 4):
    popular_categories = db.query(models.Category).order_by(models.Category.search_count.desc()).limit(limit).all()
    return popular_categories

# 4. Tek kategori detay döner
@router.get(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CategoryResponse,
    summary="Kategori Detayını Getir",
    description="Belirtilen benzersiz ID'ye sahip kategorinin adını ve detaylı açıklamasını döndürür."
)
async def get_category(db: db_dependency, category_id: int):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

# 5. Kategoriye ait tüm ürünleri gösterir
@router.get(
    "/{category_id}/products",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ProductResponse],
    summary="Kategoriye Ait Takviyeleri Listele",
    description="Seçilen kategoriye ait bitkileri/takviyeleri listeler. Bu rota çağrıldığında kategorinin popülerlik puanı (search_count) arka planda otomatik artar. Parametreler ile isme veya kanıt seviyesine göre sıralanabilir."
)
async def get_categories_products(db: db_dependency, category_id: int, sort_by: str = "name", order: str = "asc"):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    # Görüntülenme sayısını artır (Popülerlik algoritması için)
    category.search_count += 1
    db.commit()
    
    query = db.query(models.Product).filter(models.Product.category_id == category_id)

    allowed_sort_fields = {"name": models.Product.name, "evidence_level": models.Product.evidence_level}
    sort_column = allowed_sort_fields.get(sort_by, models.Product.name)
    
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
        
    products = query.all()
    return products

# 6. Kategoriyi günceller
@router.put(
    "/{category_id}",
    status_code=status.HTTP_200_OK,
    response_model=schemas.CategoryResponse,
    summary="Kategoriyi Güncelle",
    description="Mevcut bir kategorinin ismini veya açıklamasını değiştirmek için kullanılır."
)
async def update_category(db: db_dependency, category_id: int, request: schemas.CreateCategoryRequest):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    category.name = request.name
    category.description = request.description

    db.commit()
    db.refresh(category)
    return category

# 7. Kategoriyi siler
@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Kategoriyi Sil",
    description="Belirtilen kategoriyi veritabanından kalıcı olarak kaldırır. DİKKAT: Buna bağlı ürünler varsa veritabanı ilişkisi (cascade) kuralları geçerli olur."
)
async def delete_category(db: db_dependency, category_id: int):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    db.delete(category)
    db.commit()