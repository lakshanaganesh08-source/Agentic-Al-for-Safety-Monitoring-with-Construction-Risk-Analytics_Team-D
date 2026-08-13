"""
Shared Ollama HTTP client for Construction Intelligence Hub.

Centralizes connection checks and generate requests so chatbot modules
stay thin and configuration lives in config/settings.py.
"""

from __future__ import annotations

from typing import Any

import requests

from config.settings import (
    OLLAMA_DEFAULT_TIMEOUT,
    OLLAMA_FAST_TIMEOUT,
    OLLAMA_GENERATE_PATH,
    OLLAMA_MODEL,
    OLLAMA_ROOT_URLS,
)


def get_api_urls() -> list[str]:
    """Return full /api/generate URLs for each configured Ollama host."""
    return [f"{root.rstrip('/')}{OLLAMA_GENERATE_PATH}" for root in OLLAMA_ROOT_URLS]


def check_ollama_connection() -> tuple[bool, str]:
    """
    Probe configured Ollama root URLs for availability.

    Returns:
        (connected, host_url) — host_url is the first reachable root or fallback.
    """
    for root_url in OLLAMA_ROOT_URLS:
        try:
            response = requests.get(root_url, timeout=2)
            if response.status_code == 200:
                return True, root_url
        except requests.RequestException:
            continue
    return False, OLLAMA_ROOT_URLS[0]


def request_ollama(
    payload: dict[str, Any],
    timeout: tuple[float, float] | None = None,
) -> tuple[requests.Response, str]:
    """
    POST a generate payload to the first reachable Ollama host.

    Args:
        payload: JSON body for /api/generate (must include ``model`` and ``prompt``).
        timeout: Optional (connect, read) override. Defaults to OLLAMA_DEFAULT_TIMEOUT.

    Returns:
        (response, url_used)

    Raises:
        requests.RequestException: When no host is reachable.
        RuntimeError: When all hosts fail without a specific exception.
    """
    if timeout is None:
        timeout = OLLAMA_DEFAULT_TIMEOUT

    last_exception: Exception | None = None
    for url in get_api_urls():
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            return response, url
        except requests.RequestException as exc:
            last_exception = exc
            continue

    raise last_exception or RuntimeError("Unable to reach Ollama on any configured host.")


def build_generate_payload(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 160,
    temperature: float = 0.5,
    stream: bool = False,
) -> dict[str, Any]:
    """Build a standard /api/generate payload."""
    return {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }


def extract_response_text(result: dict[str, Any]) -> str:
    """Parse the assistant text from an Ollama JSON response."""
    return (
        result.get("response")
        or result.get("text")
        or result.get("output")
        or "No response received from Ollama."
    )


def list_ollama_models() -> list[str]:
    """Return available model names from the local Ollama server."""
    for root_url in OLLAMA_ROOT_URLS:
        try:
            response = requests.get(f"{root_url.rstrip('/')}/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                names = [m.get("name", "") for m in models if m.get("name")]
                if names:
                    return names
        except requests.RequestException:
            continue
    return [OLLAMA_MODEL]


def build_chat_prompt(
    system_prompt: str,
    messages: list[dict[str, str]],
    user_message: str,
    *,
    max_history: int = 6,
) -> str:
    """
    Build a single prompt string with recent conversation history for /api/generate.
    """
    lines = [system_prompt, ""]
    history = messages[-max_history:] if messages else []
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            lines.append(f"User: {content}")
        else:
            lines.append(f"Assistant: {content}")
    lines.append(f"User: {user_message}")
    lines.append("Assistant:")
    return "\n".join(lines)


def generate_with_ollama(
    prompt: str,
    *,
    model: str | None = None,
    max_tokens: int = 160,
    temperature: float = 0.5,
    timeout: tuple[float, float] | None = None,
) -> tuple[str, bool]:
    """
    Send a generate request and return (response_text, success).

    Returns error message as text with success=False on failure.
    """
    payload = build_generate_payload(
        prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    try:
        response, _ = request_ollama(payload, timeout=timeout)
        if response.status_code == 200:
            return extract_response_text(response.json()), True
        try:
            err = response.json().get("error", f"Status {response.status_code}")
        except Exception:
            err = f"Status {response.status_code}"
        return f"⚠️ Ollama error: {err}", False
    except requests.exceptions.ConnectionError:
        return (
            "❌ Could not connect to Ollama. Run `ollama serve` and `ollama pull llama3.2`.",
            False,
        )
    except requests.Timeout:
        return "⏳ Request timed out — try a shorter question or Fast mode.", False
    except Exception as exc:
        return f"⚠️ Unexpected error: {exc}", False


# Re-export for modules that reference the model name directly.
DEFAULT_MODEL = OLLAMA_MODEL
FAST_TIMEOUT = OLLAMA_FAST_TIMEOUT
