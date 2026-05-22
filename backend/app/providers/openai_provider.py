from collections.abc import AsyncGenerator

from openai import AsyncOpenAI

from app.config import settings
from app.providers.base import BaseLLMProvider, LLMMessage, LLMResult, LLMUsage, StreamChunk


class OpenAIProvider(BaseLLMProvider):
    name = "openai"

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key or "sk-placeholder")

    def _to_openai_messages(self, messages: list[LLMMessage]) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def generate(self, model: str, messages: list[LLMMessage]) -> LLMResult:
        response = await self._client.chat.completions.create(
            model=model,
            messages=self._to_openai_messages(messages),
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResult(
            content=choice.message.content or "",
            usage=LLMUsage(
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                total_tokens=usage.total_tokens if usage else 0,
            ),
            model=response.model,
            provider=self.name,
        )

    async def generate_stream(self, model: str, messages: list[LLMMessage]) -> AsyncGenerator[StreamChunk, None]:
        stream = await self._client.chat.completions.create(
            model=model,
            messages=self._to_openai_messages(messages),
            stream=True,
        )
        usage = LLMUsage()
        full_content: list[str] = []
        resolved_model = model

        async for chunk in stream:
            if chunk.model:
                resolved_model = chunk.model
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                full_content.append(delta.content)
                yield StreamChunk(content=delta.content, model=resolved_model)

            if chunk.usage:
                usage = LLMUsage(
                    prompt_tokens=chunk.usage.prompt_tokens,
                    completion_tokens=chunk.usage.completion_tokens,
                    total_tokens=chunk.usage.total_tokens,
                )

        yield StreamChunk(
            content="".join(full_content),
            done=True,
            usage=usage,
            model=resolved_model,
        )
