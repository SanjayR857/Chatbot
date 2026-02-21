# ─────────────────────────────────────────────
# app/models/chat.py
#
# PURPOSE: All request/response schemas live here.
# Pydantic models validate input and auto-document
# the API in Swagger.
# ─────────────────────────────────────────────

from pydantic import BaseModel
from typing import Optional


class Message(BaseModel):
    """A single message in the conversation history."""
    role: str       # "user" or "assistant"
    content: str    # The message text


class ChatRequest(BaseModel):
    """Request body for POST /api/v1/chat"""
    message: str                    # New user message
    history: list[Message] = []     # Full conversation so far (optional)


class ChatResponse(BaseModel):
    """Response body for POST /api/v1/chat"""
    reply: str              # Assistant's response
    timestamp: str          # ISO 8601 timestamp
    model: str              # Which model generated this
