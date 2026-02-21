// ─────────────────────────────────────────────
// TypingIndicator — Animated dots shown while
// waiting for the bot's response
// ─────────────────────────────────────────────

export function TypingIndicator() {
  return (
    <div style={{
      display: "flex",
      alignItems: "center",
      gap: "8px",
      marginBottom: "12px",
    }}>
      {/* Bot Avatar */}
      <div style={{
        width: "32px",
        height: "32px",
        borderRadius: "50%",
        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "16px",
        flexShrink: 0,
      }}>
        🤖
      </div>

      {/* Bouncing dots bubble */}
      <div style={{
        padding: "14px 18px",
        borderRadius: "18px 18px 18px 4px",
        background: "rgba(255,255,255,0.07)",
        border: "1px solid rgba(255,255,255,0.1)",
        display: "flex",
        gap: "5px",
        alignItems: "center",
      }}>
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              width: "8px",
              height: "8px",
              borderRadius: "50%",
              background: "#8b5cf6",
              animation: `bounce 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
    </div>
  );
}
