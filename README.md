# Ollive Inference Platform

A production-minded LLM chat application with **inference observability**: a logging SDK wraps every model call, ships metadata to an ingestion API, and persists telemetry for analytics dashboards.

Built for the Ollive engineering assignment — focused on **system design, logging pipelines, and schema tradeoffs**, not just a chatbot UI.

---

## Architecture

```text
Frontend (Next.js) → Backend API (FastAPI) → SDK Wrapper → Ingestion (POST /logs) → Database
                                                                              ├── MySQL (local dev)
                                                                              └── PostgreSQL (Docker Compose)
```

| Layer | Responsibility |
|-------|----------------|
| **Frontend** | Chat UI, conversation sidebar, cancel, SSE streaming, metrics dashboard |
| **Chat API** | Conversations, multi-turn context (last 10 msgs), provider routing |
| **SDK** | `InstrumentedLLMClient` — latency, tokens, status, previews, async log shipping |
| **Ingestion** | `POST /logs` — validate & store inference metadata |
| **Database** | `conversations`, `chat_messages`, `inference_logs` |

See [ARCHITECTURE.md](./ARCHITECTURE.md) for ingestion flow, logging strategy, scaling, and failure handling.

---

## Features

### Required
- Multi-turn chat with short context window
- Inference logging SDK (metadata capture + near-real-time ingestion)
- Ingestion pipeline with Pydantic validation
- Relational storage for messages + inference logs (MySQL or PostgreSQL via SQLAlchemy)

### Auth & UI
- **JWT authentication** — register, login, protected chat
- **Per-user conversations** scoped by `user_id`
- **Profile & settings** — display name, bio, default provider/model
- **Modern multi-page UI** — landing, login, chat, metrics, profile

### Bonus (implemented)
- **Docker Compose** — one-command setup
- **Streaming** — Server-Sent Events from `POST /chat`
- **Multi-provider** — OpenAI, Anthropic, Gemini + Mock (no API key)
- **Dashboard** — latency, throughput, error rate (Recharts)
- **PII redaction** — email/phone/SSN stripped from log previews
- **Cancel request** — `AbortController` on frontend

---

## Quick Start (Docker)

**Prerequisites:** Docker Desktop

```bash
git clone <your-repo-url>
cd CHATBOT
cp .env.example .env
# Optional: add OPENAI_API_KEY and set DEFAULT_PROVIDER=openai

docker compose up --build
```

| Service | URL |
|---------|-----|
| Home | http://localhost:3000 |
| Login | http://localhost:3000/login |
| Chat | http://localhost:3000/chat |
| Profile | http://localhost:3000/profile |
| Settings | http://localhost:3000/settings |
| Dashboard | http://localhost:3000/dashboard |
| API docs | http://localhost:8000/docs |

**Demo without API keys:** defaults to `mock` provider — fully functional for evaluation.

**Database in Docker:** `docker-compose.yml` runs **PostgreSQL 16**. Tables are created automatically on backend startup.

**With OpenAI:**

```env
OPENAI_API_KEY=sk-...
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
```

---

## Database

| Environment | Engine | Connection string (example) |
|-------------|--------|-----------------------------|
| **Local dev (recommended)** | MySQL 8 | `mysql+aiomysql://root:PASSWORD@localhost:3306/ollive` |
| **Docker Compose** | PostgreSQL 16 | `postgresql+asyncpg://ollive:ollive@db:5432/ollive` |
| **Optional fallback** | SQLite | `sqlite+aiosqlite:///./backend/data/ollive.db` |

Copy `.env.example` to `.env` at the repo root (gitignored). Use URL-encoded passwords in `DATABASE_URL` if they contain special characters (`@`, `$`, etc.).

---

## Local Development (without Docker)

### Windows quick start (recommended)

**1. MySQL** — create database (MySQL Workbench or CLI):

```sql
CREATE DATABASE IF NOT EXISTS ollive CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**2. Configure** — copy `.env.example` to `.env` at the repo root and set MySQL credentials:

```env
DATABASE_URL=mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/ollive
JWT_SECRET=change-me-to-a-long-random-secret-key
```

**3. Start** — use **Command Prompt** (`.bat` files avoid PowerShell script blocks):

```cmd
scripts\start-backend.bat
```

Second terminal:

```cmd
scripts\start-frontend.bat
```

Verify: http://localhost:8000/health → `"database": "connected"`

**Upgrading an existing MySQL database?** Run:

```bash
mysql -u root -p < backend/db/migrate_add_users.sql
```

Then restart the backend (creates any missing tables via SQLAlchemy).

If `Activate.ps1` fails with *running scripts is disabled*, do **not** use `activate` — use the scripts above or:

```powershell
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### Backend (manual)

