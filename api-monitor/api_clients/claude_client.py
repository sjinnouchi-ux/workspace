"""Anthropic (Claude) API client wrapper.

Provides `call(prompt, model, ...)` returning a unified `CallResult`
and writes a row to `api_call_logs`.
"""

from __future__ import annotations

import os
import time

import anthropic

import db
from api_clients import CallResult, Usage, calc_cost


SERVICE = "anthropic"
DEFAULT_MODEL = "claude-haiku-4-5"


def _client() -> anthropic.Anthropic:
    api_key = db.get_api_key(SERVICE) or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Anthropic API key not found. Set ANTHROPIC_API_KEY in .env "
            "or register it from the settings tab."
        )
    return anthropic.Anthropic(api_key=api_key)


def _extract_text(message) -> str:
    """Concatenate text blocks from an anthropic.types.Message."""
    parts: list[str] = []
    for block in getattr(message, "content", []) or []:
        text = getattr(block, "text", None)
        if text:
            parts.append(text)
    return "".join(parts)


def call(
    prompt: str,
    model: str = DEFAULT_MODEL,
    *,
    project: str | None = None,
    purpose: str | None = None,
    system: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> CallResult:
    """Call Anthropic Messages API and log usage."""
    client = _client()

    started = time.perf_counter()
    try:
        kwargs: dict = {
            "model":       model,
            "max_tokens":  max_tokens,
            "temperature": temperature,
            "messages":    [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        resp = client.messages.create(**kwargs)
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        db.insert_call_log(
            service=SERVICE,
            model=model,
            input_tokens=0,
            output_tokens=0,
            cost_usd=0.0,
            project=project,
            purpose=purpose,
            response_ms=elapsed_ms,
            status="error",
            error_message=str(exc)[:500],
        )
        raise

    elapsed_ms = int((time.perf_counter() - started) * 1000)

    usage_obj = getattr(resp, "usage", None)
    input_tokens  = int(getattr(usage_obj, "input_tokens", 0) or 0)
    output_tokens = int(getattr(usage_obj, "output_tokens", 0) or 0)
    cost_usd = calc_cost(SERVICE, model, input_tokens, output_tokens)

    content = _extract_text(resp)

    db.insert_call_log(
        service=SERVICE,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        project=project,
        purpose=purpose,
        response_ms=elapsed_ms,
        content_preview=content[:200],
        status="ok",
    )

    usage: Usage = {
        "input_tokens":  input_tokens,
        "output_tokens": output_tokens,
        "model":         model,
        "cost_usd":      cost_usd,
    }
    return CallResult(content=content, usage=usage, response_ms=elapsed_ms)
