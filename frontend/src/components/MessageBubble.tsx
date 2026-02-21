// ─────────────────────────────────────────────
// MessageBubble — Renders a single chat message
// ─────────────────────────────────────────────

import { Message } from "../types";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  const time = new Date(message.timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: "12px",
        animation: "slideIn 0.2s ease-out",
      }}
    >
      {/* Bot Avatar */}
      {!isUser && (
        <div style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "16px",
          marginRight: "8px",
          flexShrink: 0,
          boxShadow: "0 0 12px rgba(99,102,241,0.4)",
        }}>
          🤖
        </div>
      )}

      <div style={{ maxWidth: "70%", display: "flex", flexDirection: "column", alignItems: isUser ? "flex-end" : "flex-start" }}>
        {/* Bubble */}
        <div style={{
          padding: "12px 16px",
          borderRadius: isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          background: isUser
            ? "linear-gradient(135deg, #6366f1, #8b5cf6)"
            : "rgba(255,255,255,0.07)",
          color: "#f1f5f9",
          fontSize: "14px",
          lineHeight: "1.5",
          border: isUser ? "none" : "1px solid rgba(255,255,255,0.1)",
          backdropFilter: "blur(10px)",
          boxShadow: isUser
            ? "0 4px 15px rgba(99,102,241,0.3)"
            : "0 2px 8px rgba(0,0,0,0.2)",
          wordBreak: "break-word",
        }}>
          {message.content}
        </div>

        {/* Timestamp */}
        <span style={{
          fontSize: "11px",
          color: "rgba(148,163,184,0.6)",
          marginTop: "4px",
          padding: "0 4px",
        }}>
          {time}
        </span>
      </div>

      {/* User Avatar */}
      {isUser && (
        <div style={{
          width: "32px",
          height: "32px",
          borderRadius: "50%",
          background: "linear-gradient(135deg, #f472b6, #e11d48)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: "16px",
          marginLeft: "8px",
          flexShrink: 0,
        }}>
          👤
        </div>
      )}
    </div>
  );
}