```bash
cd backend
python -m venv .venv
# Windows — install into venv without activating:
.venv\Scripts\pip install -r requirements.txt

set PYTHONPATH=%CD%\backend
set DATABASE_URL=mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/ollive
set INGESTION_URL=http://localhost:8000/logs
set JWT_SECRET=change-me-to-a-long-random-secret-key
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

For PostgreSQL instead of MySQL, run Postgres locally or use `docker compose up db` and set `DATABASE_URL=postgresql+asyncpg://ollive:ollive@localhost:5432/ollive`.

### Frontend

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/auth/register` | Create account |
| `POST` | `/auth/login` | Login (JWT) |
| `GET` | `/auth/me` | Current user profile |
| `POST` | `/chat` | Send message (JSON or SSE stream) |
| `GET` | `/conversations` | List conversations |
| `GET` | `/conversations/{id}` | Get messages |
| `DELETE` | `/conversations/{id}` | Delete conversation |
| `POST` | `/logs` | Ingestion endpoint (SDK target) |
| `GET` | `/metrics` | Aggregated observability metrics |
| `GET` | `/providers` | List providers + default models |
| `GET` | `/health` | Health check |

---

## SDK Usage

The core assignment artifact — wrap any provider call:

```python
from app.providers.registry import get_provider
from app.sdk.llm_client import InstrumentedLLMClient
from app.providers.base import LLMMessage

provider = get_provider("openai")
client = InstrumentedLLMClient(provider)

result = await client.generate(
    model="gpt-4o-mini",
    messages=[LLMMessage(role="user", content="Hello")],
    conversation_id=conversation_uuid,
    request_id=request_uuid,
)
# Logs are sent asynchronously to POST /logs — never blocks the response
```

Captured metadata: `request_id`, `conversation_id`, `provider`, `model`, token counts, `latency_ms`, `status`, `error_message`, redacted previews, timestamp.

---

## Database Schema

```sql
-- users (JWT auth)
id UUID PK, email, username, hashed_password, display_name, bio,
default_provider, default_model, theme, created_at

-- conversations
id UUID PK, user_id FK (nullable for legacy rows), title, created_at, updated_at

-- chat_messages
id UUID PK, conversation_id FK, role, content, timestamp

-- inference_logs
id UUID PK, request_id, conversation_id FK (nullable, ON DELETE SET NULL),
provider, model, prompt_tokens, completion_tokens, total_tokens,
latency_ms, status, error_message, input_preview, output_preview, created_at
```

**Tradeoffs:**
- Previews instead of full prompts → storage cost & privacy
- Append-only logs → simple analytics, no update races
- Direct HTTP ingestion vs Kafka → faster to ship; document upgrade path in ARCHITECTURE.md

---

## Tradeoffs

| Decision | Why |
|----------|-----|
| HTTP ingestion vs message queue | Simpler for assignment; Kafka noted for production |
| Monolith backend | Chat + ingestion share DB; easy deploy |
| Mock provider default | Evaluators can run without secrets |
| Log after stream completes | Accurate token/latency for streaming |
| Fire-and-forget logging | User latency unaffected by observability path |

---

## What I'd Improve With More Time

1. **Kafka ingestion** — buffer logs, replay on failure, horizontal consumers
2. **OpenTelemetry** — trace IDs linking frontend → chat → SDK → ingestion
3. **Rate limiting & tenant API keys** — JWT exists; add per-tenant quotas
4. **Log retention policies** — partition `inference_logs` by month
5. **Integration tests** — SDK contract tests + ingestion idempotency
6. **Hosted demo** — Fly.io / Railway deployment with CI

---

## Project Structure

```text
CHATBOT/
├── frontend/          # Next.js + Tailwind + Recharts dashboard
├── backend/
│   └── app/
│       ├── api/       # chat, conversations, logs, metrics
│       ├── sdk/       # InstrumentedLLMClient + PII redaction
│       ├── ingestion/ # log persistence handler
│       ├── providers/ # OpenAI, Anthropic, Gemini, Mock
│       ├── services/  # chat + metrics business logic
│       └── db/        # SQLAlchemy models
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```

---

## Submission Checklist

- [x] GitHub repository with full source
- [x] README (setup, architecture, schema, tradeoffs)
- [x] ARCHITECTURE.md (ingestion, logging, scaling, failures)
- [ ] Demo link / screenshots / Loom (add after deploy)

**Submit to:** work@ollive.ai

---

## License

MIT — built as a take-home assignment submission.
#   O l i v e - A s s i g n m e n t  
 