from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/risk",
    tags=["Risk"]
)
db_dependency = Annotated[Session, Depends(get_db)]

# --- Geliştirme aşaması için gerekli endpointler (Açıklamalar Swagger'a eklendi) ---

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED, 
    response_model=schemas.RiskResponse,
    summary="Yeni Risk Kaydı Oluştur",
    description="**Sistem Notu:** Geliştirme aşaması için gereklidir. Son kullanıcı bu uçla doğrudan etkileşime girmeyecektir. Sisteme ürünlerle ilişkili yeni bir risk tanımlar."
)
async def create_risk(db: db_dependency, request: schemas.CreateRiskRequest):
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    risk = models.Risk(
        product_id=request.product_id,
        description=request.description,
        severity=request.severity,
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk

@router.get(
    "/{risk_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=schemas.RiskResponse,
    summary="Risk Kaydını Getir",
    description="Belirtilen ID'ye sahip risk kaydının detaylarını getirir."
)
async def get_risk(db: db_dependency, risk_id: int):
    risk = db.query(models.Risk).filter(models.Risk.id == risk_id).first()
    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return risk

@router.put(
    "/{risk_id}", 
    status_code=status.HTTP_200_OK, 
    response_model=schemas.RiskResponse,
    summary="Risk Kaydını Güncelle",
    description="Mevcut bir risk kaydının açıklamasını (description) veya şiddetini (severity) günceller."
)
async def update_risk(db: db_dependency, risk_id: int, request: schemas.CreateRiskRequest):
    risk = db.query(models.Risk).filter(models.Risk.id == risk_id).first()
    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
<<<<<<< HEAD
    risk.product_id = request.product_id
    risk.description = request.description
    risk.severity = request.severity
=======
    product = db.query(models.Product).filter(models.Product.id == request.product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    risk.product_id=request.product_id
    risk.description=request.description
    risk.severity=request.severity
>>>>>>> 9c2839c8ed127a634e56ea9db5c77ee3968a6ad7
    db.commit()
    db.refresh(risk)
    return risk

@router.delete(
    "/{risk_id}", 
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Risk Kaydını Sil",
    description="Sistemdeki bir risk kaydını kalıcı olarak siler."
)
async def delete_risk(db: db_dependency, risk_id: int):
    risk = db.query(models.Risk).filter(models.Risk.id == risk_id).first()
    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(risk)
    db.commit()