# 🤖 ChatterBot — FastAPI + React (TypeScript) Chatbot

A full-stack chatbot web app broken down step by step.

---

## 📁 PROJECT STRUCTURE

```
chatbot/
├── backend/
│   ├── main.py              ← FastAPI server (all API logic)
│   └── requirements.txt     ← Python dependencies
│
└── frontend/
    ├── index.html           ← HTML shell (React mounts here)
    ├── package.json         ← Node dependencies + scripts
    ├── vite.config.ts       ← Build tool config
    ├── tsconfig.json        ← TypeScript config
    └── src/
        ├── main.tsx         ← Entry point (mounts React)
        ├── App.tsx          ← Root component (UI layout)
        ├── types/
        │   └── index.ts     ← Shared TypeScript interfaces
        ├── services/
        │   └── api.ts       ← All HTTP calls (fetch wrapper)
        ├── hooks/
        │   └── useChat.ts   ← All chat logic (custom hook)
        └── components/
            ├── MessageBubble.tsx   ← Single message UI
            └── TypingIndicator.tsx ← Animated dots
```

---

## 🔄 HOW IT ALL CONNECTS (Data Flow)

```
User types → App.tsx
           → useChat hook (sendMessage)
           → api.ts (fetch POST /chat)
           → FastAPI backend (main.py)
           → generate_reply()
           → JSON response
           → api.ts parses it
           → useChat updates state
           → React re-renders
           → MessageBubble shows reply
```

---

## 📖 STEP-BY-STEP BREAKDOWN

---

### STEP 1 — FastAPI App Setup (`backend/main.py`)

```python
app = FastAPI(title="Chatbot API")
```

**What:** Creates the web server instance.  
**Why:** FastAPI is a Python framework that automatically generates API docs and validates data.

---

### STEP 2 — CORS Middleware

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

**What:** Cross-Origin Resource Sharing policy.  
**Why:** Browsers block requests from `localhost:5173` (React) to `localhost:8000` (FastAPI) by default — CORS tells the browser "this is okay."  
**Without it:** You'd get: `Access-Control-Allow-Origin` error in browser console.

---

### STEP 3 — Pydantic Models (Data Validation)

```python
class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    reply: str
    timestamp: str
```

**What:** These are like TypeScript interfaces but for Python — they validate incoming JSON automatically.  
**Why:** If a client sends `{"message": 123}`, Pydantic rejects it (message must be a string). No manual validation needed.

---

### STEP 4 — API Endpoint

```python
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    reply = generate_reply(request.message, request.history)
    return ChatResponse(reply=reply, timestamp=...)
```

**What:** Registers a POST route at `/chat`.  
**Why `response_model`?** FastAPI automatically serializes the return value to JSON and validates its shape matches `ChatResponse`.

---

### STEP 5 — TypeScript Types (`types/index.ts`)

```typescript
export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}
```

**What:** Shared data shapes across the frontend.  
**Why:** TypeScript will error at compile time if you try to access `message.text` (it's `content`). Catches bugs before runtime.  
**`"user" | "assistant"`** is a *union type* — the value can ONLY be one of these two strings.

---

### STEP 6 — API Service Layer (`services/api.ts`)

```typescript
export const api = {
  sendMessage: async (payload: ChatRequest): Promise<ChatResponse> => {
    const response = await fetch(`${BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    return response.json();
  }
}
```

**What:** Wraps `fetch()` calls in a clean service object.  
**Why separate file?** Components shouldn't know about URLs or HTTP methods. If the API changes, you update ONE file.  
**`async/await`:** Makes asynchronous HTTP calls read like synchronous code.

---

### STEP 7 — Custom Hook (`hooks/useChat.ts`)

```typescript
export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    // 1. Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    // 2. Call API
    const response = await api.sendMessage({...});
    // 3. Add bot reply
    setMessages(prev => [...prev, botMessage]);
  }, [messages]);

  return { messages, isLoading, sendMessage };
}
```

**What:** A custom React Hook — a function that uses React state and returns data/actions.  
**Why not put this in App.tsx?** Separation of concerns. The component handles DISPLAY, the hook handles LOGIC.  
**`useState<Message[]>([])`** — Generic type tells TypeScript this array contains `Message` objects.  
**`useCallback`** — Memoizes the function so it doesn't get recreated on every render (performance).  
**`prev => [...prev, newMsg]`** — Functional update: never mutate state directly, always return new array.

---

### STEP 8 — Components

**`MessageBubble.tsx`:**
```typescript
interface Props {
  message: Message;  // TypeScript forces you to pass correct props
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";
  // Conditional styling based on sender
}
```
Each message is its own isolated component. Easy to style, test, and reuse.

**`TypingIndicator.tsx`:**
Shows animated dots using CSS `@keyframes bounce` while `isLoading` is true.

---

### STEP 9 — App.tsx (Root Component)

```typescript
const { messages, isLoading, sendMessage } = useChat();  // consume the hook

// Auto-scroll
useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages]);  // runs every time messages changes

// Keyboard shortcut
const handleKeyDown = (e) => {
  if (e.key === "Enter" && !e.shiftKey) handleSend();
};
```

**`useEffect`:** Runs side effects after render. The dependency array `[messages]` means "only run when messages changes."  
**`useRef`:** Gives direct DOM access without causing re-renders (used for scroll + focus).

---

### STEP 10 — Entry Point (`main.tsx`)

```typescript
createRoot(document.getElementById("root")!).render(
  <StrictMode><App /></StrictMode>
);
```

**What:** Finds `<div id="root">` in index.html and mounts the entire React app inside it.  
**`!`:** TypeScript non-null assertion — "trust me, this element exists."  
**`StrictMode`:** In development, renders components twice to find bugs. No effect in production.

---

## 🚀 HOW TO RUN

### Backend (Terminal 1):
```bash
cd chatbot/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
- `main` = file name (main.py)
- `app` = FastAPI instance inside it
- `--reload` = auto-restart on code changes

**API Docs auto-generated at:** http://localhost:8000/docs

### Frontend (Terminal 2):
```bash
cd chatbot/frontend
npm install
npm run dev
```
**App runs at:** http://localhost:5173

---

## 🔑 KEY CONCEPTS SUMMARY

| Concept | Where | Why |
|---|---|---|
| Pydantic models | backend/main.py | Auto-validate request/response JSON |
| CORS middleware | backend/main.py | Allow cross-origin requests from React |
| TypeScript interfaces | types/index.ts | Catch bugs at compile time |
| Service layer | services/api.ts | Isolate HTTP logic |
| Custom hook | hooks/useChat.ts | Separate logic from UI |
| useState | hooks/useChat.ts | Reactive state — UI auto-updates |
| useEffect | App.tsx | Side effects (scroll, fetch on mount) |
| useRef | App.tsx | DOM access without re-render |
| useCallback | hooks/useChat.ts | Memoize functions |
| Conditional rendering | App.tsx | Show/hide loading, errors |

---

## 🔌 REPLACING THE BOT BRAIN

To use a real AI (e.g. Claude API), replace `generate_reply()` in `main.py`:

```python
import anthropic

def generate_reply(message: str, history: list) -> str:
    client = anthropic.Anthropic(api_key="your-key")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": message}]
    )
    return response.content[0].text
```

The frontend doesn't change at all — that's the power of the service layer abstraction!
