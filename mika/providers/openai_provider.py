"""OpenAI provider for mika CLI."""

from typing import Dict, Iterator, List, Optional

from openai import OpenAI

from mika.providers.base import BaseProvider, ProviderConfig, StreamChunk


class OpenAIProvider(BaseProvider):
    """OpenAI GPT models."""

    CONFIG = ProviderConfig(
        name="openai",
        display_name="OpenAI",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4o-mini",
        models=[
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ],
        requires_api_key=True,
        env_var="OPENAI_API_KEY",
        supports_thinking=False,
    )

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, model, base_url)
        self._client: Optional[OpenAI] = None

    def _get_client(self) -> OpenAI:
        if self._client is None:
            self.validate()
            self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._client

    def chat(self, messages: List[Dict[str, str]], system_prompt: Optional[str] = None, **kwargs) -> Iterator[StreamChunk]:
        client = self._get_client()
        chat_messages: List[Dict[str, str]] = []
        if system_prompt:
            chat_messages.append({"role": "system", "content": system_prompt})
        chat_messages.extend(messages)

        params = {
            "model": self.model,
            "messages": chat_messages,
            "stream": True,
        }
        if "temperature" in kwargs:
            params["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]

        completion = client.chat.completions.create(**params)
        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            finish = chunk.choices[0].finish_reason
            content = getattr(delta, "content", None)
            if content or finish:
                yield StreamChunk(content=content, finish_reason=finish)
