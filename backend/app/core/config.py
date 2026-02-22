# ─────────────────────────────────────────────
# app/core/config.py
#
# PURPOSE: Central configuration using Pydantic Settings.
# All env variables / constants live HERE — never scattered
# across files. Change one place, affects the whole app.
#
# Usage anywhere in the app:
#   from app.core.config import settings
#   print(settings.OLLAMA_MODEL)
# ─────────────────────────────────────────────

from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv
import os 
load_dotenv()

class Settings(BaseSettings):
    # ── App Info ──────────────────────────────
    APP_NAME: str = "ChatterBot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── CORS ──────────────────────────────────
    # Comma-separated origins allowed to call the API
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ── Ollama ────────────────────────────────
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL')
    OLLAMA_MODEL: str =  os.getenv('OLLAMA_MODEL')        # change to your pulled model
    OLLAMA_TIMEOUT: int = 60              # seconds before giving up
    OLLAMA_TEMPERATURE: float = 0      # 0 = deterministic, 1 = creative
    OLLAMA_MAX_TOKENS: int = 4000

    # ── System Prompt ─────────────────────────
    SYSTEM_PROMPT: str = (
        "You are ChatterBot, a friendly and helpful AI assistant. "
        "Keep replies concise and conversational."
    )

    # Reads from a .env file automatically if present
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Single instance used across the entire app
settings = Settings()