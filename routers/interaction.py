from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
import models
import schemas
from database import get_db

router=APIRouter(
    prefix="/interaction",
    tags=["Interaction"]
)

db_dependency=Annotated[Session,Depends(get_db)]

#Yeni interaction ekler:
@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_interaction(db:db_dependency,request:schemas.CreateInteractionRequest):
    interaction=models.Interaction(
        product_id=request.product_id,
        interacts_with=request.interacts_with,
        description=request.description
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction

#Tek etkileşim detay:
@router.get("/{interaction_id}",status_code=status.HTTP_200_OK,response_model=schemas.InteractionResponse)
async def get_interaction(db:db_dependency,interaction_id: int):
    interaction=db.query(models.Interaction).filter(models.Interaction.id==interaction_id).first()
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return interaction

#Etkileşimi siler:
@router.delete("/{interaction_id}",status_code=status.HTTP_200_OK)
async def delete_interaction(db:db_dependency,interaction_id: int):
    interaction=db.query(models.Interaction).filter(models.Interaction.id==interaction_id).first()
    if interaction is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    db.delete(interaction)
    db.commit()


