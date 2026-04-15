# langGraph-hello-world

A minimal end-to-end demo wiring together:

- **Django + DRF** — web app with an authenticated chat UI and a small REST API serving pre-canned knowledge-base articles and a product catalog
- **MCP server (HTTP/SSE)** — exposes tools that wrap the Django API
- **LangGraph agent** — a ReAct agent that uses the MCP tools to perform RAG over the API and answer chat prompts
- **LLM** — local Ollama (`gemma4:26b` by default)

```
            browser
               │
      POST /chat/send/ {message}
               │
               ▼
┌─────────────────────────────────────────────────────────┐
│  app  (Docker: port 8000)                               │
│                                                         │
│  ┌─────────────────────────┐                            │
│  │ Django (Chat UI + API)  │ ◄──── HTTP + Token auth ───────┐
│  └────────────┬────────────┘   (/api/articles,products) │   │
│               │ run_agent(message)                      │   │
│               ▼                                         │   │
│  ┌─────────────────────────┐                            │   │
│  │ LangGraph ReAct agent   │                            │   │
│  │ (langchain-ollama)      │                            │   │
│  └────────────┬────────────┘                            │   │
└───────────────│─────────────────────────────────────────┘   │
                │ MCP tool calls (SSE)                        │
                ▼                                             │
┌──────────────────────────────┐                              │
│  mcp-server (Docker: 8001)   │                              │
│  FastMCP / SSE               │──────────────────────────────┘
│  search_knowledge_base, ...  │
└──────────────────────────────┘
                                        ┌──────────────────┐
            app ── langchain-ollama ──► │  Ollama (host)   │
                                        └──────────────────┘
```

## Project layout

```
chatproject/      Django project settings & root urls
chat/             Web UI app — login + chat page + chat_send Django views
api/              DRF app — KB articles + product catalog endpoints
mcp_server/       FastMCP server exposing the Django API as MCP tools
agent/            LangGraph ReAct agent runner
bootstrap_demo.py Creates a demo user + DRF token, writes .env
```

## Getting started (Docker Compose)

**Prerequisites:** Docker, Docker Compose, and an [Ollama](https://ollama.com/)
server running on the host (default model: `gemma4:26b`).

```bash
# 1. Build and start all services
docker compose up --build

# 2. Bootstrap the demo user and API token (first time only)
docker compose exec app python bootstrap_demo.py
```

`bootstrap_demo.py` creates a `demo` / `demo12345` user with a DRF token and
writes `MCP_API_TOKEN` to `.env`. The MCP server uses this token to
authenticate against the Django API.

(optional) You can override any setting in `.env`:

```dotenv
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=gemma4:26b
MCP_SERVER_URL=http://mcp-server:8001/sse
DJANGO_API_BASE_URL=http://app:8000
MCP_API_TOKEN=<written by bootstrap_demo.py>
```


### Running without Docker

You need **two processes** running in addition to your Ollama server:

**Terminal 1 — Django:**
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python bootstrap_demo.py
python manage.py runserver
```

**Terminal 2 — MCP server:**
```bash
source .venv/bin/activate
python -m mcp_server.server
```

### Try it out

Open <http://localhost:8000/> in a browser, sign in as `demo` /
`demo12345`, and chat. Example questions:

- "How do I reset my password?"
- "What's your refund policy?"
- "What hardware widgets do you sell?"
- "How long does shipping take?"

## API endpoints

All endpoints require `Authorization: Token <token>` (or a session cookie):

| Method | Path                          | Description                       |
|--------|-------------------------------|-----------------------------------|
| GET    | `/api/articles/`              | List KB articles (`?category=`)   |
| GET    | `/api/articles/search/?q=`    | Search KB articles                |
| GET    | `/api/products/`              | List products (`?category=`)      |
| GET    | `/api/products/search/?q=`    | Search products                   |

## How the pieces fit together

1. The browser POSTs `{message: ...}` to the **app** service at `/chat/send/`.
2. `chat.views.chat_send` calls `agent.runner.run_agent(message)`.
3. The agent connects to the **mcp-server** over SSE, fetches the tool list,
   and runs a `create_react_agent` loop with `ChatOllama` (on the host).
4. The model decides which MCP tool(s) to call (e.g.
   `search_knowledge_base("password reset")`).
5. The **mcp-server** makes an authenticated HTTP request back to the
   **app** service's REST API.
6. The API returns JSON; the model uses it to write a grounded reply.
7. Django returns `{reply: ...}` and the page renders it.

## Notes

- The KB and product catalog live in `api/data.py` as in-memory dataclasses.
  In a real app these would be Django models — the API contract is unchanged.
- Each chat request opens a fresh MCP client. That's fine for a demo; for
  production you'd cache the client or pre-load tools at startup.
- The DRF token is written to `.env` so the MCP server can authenticate
  automatically. Don't commit `.env`.
