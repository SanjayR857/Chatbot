// ─────────────────────────────────────────────
// useChat HOOK — All chat logic lives here
// Keeps components clean (separation of concerns)
// ─────────────────────────────────────────────

import { useState, useCallback } from "react";
import { Message } from "../types";
import { api } from "../services/api";

// Helper: generate a random ID for each message
const generateId = () => Math.random().toString(36).slice(2, 9);

export function useChat() {
  // ── State ───────────────────────────────────
  const [messages, setMessages] = useState<Message[]>([
    {
      id: generateId(),
      role: "assistant",
      content: "Hello! I'm ChatterBot. How can I help you today? 🤖",
      timestamp: new Date().toISOString(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState<boolean | null>(null);

  // ── Actions ─────────────────────────────────

  /**
   * sendMessage — Core action
   * 1. Add user message to state immediately (optimistic update)
   * 2. Call API
   * 3. Add bot reply to state
   */
  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    setError(null);

    // 1. Add user message immediately (feels responsive)
    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 2. Call FastAPI — send message + history (without IDs)
      const history = messages.map(({ role, content, timestamp }) => ({
        role,
        content,
        timestamp,
      }));

      const response = await api.sendMessage({
        message: content,
        history,
      });

      // 3. Add bot reply
      const botMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: response.reply,
        timestamp: response.timestamp,
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to connect";
      setError(errorMessage);
    } finally {
      setIsLoading(false);   // Always runs — loading spinner stops
    }
  }, [messages, isLoading]);

  /**
   * clearChat — Reset conversation
   */
  const clearChat = useCallback(async () => {
    await api.clearChat();
    setMessages([
      {
        id: generateId(),
        role: "assistant",
        content: "Chat cleared! Fresh start. How can I help? 🔄",
        timestamp: new Date().toISOString(),
      },
    ]);
    setError(null);
  }, []);

  /**
   * checkConnection — Ping the backend
   */
  const checkConnection = useCallback(async () => {
    try {
      await api.healthCheck();
      setIsConnected(true);
    } catch {
      setIsConnected(false);
    }
  }, []);

  return {
    messages,
    isLoading,
    error,
    isConnected,
    sendMessage,
    clearChat,
    checkConnection,
  };
}
