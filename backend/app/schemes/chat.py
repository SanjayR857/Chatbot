# ─────────────────────────────────────────────
# app/models/chat.py
#
# PURPOSE: Pydantic models (schemas) for request/Response
# validation. These are the "contracts" between
# frontend ↔ backend and backend ↔ Ollama.
#
# Keeping models in their own file means:
# - Routes import from here (no circular deps)
# - Easy to version (v1 models, v2 models, etc.)
# ─────────────────────────────────────────────

from pydantic import BaseModel, Field
from typing import Literal, Optional
import datetime


# ── Shared Message shape ──────────────────────
class Message(BaseModel):
    role: Literal["user", "assistant"]   # strict — only these two values allowed
    content: str = Field(..., min_length=1)
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now().isoformat()
    )


# ── Incoming request from React frontend ──────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's new message")
    history: list[Message] = Field(
        default=[],
        description="Full conversation history so far"
    )


# ── Outgoing Response to React frontend ───────
class ChatResponse(BaseModel):
    reply: str
    timestamp: str
    model: str                           # which Ollama model responded


# ── Health check Response ─────────────────────
class HealthResponse(BaseModel):
    status: str
    ollama: str
    active_model: str
    available_models: list[str] = []
    #hint: Optional[str] = None