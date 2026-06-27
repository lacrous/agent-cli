"""Base provider interface for mika CLI."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional


@dataclass
class ProviderConfig:
    """Static metadata describing a provider."""

    name: str
    display_name: str
    base_url: str
    default_model: str
    models: List[str]
    requires_api_key: bool
    env_var: str
    supports_thinking: bool = False


@dataclass
class StreamChunk:
    """A single chunk emitted while streaming a response."""

    content: Optional[str] = None
    reasoning_content: Optional[str] = None
    finish_reason: Optional[str] = None


class BaseProvider(ABC):
    """Abstract base class for AI providers."""

    CONFIG: ProviderConfig

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model or self.CONFIG.default_model
        self.base_url = base_url or self.CONFIG.base_url

    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, **kwargs) -> Iterator[StreamChunk]:
        """Stream chat completion chunks. Must be implemented by subclasses."""
        raise NotImplementedError

    def validate(self) -> None:
        """Validate that the provider is ready to use."""
        if self.CONFIG.requires_api_key and not self.api_key:
            raise RuntimeError(
                f"API key required for {self.CONFIG.display_name}. "
                f"Set it with: mika config --api-key <key> or set {self.CONFIG.env_var} environment variable."
            )

    @classmethod
    def get_models(cls) -> List[str]:
        return cls.CONFIG.models

    @classmethod
    def get_default_model(cls) -> str:
        return cls.CONFIG.default_model
