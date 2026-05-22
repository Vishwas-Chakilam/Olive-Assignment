-- Reference schema (tables created via SQLAlchemy on startup)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- conversations: id, created_at, updated_at, title
-- chat_messages: id, conversation_id, role, content, timestamp
-- inference_logs: id, request_id, conversation_id, provider, model,
--   prompt/completion/total tokens, latency_ms, status, error_message,
--   input_preview, output_preview, created_at
