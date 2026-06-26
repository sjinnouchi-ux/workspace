from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


class ChatWorkClient(Protocol):
    async def send_message(self, *, room_id: str, body: str) -> str | None:
        """Send one ChatWork message and return ChatWork's message id when available."""


@dataclass(frozen=True)
class NullChatWorkClient:
    async def send_message(self, *, room_id: str, body: str) -> str | None:
        return None


@dataclass(frozen=True)
class ChatWorkApiClient:
    api_token: str

    async def send_message(self, *, room_id: str, body: str) -> str | None:
        endpoint = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
        headers = {"X-ChatWorkToken": self.api_token}
        data = {"body": body}
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(endpoint, headers=headers, data=data)
            response.raise_for_status()
            payload = response.json()
        message_id = payload.get("message_id")
        return str(message_id) if message_id is not None else None
