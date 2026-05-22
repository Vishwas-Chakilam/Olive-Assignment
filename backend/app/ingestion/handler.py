from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import InferenceLog
from app.models.schemas import InferenceLogPayload


async def ingest_log(db: AsyncSession, payload: InferenceLogPayload) -> InferenceLog:
    record = InferenceLog(
        request_id=payload.request_id,
        conversation_id=payload.conversation_id,
        provider=payload.provider,
        model=payload.model,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        total_tokens=payload.total_tokens,
        latency_ms=payload.latency_ms,
        status=payload.status,
        error_message=payload.error_message,
        input_preview=payload.input_preview,
        output_preview=payload.output_preview,
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


async def get_recent_logs(db: AsyncSession, limit: int = 500) -> list[InferenceLog]:
    result = await db.execute(
        select(InferenceLog).order_by(InferenceLog.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
