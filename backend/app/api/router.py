# ─────────────────────────────────────────────
# app/api/router.py
#
# PURPOSE: Master router — imports all sub-routers
# and registers them with a version prefix.
#
# To add a new feature (e.g. /users):
#   1. Create app/api/routes/users.py
#   2. Import and include it here — done.
# ─────────────────────────────────────────────

from fastapi import APIRouter
from app.api.routes import chat, health, auth

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health.router)   # GET /api/v1/health
api_router.include_router(chat.router)     # POST /api/v1/chat
api_router.include_router(auth.router)
