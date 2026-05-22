from app.config import settings
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.base import BaseLLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider
from app.providers.openai_provider import OpenAIProvider

PROVIDERS: dict[str, BaseLLMProvider] = {
    "mock": MockProvider(),
    "openai": OpenAIProvider(),
    "anthropic": AnthropicProvider(),
    "gemini": GeminiProvider(),
}

DEFAULT_MODELS = {
    "mock": "mock-gpt",
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "gemini": "gemini-2.5-flash",
}


def _default_provider() -> str:
    if settings.default_provider in PROVIDERS:
        return settings.default_provider
    if settings.openai_api_key:
        return "openai"
    return "mock"


def get_provider(name: str) -> BaseLLMProvider:
    key = name.lower()
    if key not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS)}")
    return PROVIDERS[key]
