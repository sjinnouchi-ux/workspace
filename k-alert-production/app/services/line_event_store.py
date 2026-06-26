from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol

import httpx

from app.core.supabase import SupabaseRestClient


class DuplicateWebhookEventError(RuntimeError):
    """Raised when LINE sends a webhookEventId that has already been stored."""


@dataclass(frozen=True)
class StoredLineEvent:
    stored: bool
    webhook_event_id: str = ""
    event_type: str = ""
    line_user_id: str = ""
    line_user_db_id: str | None = None
    message_text: str | None = None
    postback_data: str | None = None


class LineEventStore(Protocol):
    async def store_event(self, event: dict[str, Any]) -> StoredLineEvent:
        """Store one LINE webhook event."""

    async def store_ai_message(
        self,
        *,
        reply_to_webhook_event_id: str,
        body: str,
        case_id: str | None = None,
        raw_payload: dict[str, Any] | None = None,
    ) -> None:
        """Store a message sent by the system/AI side."""

    async def get_active_case(self, *, line_user_db_id: str) -> dict[str, Any] | None:
        """Return the latest unfinished case for one LINE user."""

    async def create_case(self, *, line_user_db_id: str, case_code: str) -> dict[str, Any] | None:
        """Create a case used as the consultation session."""

    async def close_case(self, *, case_id: str) -> None:
        """Close one consultation case."""

    async def update_case_route(self, *, case_id: str, route_type: str, status: str) -> None:
        """Update the user-selected case route."""

    async def attach_message_to_case(self, *, webhook_event_id: str, case_id: str) -> None:
        """Attach a stored inbound message to a case."""

    async def count_case_user_messages(self, *, case_id: str) -> int:
        """Count user text messages attached to one case."""

    async def create_chatwork_notification(
        self,
        *,
        case_id: str,
        room_id: str,
        message_body: str,
        status: str,
        chatwork_message_id: str | None = None,
        error_message: str | None = None,
    ) -> None:
        """Record a ChatWork notification attempt."""

    async def update_line_user_profile(
        self,
        *,
        line_user_db_id: str,
        display_name: str | None = None,
        picture_url: str | None = None,
    ) -> None:
        """Update LINE profile fields for one stored LINE user."""


@dataclass
class NullLineEventStore:
    async def store_event(self, event: dict[str, Any]) -> StoredLineEvent:
        return StoredLineEvent(
            stored=True,
            webhook_event_id=_webhook_event_id(event),
            event_type=str(event.get("type") or ""),
            line_user_id=_line_user_id(event),
            message_text=_text_message_body(event),
            postback_data=_postback_data(event),
        )

    async def store_ai_message(
        self,
        *,
        reply_to_webhook_event_id: str,
        body: str,
        case_id: str | None = None,
        raw_payload: dict[str, Any] | None = None,
    ) -> None:
        return None

    async def get_active_case(self, *, line_user_db_id: str) -> dict[str, Any] | None:
        return None

    async def create_case(self, *, line_user_db_id: str, case_code: str) -> dict[str, Any] | None:
        return {"id": "local-case", "case_code": case_code, "line_user_id": line_user_db_id}

    async def close_case(self, *, case_id: str) -> None:
        return None

    async def update_case_route(self, *, case_id: str, route_type: str, status: str) -> None:
        return None

    async def attach_message_to_case(self, *, webhook_event_id: str, case_id: str) -> None:
        return None

    async def count_case_user_messages(self, *, case_id: str) -> int:
        return 0

    async def create_chatwork_notification(
        self,
        *,
        case_id: str,
        room_id: str,
        message_body: str,
        status: str,
        chatwork_message_id: str | None = None,
        error_message: str | None = None,
    ) -> None:
        return None

    async def update_line_user_profile(
        self,
        *,
        line_user_db_id: str,
        display_name: str | None = None,
        picture_url: str | None = None,
    ) -> None:
        return None


