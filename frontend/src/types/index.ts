// ─────────────────────────────────────────────
// TYPES — Shared data shapes across the app
// ─────────────────────────────────────────────

export interface Message {
  id: string;           // Unique ID for React key prop
  role: "user" | "assistant";
  content: string;
  timestamp: string;    // ISO string from server
}

export interface ChatRequest {
  message: string;
  history: Omit<Message, "id">[];   // Don't send internal IDs to server
}

export interface ChatResponse {
  reply: string;
  timestamp: string;
}

export interface ApiError {
  detail: string;
}
