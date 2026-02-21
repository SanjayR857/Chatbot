# ─────────────────────────────────────────────
# app/api/routes/health.py
#
# PURPOSE: Health check endpoints to verify both
# FastAPI and Ollama are running and healthy.
# ─────────────────────────────────────────────

import httpx
from fastapi import APIRouter

from app.core.config import settings
from app.services.ollama_service import ollama_service


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Checks both FastAPI AND Ollama are reachable.
    Returns which models are available locally.
    """
    try:
        models = await ollama_service.list_models()
        return {
            "status": "healthy",
            "ollama": "connected",
            "active_model": settings.OLLAMA_MODEL,
            "available_models": models,
        }
    except Exception as e:
        return {
            "status": "degraded",
            "ollama": f"unreachable — {str(e)}",
            "hint": "Make sure Ollama is running: `ollama serve`",
        }


async def root():
    """
    Root endpoint — simple greeting.
    """
    return {
        "message": "Welcome to ChatterBot API",
        "docs": "Visit /docs for interactive API documentation",
    }