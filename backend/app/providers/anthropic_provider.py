from collections.abc import AsyncGenerator

from anthropic import AsyncAnthropic

from app.config import settings
from app.providers.base import BaseLLMProvider, LLMMessage, LLMResult, LLMUsage, StreamChunk


class AnthropicProvider(BaseLLMProvider):
    name = "anthropic"

    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key or "placeholder")

    def _split_messages(self, messages: list[LLMMessage]) -> tuple[str | None, list[dict]]:
        system = None
        conv: list[dict] = []
        for m in messages:
            if m.role == "system":
                system = m.content
            else:
                conv.append({"role": m.role, "content": m.content})
        return system, conv

    async def generate(self, model: str, messages: list[LLMMessage]) -> LLMResult:
        system, conv = self._split_messages(messages)
        kwargs: dict = {"model": model, "max_tokens": 4096, "messages": conv}
        if system:
            kwargs["system"] = system

        response = await self._client.messages.create(**kwargs)
        text = "".join(block.text for block in response.content if hasattr(block, "text"))
        usage = response.usage
        return LLMResult(
            content=text,
            usage=LLMUsage(
                prompt_tokens=usage.input_tokens,
                completion_tokens=usage.output_tokens,
                total_tokens=usage.input_tokens + usage.output_tokens,
            ),
            model=model,
            provider=self.name,
        )

    async def generate_stream(self, model: str, messages: list[LLMMessage]) -> AsyncGenerator[StreamChunk, None]:
        system, conv = self._split_messages(messages)
        kwargs: dict = {"model": model, "max_tokens": 4096, "messages": conv}
        if system:
            kwargs["system"] = system

        full: list[str] = []
        usage = LLMUsage()

        async with self._client.messages.stream(**kwargs) as stream:
            async for text in stream.text_stream:
                full.append(text)
                yield StreamChunk(content=text, model=model)

            final = await stream.get_final_message()
            usage = LLMUsage(
                prompt_tokens=final.usage.input_tokens,
                completion_tokens=final.usage.output_tokens,
                total_tokens=final.usage.input_tokens + final.usage.output_tokens,
            )

        yield StreamChunk(content="".join(full), done=True, usage=usage, model=model)
