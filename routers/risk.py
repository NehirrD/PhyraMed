from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/risks",
    tags=["Risks"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.RiskResponse])
async def get_risks(db: db_dependency):
    risks = db.query(models.Risk).all()
    return risks

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.RiskResponse)
async def create_risk(db: db_dependency, request: schemas.RiskCreate):
    risk = models.Risk(
        product_id=request.product_id,
        description=request.description,
        severity=request.severity
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk