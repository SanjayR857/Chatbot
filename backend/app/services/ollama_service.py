# ─────────────────────────────────────────────
# app/services/ollama_service.py
#
# PURPOSE: All Ollama API communication lives here.
# Routes call this service — they don't do HTTP themselves.
#
# WHY a service layer?
# - Swap Ollama → OpenAI → Claude by editing ONE file
# - Easy to unit-test (mock this service in tests)
# - Routes stay thin and readable
# ─────────────────────────────────────────────

import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.models.chat import Message


class OllamaService:
    """Handles all communication with the local Ollama server."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model    = settings.OLLAMA_MODEL
        self.timeout  = settings.OLLAMA_TIMEOUT

    # ── Private: build message list ──────────
    def _build_messages(
        self,
        user_message: str,
        history: list[Message],
    ) -> list[dict]:
        """
        Converts our internal Message objects into the
        format Ollama's /api/chat endpoint expects:
        [
          {"role": "system",    "content": "..."},
          {"role": "user",      "content": "..."},
          {"role": "assistant", "content": "..."},
          {"role": "user",      "content": "<new message>"},
        ]
        """
        messages = [{"role": "system", "content": settings.SYSTEM_PROMPT}]

        # Append history (skip timestamp — Ollama doesn't need it)
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})

        # New user message goes last
        messages.append({"role": "user", "content": user_message})
        return messages

    # ── Public: generate reply ────────────────
    async def generate_reply(
        self,
        user_message: str,
        history: list[Message],
    ) -> str:
        """
        Calls Ollama /api/chat and returns the assistant's reply text.
        Raises HTTPException on failure so FastAPI can return proper errors.
        """
        payload = {
            "model": self.model,
            "messages": self._build_messages(user_message, history),
            "stream": False,
            "options": {
                "temperature": settings.OLLAMA_TEMPERATURE,
                "num_predict": settings.OLLAMA_MAX_TOKENS,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Cannot reach Ollama. Is it running? Try: `ollama serve`",
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail=f"Ollama timed out after {self.timeout}s. Try a smaller model.",
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Ollama returned {response.status_code}: {response.text}",
            )

        data = response.json()
        return data["message"]["content"]

    # ── Public: list available models ─────────
    async def list_models(self) -> list[str]:
        """Returns names of all locally pulled Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []


# Single shared instance (acts like a singleton)
ollama_service = OllamaService()