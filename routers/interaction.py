from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"]
)

db_dependency = Annotated[Session,Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.InteractionResponse])
async def get_interactions(db: db_dependency):
    interactions = db.query(models.Interaction).all()
    return interactions

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.InteractionResponse)
async def create_interaction(db: db_dependency, request: schemas.InteractionCreate):
    interaction = models.Interaction(
        product_id=request.product_id,
        interacts_with=request.interacts_with,
        description=request.description
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction