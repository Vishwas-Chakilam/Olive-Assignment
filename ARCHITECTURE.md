# Architecture Notes

## System Overview

```text
┌─────────────┐     HTTP/SSE      ┌──────────────────────────────────────┐
│  Next.js    │ ────────────────► │  FastAPI Backend (Chat Service)      │
│  Frontend   │                   │  POST /chat, GET /conversations, …   │
└─────────────┘                   └──────────────┬───────────────────────┘
                                                 │
                                                 ▼
                                    ┌────────────────────────┐
                                    │  InstrumentedLLMClient │  (SDK)
                                    │  - timer               │
                                    │  - token/latency meta  │
                                    │  - fire-and-forget log │
                                    └────────────┬───────────┘
                                                 │ POST /logs (async)
                                                 ▼
                                    ┌────────────────────────┐
                                    │  Ingestion Handler     │
                                    │  - Pydantic validate   │
                                    │  - persist metadata    │
                                    └────────────┬───────────┘
                                                 │
                                                 ▼
                                    ┌────────────────────────┐
                                    │  SQLAlchemy + DB       │
                                    │  MySQL (local) or      │
                                    │  PostgreSQL (Docker)   │
                                    │  users, conversations  │
                                    │  chat_messages         │
                                    │  inference_logs        │
                                    └────────────────────────┘
```

## Ingestion Flow

1. User sends a message via `POST /chat` (optionally with `stream: true`).
2. Chat service loads the last N messages (default 10) for multi-turn context.
3. `InstrumentedLLMClient` wraps the selected provider (`OpenAI`, `Anthropic`, `Gemini`, or `Mock`).
4. On success or failure, the SDK builds an `InferenceLogPayload` with:
   - `request_id`, `conversation_id`, `provider`, `model`
   - token counts, `latency_ms`, `status`, `error_message`
   - PII-redacted `input_preview` / `output_preview` (first 100 chars)
5. Log is sent to `POST /logs` via `httpx` with a short timeout (2s).
6. Ingestion validates with Pydantic and inserts into `inference_logs`.
7. Chat response returns to the user **without waiting** for log persistence.

## Logging Strategy

| Concern | Approach |
|--------|----------|
| Separation | SDK is isolated from chat routing and DB models |
| Non-blocking | `asyncio.create_task` + timeout; failures swallowed |
| Previews | Truncated + regex PII redaction (email, phone, SSN) |
| Correlation | `request_id` per inference, `conversation_id` per session |
| Streaming | Single log emitted after stream completes (with aggregated tokens) |

## Database Backends

The same SQLAlchemy models run against **MySQL** (local Windows/Linux dev) or **PostgreSQL** (Docker Compose). `DATABASE_URL` selects the driver (`mysql+aiomysql` vs `postgresql+asyncpg`). Startup runs `create_all` plus lightweight migrations (e.g. adding `user_id` to existing MySQL databases).

## Schema Design Decisions

- **`users`**: JWT auth, per-user defaults for provider/model; conversations cascade on delete.
- **`conversations`**: lightweight session entity with auto-generated title from first user message; scoped by `user_id` when authenticated.
- **`chat_messages`**: normalized message store; context window built via `ORDER BY timestamp DESC LIMIT N`.
- **`inference_logs`**: append-only telemetry table, decoupled from message content (previews only).
- **`request_id`** on logs: enables future distributed tracing without coupling to message PKs.
- **FK `ON DELETE SET NULL`** on logs: deleting a conversation retains historical metrics.

## Scaling Considerations

| Today (assignment) | Production evolution |
|------------------|---------------------|
| Sync HTTP log shipping | Kafka / RabbitMQ buffer between SDK and ingestion |
| Monolithic FastAPI | Split chat API vs ingestion workers |
| Relational DB direct writes (Postgres/MySQL) | TimescaleDB or ClickHouse for analytics |
| Polling dashboard | Grafana + Prometheus exporters from ingestion |
| Single region | Multi-region ingestion with idempotent `request_id` |

Throughput can scale ingestion horizontally by partitioning on `conversation_id` hash. Chat API scales on stateless replicas with a shared primary database (PostgreSQL or MySQL).

## MySQL Connection Stability

Local dev uses a small connection pool (`pool_size=5`, `pool_recycle=1800`). MySQL disables `pool_pre_ping` due to an aiomysql/SQLAlchemy compatibility issue; stale connections are recycled instead. Streaming chat **does not** hold a DB session for the whole SSE response — only short sessions for setup and saving the assistant message. That prevents pool exhaustion, which previously caused `/health` to flip between `connected` and `disconnected`.

## Failure Handling Assumptions

1. **Logging failure never blocks inference** — SDK catches all ingestion errors.
2. **Provider timeout/error** — logged with `status=error`, user receives HTTP 502 or SSE error event.
3. **Client disconnect** — streaming checks `request.is_disconnected()` and emits `cancelled` event.
4. **DB unavailable** — chat and ingestion return 5xx; no silent drops for chat, ingestion may retry in production.
5. **Invalid log payload** — FastAPI/Pydantic returns 422; SDK does not retry (would add dead-letter queue later).

## Event-Based Architecture (Future)

Current design uses **near-real-time HTTP** (simpler, sufficient for assignment). A production event path:

```text
SDK → message bus (Kafka) → ingestion consumer(s) → DB
                           → real-time metrics agent
                           → alerting on error_rate spike
```

Benefits: backpressure, replay, decoupled scaling. Tradeoff: operational complexity.

## Multi-Provider Layer

```text
BaseLLMProvider
 ├── MockProvider      (demo, no API key)
 ├── OpenAIProvider
 ├── AnthropicProvider
 └── GeminiProvider
```

Registry resolves provider by name. `InstrumentedLLMClient` is provider-agnostic.
