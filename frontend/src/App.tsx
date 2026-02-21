// ─────────────────────────────────────────────
// App.tsx — Root component
// Composes everything together
// ─────────────────────────────────────────────

import { useState, useEffect, useRef, KeyboardEvent } from "react";
import { useChat } from "./hooks/useChat";
import { MessageBubble } from "./components/MessageBubble";
import { TypingIndicator } from "./components/TypingIndicator";

export default function App() {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const { messages, isLoading, error, isConnected, sendMessage, clearChat, checkConnection } = useChat();

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Check backend connection on mount
  useEffect(() => {
    checkConnection();
  }, [checkConnection]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const msg = input;
    setInput("");             // Clear input immediately
    await sendMessage(msg);
    inputRef.current?.focus();
  };

  // Send on Enter (Shift+Enter = new line)
  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
      padding: "20px",
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 2px; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0.7); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
        textarea:focus { outline: none; }
        textarea { resize: none; }
      `}</style>

      {/* ── Chat Window ── */}
      <div style={{
        width: "100%",
        maxWidth: "720px",
        height: "calc(100vh - 40px)",
        maxHeight: "800px",
        display: "flex",
        flexDirection: "column",
        borderRadius: "24px",
        overflow: "hidden",
        border: "1px solid rgba(255,255,255,0.08)",
        boxShadow: "0 25px 80px rgba(0,0,0,0.5), 0 0 0 1px rgba(99,102,241,0.1)",
        backdropFilter: "blur(20px)",
        background: "rgba(15,12,41,0.85)",
      }}>

        {/* ── Header ── */}
        <div style={{
          padding: "20px 24px",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(99,102,241,0.05)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            <div style={{
              width: "44px",
              height: "44px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "22px",
              boxShadow: "0 4px 15px rgba(99,102,241,0.4)",
            }}>
              🤖
            </div>
            <div>
              <h1 style={{ fontSize: "17px", fontWeight: 600, color: "#f1f5f9", letterSpacing: "-0.3px" }}>
                ChatterBot
              </h1>
              {/* Connection status indicator */}
              <div style={{ display: "flex", alignItems: "center", gap: "5px" }}>
                <div style={{
                  width: "7px",
                  height: "7px",
                  borderRadius: "50%",
                  background: isConnected === null ? "#fbbf24" : isConnected ? "#4ade80" : "#f87171",
                  animation: isLoading ? "pulse 1s infinite" : "none",
                }} />
                <span style={{ fontSize: "12px", color: "rgba(148,163,184,0.7)" }}>
                  {isConnected === null ? "Connecting..." : isConnected ? "Online" : "Backend Offline"}
                </span>
              </div>
            </div>
          </div>

          {/* Clear Button */}
          <button
            onClick={clearChat}
            style={{
              padding: "8px 16px",
              borderRadius: "10px",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)",
              color: "rgba(148,163,184,0.8)",
              fontSize: "13px",
              cursor: "pointer",
              transition: "all 0.2s",
            }}
            onMouseEnter={e => (e.currentTarget.style.background = "rgba(239,68,68,0.15)")}
            onMouseLeave={e => (e.currentTarget.style.background = "rgba(255,255,255,0.05)")}
          >
            🗑 Clear
          </button>
        </div>

        {/* ── Messages Area ── */}
        <div style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px 20px",
          display: "flex",
          flexDirection: "column",
        }}>
          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {/* Typing indicator appears when loading */}
          {isLoading && <TypingIndicator />}

          {/* Error banner */}
          {error && (
            <div style={{
              padding: "12px 16px",
              borderRadius: "12px",
              background: "rgba(239,68,68,0.1)",
              border: "1px solid rgba(239,68,68,0.3)",
              color: "#fca5a5",
              fontSize: "13px",
              marginBottom: "12px",
              animation: "slideIn 0.2s ease-out",
            }}>
              ⚠️ {error} — Make sure your FastAPI server is running on port 8000
            </div>
          )}

          {/* Invisible div to scroll into view */}
          <div ref={messagesEndRef} />
        </div>

        {/* ── Input Area ── */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(0,0,0,0.2)",
          display: "flex",
          gap: "12px",
          alignItems: "flex-end",
        }}>
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message... (Enter to send)"
            rows={1}
            style={{
              flex: 1,
              padding: "14px 18px",
              borderRadius: "16px",
              border: "1px solid rgba(255,255,255,0.1)",
              background: "rgba(255,255,255,0.05)",
              color: "#f1f5f9",
              fontSize: "14px",
              lineHeight: "1.5",
              fontFamily: "inherit",
              maxHeight: "120px",
              overflowY: "auto",
              transition: "border-color 0.2s",
            }}
            onFocus={e => (e.target.style.borderColor = "rgba(99,102,241,0.5)")}
            onBlur={e => (e.target.style.borderColor = "rgba(255,255,255,0.1)")}
          />

          <button
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
            style={{
              width: "48px",
              height: "48px",
              borderRadius: "14px",
              border: "none",
              background: isLoading || !input.trim()
                ? "rgba(99,102,241,0.3)"
                : "linear-gradient(135deg, #6366f1, #8b5cf6)",
              color: "white",
              fontSize: "20px",
              cursor: isLoading || !input.trim() ? "not-allowed" : "pointer",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              transition: "all 0.2s",
              flexShrink: 0,
              boxShadow: isLoading || !input.trim() ? "none" : "0 4px 15px rgba(99,102,241,0.4)",
            }}
          >
            {isLoading ? "⏳" : "➤"}
          </button>
        </div>
      </div>
    </div>
  );
}
