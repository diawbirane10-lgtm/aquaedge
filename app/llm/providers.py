from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


class LLMProviderError(RuntimeError):
    pass


@dataclass(slots=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    raw: dict[str, Any] | None = None


def _messages(system: str, user: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


class BaseProvider:
    name = "base"

    def chat(self, model: str, system: str, user: str) -> LLMResponse:
        raise NotImplementedError


class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, base_url: str | None = None, timeout: float = 180.0) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.timeout = timeout

    def chat(self, model: str, system: str, user: str) -> LLMResponse:
        payload = {"model": model, "messages": _messages(system, user), "stream": False}
        r = httpx.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout)
        r.raise_for_status()
        raw = r.json()
        return LLMResponse(raw["message"]["content"], self.name, model, raw)


class OpenAICompatibleProvider(BaseProvider):
    def __init__(self, name: str, base_url: str, api_key_env: str, timeout: float = 180.0) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout

    def chat(self, model: str, system: str, user: str) -> LLMResponse:
        key = os.getenv(self.api_key_env)
        if not key:
            raise LLMProviderError(f"Missing environment variable {self.api_key_env}")
        payload = {"model": model, "messages": _messages(system, user), "temperature": 0.1}
        r = httpx.post(
            f"{self.base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {key}"},
            timeout=self.timeout,
        )
        r.raise_for_status()
        raw = r.json()
        return LLMResponse(raw["choices"][0]["message"]["content"], self.name, model, raw)


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def chat(self, model: str, system: str, user: str) -> LLMResponse:
        key = os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise LLMProviderError("Missing environment variable ANTHROPIC_API_KEY")
        payload = {
            "model": model,
            "max_tokens": 900,
            "temperature": 0.1,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        r = httpx.post(
            "https://api.anthropic.com/v1/messages",
            json=payload,
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=180.0,
        )
        r.raise_for_status()
        raw = r.json()
        text = "\n".join(p.get("text", "") for p in raw.get("content", []) if p.get("type") == "text")
        return LLMResponse(text, self.name, model, raw)


class OpenAIResponsesProvider(BaseProvider):
    name = "openai"

    def chat(self, model: str, system: str, user: str) -> LLMResponse:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise LLMProviderError("Missing environment variable OPENAI_API_KEY")
        payload = {
            "model": model,
            "instructions": system,
            "input": user,
        }
        r = httpx.post(
            "https://api.openai.com/v1/responses",
            json=payload,
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            timeout=180.0,
        )
        r.raise_for_status()
        raw = r.json()
        text = raw.get("output_text")
        if not text:
            parts: list[str] = []
            for item in raw.get("output", []):
                for c in item.get("content", []):
                    if c.get("type") in {"output_text", "text"}:
                        parts.append(c.get("text", ""))
            text = "\n".join(parts)
        return LLMResponse(text or "", self.name, model, raw)


def get_provider(name: str) -> BaseProvider:
    n = name.lower()
    if n == "ollama":
        return OllamaProvider()
    if n == "groq":
        return OpenAICompatibleProvider(
            "groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY"
        )
    if n == "mistral":
        return OpenAICompatibleProvider(
            "mistral", "https://api.mistral.ai/v1", "MISTRAL_API_KEY"
        )
    if n == "openrouter":
        return OpenAICompatibleProvider(
            "openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"
        )
    if n == "anthropic":
        return AnthropicProvider()
    if n == "openai":
        return OpenAIResponsesProvider()
    raise ValueError(f"Unknown provider: {name}")
