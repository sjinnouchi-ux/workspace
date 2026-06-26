from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import httpx

LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply"
LINE_PROFILE_ENDPOINT = "https://api.line.me/v2/bot/profile"


class LineMessagingClient(Protocol):
    async def reply_messages(
        self,
        *,
        reply_token: str,
        messages: list[dict[str, Any]],
    ) -> None:
        """Reply to one LINE webhook event with raw LINE message objects."""

    async def reply_text(
        self,
        *,
        reply_token: str,
        text: str,
        quick_reply: dict[str, Any] | None = None,
    ) -> None:
        """Reply to one LINE webhook event with a text message."""

    async def get_profile(self, *, user_id: str) -> dict[str, Any] | None:
        """Return a LINE user profile when the user can be resolved."""


@dataclass
class NullLineMessagingClient:
    async def reply_messages(
        self,
        *,
        reply_token: str,
        messages: list[dict[str, Any]],
    ) -> None:
        return None

    async def reply_text(
        self,
        *,
        reply_token: str,
        text: str,
        quick_reply: dict[str, Any] | None = None,
    ) -> None:
        return None

    async def get_profile(self, *, user_id: str) -> dict[str, Any] | None:
        return None


@dataclass(frozen=True)
class LineMessagingApiClient:
    channel_access_token: str

    async def reply_messages(
        self,
        *,
        reply_token: str,
        messages: list[dict[str, Any]],
    ) -> None:
        payload = {
            "replyToken": reply_token,
            "messages": messages,
        }
        headers = {
            "Authorization": f"Bearer {self.channel_access_token}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(LINE_REPLY_ENDPOINT, headers=headers, json=payload)
            response.raise_for_status()

    async def reply_text(
        self,
        *,
        reply_token: str,
        text: str,
        quick_reply: dict[str, Any] | None = None,
    ) -> None:
        message: dict[str, Any] = {"type": "text", "text": text}
        if quick_reply:
            message["quickReply"] = quick_reply
        await self.reply_messages(reply_token=reply_token, messages=[message])

    async def get_profile(self, *, user_id: str) -> dict[str, Any] | None:
        headers = {"Authorization": f"Bearer {self.channel_access_token}"}
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{LINE_PROFILE_ENDPOINT}/{user_id}", headers=headers)
            response.raise_for_status()
            payload = response.json()
        return payload if isinstance(payload, dict) else None
