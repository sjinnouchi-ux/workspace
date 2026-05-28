"""Shared interface, pricing table and cost calculator for API clients.

Each provider client exposes a `call(prompt, model, ...)` function that
returns a dict matching `CallResult`:

    {
        "content":      str,           # model output text
        "usage": {
            "input_tokens":  int,
            "output_tokens": int,
            "model":         str,
            "cost_usd":      float,
        },
        "response_ms":  int,
    }

The call is also logged to the SQLite layer (see `db.insert_call_log`).
"""

from __future__ import annotations

from typing import TypedDict


SUPPORTED_SERVICES: tuple[str, ...] = ("openai", "anthropic", "google")


class Usage(TypedDict):
    input_tokens: int
    output_tokens: int
    model: str
    cost_usd: float


class CallResult(TypedDict):
    content: str
    usage: Usage
    response_ms: int


# ---------------------------------------------------------------------------
# Pricing table — USD per 1M tokens
# Source: implementation_plan.md (2026-05 snapshot). Refresh in Phase 5.
# ---------------------------------------------------------------------------

# (service, model) -> (input_per_1m_usd, output_per_1m_usd)
MODEL_PRICING: dict[tuple[str, str], tuple[float, float]] = {
    # OpenAI
    ("openai",    "gpt-4o-mini"):          (0.15,  0.60),
    ("openai",    "gpt-4o"):               (2.50, 10.00),

    # Anthropic
    ("anthropic", "claude-haiku-4-5"):     (0.80,  4.00),
    ("anthropic", "claude-sonnet-4-6"):    (3.00, 15.00),
    ("anthropic", "claude-opus-4-6"):      (5.00, 25.00),
    ("anthropic", "claude-opus-4-7"):      (5.00, 25.00),

    # Google
    ("google",    "gemini-1.5-flash"):     (0.075, 0.30),
    ("google",    "gemini-1.5-pro"):       (1.25,  5.00),
}


def calc_cost(service: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """Compute USD cost for a single call.

    Returns 0.0 when the (service, model) pair is unknown so the call still
    logs cleanly — Phase 5 will surface unknown-model warnings in the UI.
    """
    rates = MODEL_PRICING.get((service, model))
    if not rates:
        return 0.0
    inp_rate, out_rate = rates
    return (input_tokens / 1_000_000.0) * inp_rate + (output_tokens / 1_000_000.0) * out_rate


__all__ = [
    "SUPPORTED_SERVICES",
    "Usage",
    "CallResult",
    "MODEL_PRICING",
    "calc_cost",
]
