from fastapi import APIRouter
from pydantic import BaseModel

from ai.chatbot import get_bot_response

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = get_bot_response(request.message)
    return {"response": answer}