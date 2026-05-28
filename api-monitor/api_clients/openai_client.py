"""OpenAI API client wrapper.

Provides `call(prompt, model, ...)` returning a unified `CallResult`
and writes a row to `api_call_logs`.
"""

from __future__ import annotations

import os
import time

from openai import OpenAI

import db
from api_clients import CallResult, Usage, calc_cost


SERVICE = "openai"
DEFAULT_MODEL = "gpt-4o-mini"


def _client() -> OpenAI:
    api_key = db.get_api_key(SERVICE) or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OpenAI API key not found. Set OPENAI_API_KEY in .env "
            "or register it from the settings tab."
        )
    return OpenAI(api_key=api_key)


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
    """Call OpenAI Chat Completions and log usage."""
    client = _client()
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    started = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
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

    usage_obj = resp.usage
    input_tokens  = int(getattr(usage_obj, "prompt_tokens", 0) or 0)
    output_tokens = int(getattr(usage_obj, "completion_tokens", 0) or 0)
    cost_usd = calc_cost(SERVICE, model, input_tokens, output_tokens)

    content = ""
    if resp.choices:
        content = resp.choices[0].message.content or ""

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
