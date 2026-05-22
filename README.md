# Ollive Inference Platform

Production-oriented LLM chat platform with real-time inference observability, ingestion pipelines, and analytics.

This project was built for the Ollive engineering assignment with a focus on:

- LLM infrastructure design
- inference logging
- telemetry pipelines
- schema tradeoffs
- scalable backend architecture

The goal was to build more than a chatbot — the system demonstrates how modern LLM applications instrument, ingest, and analyze inference traffic in production environments.

---

# System Architecture

```text
Frontend (Next.js)
        ↓
FastAPI Chat API
        ↓
Instrumented LLM SDK
        ↓
LLM Provider (OpenAI / Anthropic / Gemini / Mock)
        ↓
Async Log Shipping
        ↓
Ingestion API (/logs)
        ↓
Database
```

## Architecture Overview

| Component | Responsibility |
|---|---|
| Frontend | Chat UI, conversation management, streaming responses, dashboards |
| Chat API | Conversation lifecycle, provider routing, context handling |
| Instrumented SDK | Captures latency, token usage, status, previews, timestamps |
| Ingestion Service | Validates and persists telemetry |
| Database | Stores conversations, messages, and inference metadata |

Additional architecture details are documented in `ARCHITECTURE.md`.

---

# Features

## Core Requirements

- Multi-turn conversations
- Short conversational memory window
- Streaming chat responses
- Inference logging middleware
- Near real-time ingestion pipeline
- Metadata extraction and storage
- Relational schema design
- Analytics endpoints

---

## Authentication & User Features

- JWT authentication
- User registration & login
- Per-user conversation history
- Resume conversations
- Delete conversations
- Profile & settings pages

---

## Observability Features

The SDK captures:

- provider
- model
- latency
- token usage
- timestamps
- request status
- error messages
- conversation/session IDs
- request/response previews

Logs are asynchronously sent to the ingestion API to avoid blocking inference responses.

---

## Bonus Features Implemented

- Multi-provider support
- Streaming responses (SSE)
- Docker Compose setup
- Metrics dashboard
- PII redaction
- Cancel active requests
- Mock provider for local evaluation

---

# Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, TailwindCSS, Recharts |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Validation | Pydantic |
| Database | MySQL / PostgreSQL |
| Streaming | Server-Sent Events |
| Authentication | JWT |
| Containers | Docker Compose |

---

# Quick Start (Docker)

## Prerequisites

- Docker Desktop
- Git

---

## Run the Project

```bash
git clone <your-repo-url>
cd CHATBOT

cp .env.example .env

docker compose up --build
```

---

## Application URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Login | http://localhost:3000/login |
| Chat | http://localhost:3000/chat |
| Dashboard | http://localhost:3000/dashboard |
| API Docs | http://localhost:8000/docs |

---

## Default Behavior

The application defaults to the mock provider, allowing the project to run without external API keys.

To use OpenAI:

```env
OPENAI_API_KEY=sk-...
DEFAULT_PROVIDER=openai
DEFAULT_MODEL=gpt-4o-mini
```

---

# Database Configuration

## Local Development (MySQL)

```env
DATABASE_URL=mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/ollive
```

---

## Docker Compose (PostgreSQL)

```env
DATABASE_URL=postgresql+asyncpg://ollive:ollive@db:5432/ollive
```

---

## SQLite Fallback

```env
DATABASE_URL=sqlite+aiosqlite:///./backend/data/ollive.db
```

---

# Local Development Setup

## 1. Create Database

```sql
CREATE DATABASE IF NOT EXISTS ollive
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

---

## 2. Configure Environment

Copy `.env.example` to `.env`.

Example:

```env
DATABASE_URL=mysql+aiomysql://root:PASSWORD@localhost:3306/ollive
JWT_SECRET=change-this-secret
```

---

## 3. Start Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\pip install -r requirements.txt

.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

---

## 4. Start Frontend

```bash
cd frontend

npm install
npm run dev
```

---

# API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register user |
| POST | `/auth/login` | Login |
| GET | `/auth/me` | Current user |
| POST | `/chat` | Send chat message |
| GET | `/conversations` | List conversations |
| GET | `/conversations/{id}` | Get conversation |
| DELETE | `/conversations/{id}` | Delete conversation |
| POST | `/logs` | Ingestion endpoint |
| GET | `/metrics` | Observability metrics |
| GET | `/providers` | Available providers |
| GET | `/health` | Health check |

---

# SDK Example

```python
from app.providers.registry import get_provider
from app.sdk.llm_client import InstrumentedLLMClient
from app.providers.base import LLMMessage

provider = get_provider("openai")
client = InstrumentedLLMClient(provider)

result = await client.generate(
    model="gpt-4o-mini",
    messages=[
        LLMMessage(role="user", content="Hello")
    ],
    conversation_id=conversation_id,
    request_id=request_id,
)
```

Inference logs are asynchronously sent to:

```text
POST /logs
```

Captured metadata includes:

- request ID
- conversation ID
- provider
- model
- token counts
- latency
- timestamps
- status/errors
- redacted previews

---

# Database Schema

```sql
-- users
id UUID PRIMARY KEY,
email,
username,
hashed_password,
display_name,
bio,
default_provider,
default_model,
created_at

-- conversations
id UUID PRIMARY KEY,
user_id,
title,
created_at,
updated_at

-- chat_messages
id UUID PRIMARY KEY,
conversation_id,
role,
content,
timestamp

-- inference_logs
id UUID PRIMARY KEY,
request_id,
conversation_id,
provider,
model,
prompt_tokens,
completion_tokens,
total_tokens,
latency_ms,
status,
error_message,
input_preview,
output_preview,
created_at
```

---

# Engineering Tradeoffs

| Decision | Reason |
|---|---|
| HTTP ingestion over Kafka | Faster implementation for assignment scope |
| Monolithic backend | Simpler deployment and reduced operational overhead |
| Async fire-and-forget logging | Observability failures never block user responses |
| Log previews instead of full prompts | Better privacy and lower storage costs |
| Mock provider default | Evaluators can run locally without API keys |

---

# Scaling Considerations

Future production improvements:

1. Kafka or RabbitMQ ingestion pipeline
2. OpenTelemetry distributed tracing
3. Rate limiting and tenant quotas
4. Partitioned log tables
5. Retry queues and dead-letter handling
6. CI/CD deployment pipelines
7. Kubernetes deployment
8. Horizontal ingestion workers

---

# Project Structure

```text
CHATBOT/
├── frontend/
├── backend/
│   └── app/
│       ├── api/
│       ├── sdk/
│       ├── ingestion/
│       ├── providers/
│       ├── services/
│       └── db/
├── docker-compose.yml
├── README.md
└── ARCHITECTURE.md
```

---

# Submission Checklist

- [x] Multi-turn chatbot
- [x] Inference logging SDK
- [x] Ingestion API
- [x] Relational database schema
- [x] Dashboard metrics
- [x] Docker Compose setup
- [x] Multi-provider support
- [x] Streaming responses
- [x] Authentication
- [ ] Hosted demo / Loom video

---

# License

MIT License