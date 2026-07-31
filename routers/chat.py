from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.chatbot import get_bot_response


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    answer = get_bot_response(request.message)
    return {"response": answer}