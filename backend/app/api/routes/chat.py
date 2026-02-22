# ─────────────────────────────────────────────
# app/api/routes/chat.py
# Import paths updated: app.db.database, app.models.models
# ─────────────────────────────────────────────

import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db                  # ← updated
from app.models.models import User, ChatMessage     # ← updated
from app.schemes.chat import ChatRequest, ChatResponse
from app.services.ollama_service import ollama_service
from app.core.config import settings
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message. Requires valid Bearer token."""
    reply = await ollama_service.generate_reply(request.message, request.history)
    timestamp = datetime.datetime.now().isoformat()

    db.add(ChatMessage(user_id=current_user.id, role="user",      content=request.message))
    db.add(ChatMessage(user_id=current_user.id, role="assistant", content=reply))

    return ChatResponse(reply=reply, timestamp=timestamp, model=settings.OLLAMA_MODEL)


@router.delete("/clear")
async def clear_chat(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete all chat messages for the current user."""
    deleted = await user_service_chat_clear(db, current_user.id)
    return {"status": "cleared", "messages_deleted": deleted}


# ── inline helper (avoids circular import) ────
from sqlalchemy import delete as sql_delete

async def user_service_chat_clear(db: AsyncSession, user_id: int) -> int:
    result = await db.execute(
        sql_delete(ChatMessage).where(ChatMessage.user_id == user_id)
    )
    await db.flush()
    return result.rowcount