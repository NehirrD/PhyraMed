from fastapi import APIRouter
from pydantic import BaseModel

from ai.chatbot import get_bot_response

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    answer = get_bot_response(request.message, request.session_id)
    return {"response": answer}


@router.delete("/sessions/{session_id}")
async def clear_session(session_id: str):
    from ai.chatbot import clear_session
    cleared = clear_session(session_id)
    return {"cleared": cleared, "session_id": session_id}