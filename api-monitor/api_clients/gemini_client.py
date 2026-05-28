"""Google (Gemini) API client wrapper.

Provides `call(prompt, model, ...)` returning a unified `CallResult`
and writes a row to `api_call_logs`.
"""

from __future__ import annotations

import os
import time

import google.generativeai as genai

import db
from api_clients import CallResult, Usage, calc_cost


SERVICE = "google"
DEFAULT_MODEL = "gemini-1.5-flash"


def _configure() -> None:
    api_key = db.get_api_key(SERVICE) or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Google API key not found. Set GOOGLE_API_KEY in .env "
            "or register it from the settings tab."
        )
    genai.configure(api_key=api_key)


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
    """Call Gemini and log usage.

    Token counts are read from `response.usage_metadata`:
        prompt_token_count       -> input_tokens
        candidates_token_count   -> output_tokens
    """
    _configure()

    gen_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system if system else None,
    )

    started = time.perf_counter()
    try:
        resp = gen_model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature":       temperature,
            },
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

    usage_obj = getattr(resp, "usage_metadata", None)
    input_tokens  = int(getattr(usage_obj, "prompt_token_count", 0) or 0)
    output_tokens = int(getattr(usage_obj, "candidates_token_count", 0) or 0)
    cost_usd = calc_cost(SERVICE, model, input_tokens, output_tokens)

    content = getattr(resp, "text", "") or ""

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
