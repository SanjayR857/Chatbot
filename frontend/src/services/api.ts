// ─────────────────────────────────────────────
// API SERVICE — All HTTP calls live here
// This abstracts fetch() so components stay clean
// ─────────────────────────────────────────────

import { ChatRequest, ChatResponse } from "../types";

const BASE_URL = "http://localhost:8000";

export const api = {
  /**
   * POST /chat
   * Sends user message + history to FastAPI
   * Returns bot's reply
   */
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
    const response = await fetch(`${BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",   // Tell server we're sending JSON
      },
      body: JSON.stringify(payload),           // Serialize JS object → JSON string
    });

    if (!response.ok) {
      // Parse FastAPI's error detail field
      const err = await response.json();
      throw new Error(err.detail || "Request failed");
    }

    return response.json();   // Parse JSON → JS object
  },

  /**
   * GET /health
   * Check if the backend is reachable
   */
  healthCheck: async (): Promise<{ status: string }> => {
    const response = await fetch(`${BASE_URL}/api/health`);
    return response.json();
  },

  /**
   * DELETE /chat/clear
   * Signal to backend that chat was cleared
   */
  clearChat: async (): Promise<void> => {
    await fetch(`${BASE_URL}/chat/clear`, { method: "DELETE" });
  },
};
