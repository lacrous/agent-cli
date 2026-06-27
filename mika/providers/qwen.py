"""Qwen / Alibaba DashScope provider for mika CLI."""

from typing import Dict, Iterator, List, Optional

from openai import OpenAI

from mika.providers.base import BaseProvider, ProviderConfig, StreamChunk


class QwenProvider(BaseProvider):
    """Qwen models through DashScope compatible-mode API."""

    CONFIG = ProviderConfig(
        name="qwen",
        display_name="Alibaba Qwen (DashScope)",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        default_model="qwen3.7-max",
        models=[
            "qwen3.7-max",
            "qwen3.7-72b-instruct",
            "qwen3.7-32b-instruct",
            "qwen3.7-14b-instruct",
            "qwen3.7-7b-instruct",
            "qwen3.5-turbo",
            "qwen3.5-72b-instruct",
            "qwen-max",
            "qwen-plus",
            "qwen-turbo",
        ],
        requires_api_key=True,
        env_var="DASHSCOPE_API_KEY",
        supports_thinking=True,
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

        extra_body = {"enable_thinking": kwargs.get("enable_thinking", True)}
        if "temperature" in kwargs:
            extra_body["temperature"] = kwargs["temperature"]
        if "max_tokens" in kwargs:
            extra_body["max_tokens"] = kwargs["max_tokens"]

        completion = client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            extra_body=extra_body,
            stream=True,
        )

        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            finish = chunk.choices[0].finish_reason
            content = getattr(delta, "content", None)
            reasoning = getattr(delta, "reasoning_content", None)
            if content or reasoning or finish:
                yield StreamChunk(
                    content=content,
                    reasoning_content=reasoning,
                    finish_reason=finish,
                )
