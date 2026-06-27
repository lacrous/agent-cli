"""Anthropic provider for mika CLI."""

from typing import Dict, Iterator, List, Optional

from mika.providers.base import BaseProvider, ProviderConfig, StreamChunk


class AnthropicProvider(BaseProvider):
    """Anthropic Claude models."""

    CONFIG = ProviderConfig(
        name="anthropic",
        display_name="Anthropic Claude",
        base_url="https://api.anthropic.com/v1",
        default_model="claude-3-5-sonnet-20241022",
        models=[
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ],
        requires_api_key=True,
        env_var="ANTHROPIC_API_KEY",
        supports_thinking=False,
    )

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        self._client = None

    def _get_client(self):
        if self._client is None:
            self.validate()
            try:
                import anthropic
            except ImportError as exc:
                raise RuntimeError(
                    "Anthropic provider requires the 'anthropic' package. Install it with: pip install anthropic"
                ) from exc
            self._client = anthropic.Anthropic(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, **kwargs) -> Iterator[StreamChunk]:
        client = self._get_client()
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "stream": True,
        }
        if system_prompt:
            params["system"] = system_prompt
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]

        with client.messages.stream(**params) as stream:
            for text in stream.text_stream:
                yield StreamChunk(content=text)
