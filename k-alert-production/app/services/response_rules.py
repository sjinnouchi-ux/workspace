from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.core.supabase import SupabaseRestClient


class ResponseRuleStore(Protocol):
    async def find_reply(self, *, text: str) -> str | None:
        """Return a fast fixed reply matched by active DB rules."""


@dataclass(frozen=True)
class NullResponseRuleStore:
    async def find_reply(self, *, text: str) -> str | None:
        return None


@dataclass(frozen=True)
class SupabaseResponseRuleStore:
    client: SupabaseRestClient

    async def find_reply(self, *, text: str) -> str | None:
        rows = await self.client.select(
            "ai_response_rules",
            select="trigger_type,trigger_text,instruction,priority",
            filters={"active": "eq.true"},
            order="priority.asc,created_at.asc",
            limit=50,
        )
        normalized_text = text.strip()
        for row in rows:
            reply = _match_reply_rule(row=row, text=normalized_text)
            if reply:
                return reply
        return None


def _match_reply_rule(*, row: dict, text: str) -> str | None:
    trigger_type = row.get("trigger_type")
    trigger_text = row.get("trigger_text")
    instruction = row.get("instruction")
    if not isinstance(trigger_type, str) or not isinstance(instruction, str):
        return None
    if not instruction.strip():
        return None

    if trigger_type == "exact_text_reply" and isinstance(trigger_text, str):
        return instruction if text == trigger_text.strip() else None
    if trigger_type == "contains_text_reply" and isinstance(trigger_text, str):
        return instruction if trigger_text.strip() in text else None
    if trigger_type == "fallback_reply":
        return instruction
    return None
