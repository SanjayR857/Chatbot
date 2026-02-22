# ─────────────────────────────────────────────
# app/api/routes/chat.py
#
# PURPOSE: Only the /chat endpoint lives here.
# Routes are thin — they validate input, call the
# service, and return the response. Zero business logic.
# ─────────────────────────────────────────────

import datetime
from fastapi import APIRouter

from app.schemes.chat import ChatRequest, ChatResponse
from app.services.ollama_service import ollama_service
from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Send a message and get an AI reply.

    - **message**: the user's new message
    - **history**: full conversation so far (for context)
    """
    reply = await ollama_service.generate_reply(
        user_message=request.message,
        history=request.history,
    )

    return ChatResponse(
        reply=reply,
        timestamp=datetime.datetime.now().isoformat(),
        model=settings.OLLAMA_MODEL,
    )


@router.delete("/clear")
async def clear_chat():
    """
    Signal endpoint — history is managed on the client.
    Call this to notify backend a session was cleared.
    """
    return {"status": "cleared", "message": "Chat history cleared on client"}