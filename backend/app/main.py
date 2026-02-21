# ─────────────────────────────────────────────
# app/main.py
#
# PURPOSE: App factory — creates and configures the
# FastAPI instance. This file should stay CLEAN.
# No route logic, no business logic — just wiring.
# ─────────────────────────────────────────────

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.router import api_router


def create_app() -> FastAPI:
    """
    Factory function that builds the FastAPI app.
    Using a factory makes it easy to create test instances
    with different configs.
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="AI Chatbot powered by Ollama running locally",
        docs_url="/docs",       # Swagger UI  → http://localhost:8000/docs
        redoc_url="/redoc",     # ReDoc UI    → http://localhost:8000/redoc
    )

    # ── Middleware ──────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ─────────────────────────────────
    # All routes live under /api/v1/*
    app.include_router(api_router)

    # Root redirect
    from app.api.routes.health import root
    app.get("/")(root)

    return app


# The app instance — uvicorn points at this
app = create_app()