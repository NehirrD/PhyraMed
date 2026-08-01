from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ai.chatbot import get_bot_response


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


class ChatHistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(
        min_length=1,
        max_length=4000,
    )


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )
    history: list[ChatHistoryMessage] = Field(
        default_factory=list,
        max_length=8,
    )


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    answer = get_bot_response(
        request.message,
        history=[
            message.model_dump()
            for message in request.history
        ],
    )
    return {"response": answer}
