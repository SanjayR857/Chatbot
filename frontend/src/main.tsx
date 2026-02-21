// ─────────────────────────────────────────────
// main.tsx — App Entry Point
// React's starting point: mounts <App /> into #root div
// ─────────────────────────────────────────────

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

// StrictMode: helps catch bugs in development
// (renders components twice to detect side effects)
createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
