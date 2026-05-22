"""Lightweight SDK wrapper: instruments LLM calls and ships logs to ingestion."""

import asyncio
import time
import uuid
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.models.schemas import InferenceLogPayload
from app.providers.base import BaseLLMProvider, LLMMessage, LLMResult, StreamChunk
from app.sdk.pii import redact_pii


def _preview(text: str) -> str:
    if not text:
        return ""
    return redact_pii(text)[: settings.preview_chars]


class InstrumentedLLMClient:
    """Wraps provider calls with latency/token logging. Logging never blocks the response."""

    def __init__(self, provider: BaseLLMProvider, ingestion_url: str | None = None) -> None:
        self.provider = provider
        self.ingestion_url = ingestion_url or settings.ingestion_url

    async def _emit_log(self, payload: InferenceLogPayload) -> None:
        try:
            async with httpx.AsyncClient(timeout=settings.log_timeout_seconds) as client:
                await client.post(self.ingestion_url, json=payload.model_dump(mode="json"))
        except Exception:
            # Logging failures must never break inference
            pass

    def _fire_and_forget_log(self, payload: InferenceLogPayload) -> None:
        asyncio.create_task(self._emit_log(payload))

    async def generate(
        self,
        model: str,
        messages: list[LLMMessage],
        *,
        conversation_id: uuid.UUID | None = None,
        request_id: uuid.UUID | None = None,
    ) -> LLMResult:
        req_id = request_id or uuid.uuid4()
        input_preview = _preview(messages[-1].content if messages else "")
        start = time.perf_counter()

        try:
            result = await self.provider.generate(model, messages)
            latency_ms = int((time.perf_counter() - start) * 1000)
            self._fire_and_forget_log(
                InferenceLogPayload(
                    request_id=req_id,
                    conversation_id=conversation_id,
                    provider=result.provider or self.provider.name,
                    model=result.model or model,
                    prompt_tokens=result.usage.prompt_tokens,
                    completion_tokens=result.usage.completion_tokens,
                    total_tokens=result.usage.total_tokens,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc),
                    status="success",
                    input_preview=input_preview,
                    output_preview=_preview(result.content),
                )
            )
            return result
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self._fire_and_forget_log(
                InferenceLogPayload(
                    request_id=req_id,
                    conversation_id=conversation_id,
                    provider=self.provider.name,
                    model=model,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc),
                    status="error",
                    error_message=str(e),
                    input_preview=input_preview,
                )
            )
            raise

    async def generate_stream(
        self,
        model: str,
        messages: list[LLMMessage],
        *,
        conversation_id: uuid.UUID | None = None,
        request_id: uuid.UUID | None = None,
    ):
        req_id = request_id or uuid.uuid4()
        input_preview = _preview(messages[-1].content if messages else "")
        start = time.perf_counter()
        collected: list[str] = []
        final_usage = None
        resolved_model = model

        try:
            async for chunk in self.provider.generate_stream(model, messages):
                if chunk.model:
                    resolved_model = chunk.model
                if chunk.content and not chunk.done:
                    collected.append(chunk.content)
                    yield chunk
                if chunk.done:
                    final_usage = chunk.usage
                    yield chunk

            latency_ms = int((time.perf_counter() - start) * 1000)
            output = "".join(collected)
            usage = final_usage
            self._fire_and_forget_log(
                InferenceLogPayload(
                    request_id=req_id,
                    conversation_id=conversation_id,
                    provider=self.provider.name,
                    model=resolved_model,
                    prompt_tokens=usage.prompt_tokens if usage else None,
                    completion_tokens=usage.completion_tokens if usage else None,
                    total_tokens=usage.total_tokens if usage else None,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc),
                    status="success",
                    input_preview=input_preview,
                    output_preview=_preview(output),
                )
            )
        except Exception as e:
            latency_ms = int((time.perf_counter() - start) * 1000)
            self._fire_and_forget_log(
                InferenceLogPayload(
                    request_id=req_id,
                    conversation_id=conversation_id,
                    provider=self.provider.name,
                    model=model,
                    latency_ms=latency_ms,
                    timestamp=datetime.now(timezone.utc),
                    status="error",
                    error_message=str(e),
                    input_preview=input_preview,
                    output_preview=_preview("".join(collected)),
                )
            )
            raise
