from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class LLMMessage:
    role: str
    content: str


@dataclass
class LLMUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class LLMResult:
    content: str
    usage: LLMUsage = field(default_factory=LLMUsage)
    model: str = ""
    provider: str = ""


@dataclass
class StreamChunk:
    content: str = ""
    done: bool = False
    usage: LLMUsage | None = None
    model: str = ""


class BaseLLMProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def generate(self, model: str, messages: list[LLMMessage]) -> LLMResult:
        pass

    @abstractmethod
    async def generate_stream(self, model: str, messages: list[LLMMessage]):
        """Async generator yielding StreamChunk."""
        pass
