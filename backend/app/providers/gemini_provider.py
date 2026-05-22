from collections.abc import AsyncGenerator

import google.generativeai as genai

from app.config import settings
from app.providers.base import BaseLLMProvider, LLMMessage, LLMResult, LLMUsage, StreamChunk
from app.utils.model_names import normalize_model_name


class GeminiProvider(BaseLLMProvider):
    name = "gemini"

    def __init__(self) -> None:
        genai.configure(api_key=settings.google_api_key or "placeholder")

    def _to_prompt(self, messages: list[LLMMessage]) -> str:
        parts = []
        for m in messages:
            parts.append(f"{m.role.upper()}: {m.content}")
        return "\n\n".join(parts)

    async def generate(self, model: str, messages: list[LLMMessage]) -> LLMResult:
        model = normalize_model_name(model)
        client = genai.GenerativeModel(model)
        response = await client.generate_content_async(self._to_prompt(messages))
        text = response.text or ""
        usage_meta = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) if usage_meta else 0
        completion_tokens = getattr(usage_meta, "candidates_token_count", 0) if usage_meta else 0
        return LLMResult(
            content=text,
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model=model,
            provider=self.name,
        )

    async def generate_stream(self, model: str, messages: list[LLMMessage]) -> AsyncGenerator[StreamChunk, None]:
        model = normalize_model_name(model)
        client = genai.GenerativeModel(model)
        response = await client.generate_content_async(self._to_prompt(messages), stream=True)
        full: list[str] = []
        prompt_tokens = 0
        completion_tokens = 0
        async for chunk in response:
            if chunk.text:
                full.append(chunk.text)
                yield StreamChunk(content=chunk.text, model=model)
            usage_meta = getattr(chunk, "usage_metadata", None)
            if usage_meta:
                prompt_tokens = getattr(usage_meta, "prompt_token_count", 0) or prompt_tokens
                completion_tokens = getattr(usage_meta, "candidates_token_count", 0) or completion_tokens
        yield StreamChunk(
            content="".join(full),
            done=True,
            usage=LLMUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            model=model,
        )
