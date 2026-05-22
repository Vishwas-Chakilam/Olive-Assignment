import asyncio
from collections.abc import AsyncGenerator

from app.providers.base import BaseLLMProvider, LLMMessage, LLMResult, LLMUsage, StreamChunk


class MockProvider(BaseLLMProvider):
    """Deterministic provider for local demo without API keys."""

    name = "mock"

    async def generate(self, model: str, messages: list[LLMMessage]) -> LLMResult:
        await asyncio.sleep(0.3)
        last = messages[-1].content if messages else ""
        reply = f"[mock/{model}] I received your message ({len(last)} chars). This is a demo response with simulated token usage."
        return LLMResult(
            content=reply,
            usage=LLMUsage(prompt_tokens=max(10, len(last) // 4), completion_tokens=45, total_tokens=55),
            model=model,
            provider=self.name,
        )

    async def generate_stream(self, model: str, messages: list[LLMMessage]) -> AsyncGenerator[StreamChunk, None]:
        last = messages[-1].content if messages else ""
        text = f"[mock/{model}] Streaming demo reply to: {last[:80]}..."
        for word in text.split(" "):
            await asyncio.sleep(0.05)
            yield StreamChunk(content=word + " ", model=model)
        yield StreamChunk(
            content=text,
            done=True,
            usage=LLMUsage(prompt_tokens=30, completion_tokens=len(text.split()), total_tokens=50),
            model=model,
        )