@dataclass
class SupabaseLineEventStore:
    client: SupabaseRestClient

    async def store_event(self, event: dict[str, Any]) -> StoredLineEvent:
        webhook_event_id = _webhook_event_id(event)
        if not webhook_event_id:
            return StoredLineEvent(
                stored=True,
                event_type=str(event.get("type") or ""),
                line_user_id=_line_user_id(event),
                message_text=_text_message_body(event),
                postback_data=_postback_data(event),
            )

        line_user = await self._upsert_line_user(event)
        stored_line_user_id = line_user.get("id") if line_user else None
        try:
            await self.client.insert(
                "webhook_events",
                {
                    "webhook_event_id": webhook_event_id,
                    "line_user_id": stored_line_user_id,
                    "event_type": event.get("type"),
                    "raw_payload": event,
                    "processed_at": _now_iso(),
                },
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                return StoredLineEvent(
                    stored=False,
                    webhook_event_id=webhook_event_id,
                    event_type=str(event.get("type") or ""),
                    line_user_id=_line_user_id(event),
                    line_user_db_id=stored_line_user_id,
                    message_text=_text_message_body(event),
                    postback_data=_postback_data(event),
                )
            raise

        message_payload = _message_payload(event, line_user_id=stored_line_user_id)
        if message_payload:
            await self.client.insert("messages", message_payload)

        return StoredLineEvent(
            stored=True,
            webhook_event_id=webhook_event_id,
            event_type=str(event.get("type") or ""),
            line_user_id=_line_user_id(event),
            line_user_db_id=stored_line_user_id,
            message_text=_text_message_body(event),
            postback_data=_postback_data(event),
        )

    async def store_ai_message(
        self,
        *,
        reply_to_webhook_event_id: str,
        body: str,
        case_id: str | None = None,
        raw_payload: dict[str, Any] | None = None,
    ) -> None:
        await self.client.insert(
            "messages",
            {
                "case_id": case_id,
                "webhook_event_id": reply_to_webhook_event_id,
                "sender_type": "ai",
                "channel": "line",
                "body": body,
                "message_type": "text",
                "raw_payload": raw_payload or {},
            },
        )

    async def get_active_case(self, *, line_user_db_id: str) -> dict[str, Any] | None:
        rows = await self.client.select_by_eq(
            "cases",
            "line_user_id",
            line_user_db_id,
            select="id,case_code,status,route_type,created_at",
            limit=20,
        )
        active_statuses = {"open", "collecting", "waiting_investigator", "in_consultation"}
        active_rows = [row for row in rows if row.get("status") in active_statuses]
        if not active_rows:
            return None
        return sorted(
            active_rows,
            key=lambda row: str(row.get("created_at") or ""),
            reverse=True,
        )[0]

    async def create_case(self, *, line_user_db_id: str, case_code: str) -> dict[str, Any] | None:
        rows = await self.client.insert(
            "cases",
            {
                "case_code": case_code,
                "line_user_id": line_user_db_id,
                "route_type": "undecided",
                "status": "collecting",
                "urgency": "unknown",
            },
        )
        return rows[0] if rows else None

    async def close_case(self, *, case_id: str) -> None:
        await self.client.update_by_eq(
            "cases",
            "id",
            case_id,
            {"status": "closed", "completed_at": _now_iso()},
        )

    async def update_case_route(self, *, case_id: str, route_type: str, status: str) -> None:
        payload: dict[str, Any] = {"route_type": route_type, "status": status}
        if status in {"completed", "closed"}:
            payload["completed_at"] = _now_iso()
        await self.client.update_by_eq("cases", "id", case_id, payload)

    async def attach_message_to_case(self, *, webhook_event_id: str, case_id: str) -> None:
        if not webhook_event_id:
            return
        await self.client.update_by_eq(
            "messages",
            "webhook_event_id",
            webhook_event_id,
            {"case_id": case_id},
        )

    async def count_case_user_messages(self, *, case_id: str) -> int:
        rows = await self.client.select_by_eq(
            "messages",
            "case_id",
            case_id,
            select="id,sender_type,message_type,body",
            limit=100,
        )
        return sum(
            1
            for row in rows
            if row.get("sender_type") == "user"
            and row.get("message_type") == "text"
            and isinstance(row.get("body"), str)
            and row.get("body")
        )

    async def create_chatwork_notification(
        self,
        *,
        case_id: str,
        room_id: str,
        message_body: str,
        status: str,
        chatwork_message_id: str | None = None,
        error_message: str | None = None,
    ) -> None:
        payload = {
            "case_id": case_id,
            "room_id": room_id,
            "message_body": message_body,
            "status": status,
            "chatwork_message_id": chatwork_message_id,
            "error_message": error_message,
        }
        if status == "sent":
            payload["sent_at"] = _now_iso()
        await self.client.insert("chatwork_notifications", payload)

    async def update_line_user_profile(
        self,
        *,
        line_user_db_id: str,
        display_name: str | None = None,
        picture_url: str | None = None,
    ) -> None:
        payload: dict[str, Any] = {"last_seen_at": _now_iso(), "is_active": True}
        if display_name:
            payload["display_name"] = display_name
        if picture_url:
            payload["picture_url"] = picture_url
        await self.client.update_by_eq("line_users", "id", line_user_db_id, payload)

    async def _upsert_line_user(self, event: dict[str, Any]) -> dict[str, Any] | None:
        line_user_id = _line_user_id(event)
        if not line_user_id:
            return None

        existing = await self.client.select_by_eq("line_users", "line_user_id", line_user_id)
        if existing:
            rows = await self.client.update_by_eq(
                "line_users",
                "line_user_id",
                line_user_id,
                {"last_seen_at": _now_iso(), "is_active": True},
            )
            return rows[0] if rows else existing[0]

        now = _now_iso()
        rows = await self.client.insert(
            "line_users",
            {
                "line_user_id": line_user_id,
                "first_seen_at": now,
                "last_seen_at": now,
                "is_active": True,
            },
        )
        return rows[0] if rows else None


def _webhook_event_id(event: dict[str, Any]) -> str:
    value = event.get("webhookEventId")
    return value if isinstance(value, str) else ""


def _line_user_id(event: dict[str, Any]) -> str:
    source = event.get("source")
    if not isinstance(source, dict):
        return ""
    value = source.get("userId")
    return value if isinstance(value, str) else ""


def _postback_data(event: dict[str, Any]) -> str | None:
    postback = event.get("postback")
    if not isinstance(postback, dict):
        return None
    value = postback.get("data")
    return value if isinstance(value, str) else None


def _text_message_body(event: dict[str, Any]) -> str | None:
    if event.get("type") != "message":
        return None
    message = event.get("message")
    if not isinstance(message, dict):
        return None
    if message.get("type") != "text":
        return None
    value = message.get("text")
    return value if isinstance(value, str) else None


def _message_payload(event: dict[str, Any], *, line_user_id: str | None) -> dict[str, Any] | None:
    if event.get("type") != "message":
        return None

    message = event.get("message")
    if not isinstance(message, dict):
        return None

    message_type = message.get("type")
    body = message.get("text") if message_type == "text" else None

    return {
        "webhook_event_id": _webhook_event_id(event),
        "sender_type": "user",
        "sender_line_user_id": line_user_id,
        "channel": "line",
        "body": body if isinstance(body, str) else None,
        "message_type": message_type if isinstance(message_type, str) else None,
        "raw_payload": event,
    }


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
