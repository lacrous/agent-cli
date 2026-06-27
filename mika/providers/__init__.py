"""Provider registry for mika CLI."""

from typing import Dict, Type

from mika.providers.base import BaseProvider
from mika.providers.qwen import QwenProvider
from mika.providers.openai_provider import OpenAIProvider
from mika.providers.anthropic_provider import AnthropicProvider
from mika.providers.ollama import OllamaProvider


PROVIDERS: Dict[str, Type[BaseProvider]] = {
    QwenProvider.CONFIG.name: QwenProvider,
    OpenAIProvider.CONFIG.name: OpenAIProvider,
    AnthropicProvider.CONFIG.name: AnthropicProvider,
    OllamaProvider.CONFIG.name: OllamaProvider,
}


def list_providers() -> Dict[str, Type[BaseProvider]]:
    return PROVIDERS.copy()


def get_provider(name: str) -> Type[BaseProvider]:
    if name not in PROVIDERS:
        raise KeyError(f"Unknown provider: {name}. Available: {', '.join(PROVIDERS)}")
    return PROVIDERS[name]
