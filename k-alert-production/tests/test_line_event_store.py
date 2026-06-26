import json

import httpx
import pytest

from app.services.line_event_store import SupabaseLineEventStore
from app.services.line_webhook_service import (
    EMERGENCY_RECOMMENDATION_MESSAGE,
    EMPATHY_CHOICE_MESSAGE,
    INTRO_MESSAGE,
    LEGACY_REPORT_COMPLETION_MESSAGES,
    REPORT_COMPLETION_NO_CONSULTATION_MESSAGE,
    REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE,
    ROUTE_DECISION_MESSAGE,
    LineWebhookService,
)


class FakeSupabaseClient:
    def __init__(
        self,
        *,
        duplicate_webhook_ids: set[str] | None = None,
        active_case: dict | None = None,
        case_message_rows: list[dict] | None = None,
    ) -> None:
        self.duplicate_webhook_ids = duplicate_webhook_ids or set()
        self.active_case = active_case
        self.case_message_rows = case_message_rows or []
        self.selects: list[tuple[str, str, str]] = []
        self.updates: list[tuple[str, str, str, dict]] = []
        self.inserts: list[tuple[str, dict]] = []

    async def select_by_eq(
        self,
        table: str,
        column: str,
        value: str,
        *,
        select: str = "*",
        limit: int = 1,
    ) -> list[dict]:
        self.selects.append((table, column, value))
        if table == "cases" and self.active_case:
            return [self.active_case]
        if table == "messages" and column == "case_id":
            return self.case_message_rows
        return []

    async def update_by_eq(self, table: str, column: str, value: str, payload: dict) -> list[dict]:
        self.updates.append((table, column, value, payload))
        return [{"id": "line-user-uuid", **payload}]

    async def insert(self, table: str, payload: dict) -> list[dict]:
        if table == "webhook_events" and payload["webhook_event_id"] in self.duplicate_webhook_ids:
            request = httpx.Request("POST", "https://example.supabase.co/rest/v1/webhook_events")
            response = httpx.Response(409, request=request)
            raise httpx.HTTPStatusError("duplicate", request=request, response=response)
        self.inserts.append((table, payload))
        if table == "line_users":
            return [{"id": "line-user-uuid", **payload}]
        if table == "cases":
            return [{"id": "case-uuid", **payload}]
        return [{"id": "inserted-uuid", **payload}]


class FakeLineMessagingClient:
    def __init__(self) -> None:
        self.replies: list[tuple[str, str, dict | None]] = []
        self.message_replies: list[tuple[str, list[dict]]] = []
        self.profile: dict | None = None

    async def reply_messages(
        self,
        *,
        reply_token: str,
        messages: list[dict],
    ) -> None:
        self.message_replies.append((reply_token, messages))

    async def reply_text(
        self,
        *,
        reply_token: str,
        text: str,
        quick_reply: dict | None = None,
    ) -> None:
        self.replies.append((reply_token, text, quick_reply))

    async def get_profile(self, *, user_id: str) -> dict | None:
        return self.profile


class FakeChatWorkClient:
    def __init__(self, message_id: str | None = "chatwork-message-1") -> None:
        self.message_id = message_id
        self.messages: list[tuple[str, str]] = []

    async def send_message(self, *, room_id: str, body: str) -> str | None:
        self.messages.append((room_id, body))
        return self.message_id


@pytest.mark.asyncio
async def test_store_text_message_event_writes_user_event_and_message() -> None:
    client = FakeSupabaseClient()
    store = SupabaseLineEventStore(client)

    stored = await store.store_event(
        {
            "type": "message",
            "webhookEventId": "event-1",
            "source": {"type": "user", "userId": "U123"},
            "message": {"id": "msg-1", "type": "text", "text": "相談したいです"},
        }
    )

    assert stored.stored is True
    assert stored.line_user_db_id == "line-user-uuid"
    assert stored.message_text == "相談したいです"
    assert client.selects[0] == ("line_users", "line_user_id", "U123")
    assert client.inserts[0][0] == "line_users"
    assert client.inserts[0][1]["line_user_id"] == "U123"
    assert client.inserts[1][0] == "webhook_events"
    assert client.inserts[1][1]["webhook_event_id"] == "event-1"
    assert client.inserts[2][0] == "messages"
    assert client.inserts[2][1]["body"] == "相談したいです"
    assert client.inserts[2][1]["sender_line_user_id"] == "line-user-uuid"


@pytest.mark.asyncio
async def test_line_webhook_service_updates_line_user_profile() -> None:
    client = FakeSupabaseClient()
    store = SupabaseLineEventStore(client)
    messaging = FakeLineMessagingClient()
    messaging.profile = {
        "userId": "U123",
        "displayName": "ジンノウチさん",
        "pictureUrl": "https://example.com/profile.jpg",
    }
    service = LineWebhookService(event_store=store, messaging_client=messaging)

    body = json.dumps(
        {
            "events": [
                {
                    "type": "message",
                    "webhookEventId": "event-profile",
                    "replyToken": "reply-1",
                    "source": {"userId": "U123"},
                    "message": {"type": "text", "text": "こんにちは"},
                }
            ]
        },
        ensure_ascii=False,
    ).encode("utf-8")

    await service.handle_raw_webhook(body)

    assert (
        "line_users",
        "id",
        "line-user-uuid",
        {
            "last_seen_at": client.updates[0][3]["last_seen_at"],
            "is_active": True,
            "display_name": "ジンノウチさん",
            "picture_url": "https://example.com/profile.jpg",
        },
    ) in client.updates


@pytest.mark.asyncio
async def test_line_webhook_service_counts_duplicate_events() -> None:
    client = FakeSupabaseClient(duplicate_webhook_ids={"event-1"})
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )

    result = await service.handle_raw_webhook(
        b'{"events":[{"type":"message","webhookEventId":"event-1","replyToken":"reply-1",'
        b'"source":{"userId":"U123"}}]}'
    )

    assert result.handled is True
    assert result.event_count == 1
    assert result.duplicate_count == 1
    assert result.reply_count == 0
    assert not any(table == "messages" for table, _ in client.inserts)
    assert messaging.replies == []
    assert messaging.message_replies == []


@pytest.mark.asyncio
async def test_line_webhook_service_does_not_reply_to_message_outside_session() -> None:
    client = FakeSupabaseClient()
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-1","replyToken":"reply-1",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"相談です"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 0
    assert messaging.replies == []
    assert messaging.message_replies == []


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "completion_message",
    [
        REPORT_COMPLETION_NO_CONSULTATION_MESSAGE,
        REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE,
        *LEGACY_REPORT_COMPLETION_MESSAGES,
    ],
)
async def test_line_webhook_service_ignores_liff_completion_chat_message(
    completion_message: str,
) -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "completed",
            "route_type": "anonymous_report",
            "created_at": "2026-06-25T00:00:00+00:00",
        }
    )
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = json.dumps(
        {
            "events": [
                {
                    "type": "message",
                    "webhookEventId": "event-liff-done",
                    "replyToken": "reply-liff-done",
                    "source": {"userId": "U123"},
                    "message": {"type": "text", "text": completion_message},
                }
            ]
        },
        ensure_ascii=False,
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 0
    assert messaging.replies == []
    assert messaging.message_replies == []


@pytest.mark.asyncio
async def test_line_webhook_service_starts_chat_on_consult_text() -> None:
    client = FakeSupabaseClient()
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-1","replyToken":"reply-1",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"相談する"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert messaging.replies[0][0:2] == ("reply-1", INTRO_MESSAGE)
    quick_reply_items = messaging.replies[0][2]["items"]
    assert quick_reply_items[0]["action"]["data"] == "action=end_consult"
    assert quick_reply_items[1]["action"]["text"] == "調査官相談"
    assert quick_reply_items[2]["action"]["text"] == "通報する"
    assert any(table == "cases" for table, _ in client.inserts)
    assert any(
        table == "messages" and payload.get("case_id") == "case-uuid"
        for table, payload in client.inserts
    )
    ai_messages = []
    for table, payload in client.inserts:
        if table == "messages" and payload["sender_type"] == "ai":
            ai_messages.append(payload)
    assert len(ai_messages) == 1
    assert ai_messages[0]["body"] == INTRO_MESSAGE
    assert ai_messages[0]["case_id"] == "case-uuid"


@pytest.mark.asyncio
async def test_line_webhook_service_replies_with_empathy_and_route_choices() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        }
    )
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-5","replyToken":"reply-5",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"職場で強く責められました"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert messaging.replies[0][1] == EMPATHY_CHOICE_MESSAGE
    quick_reply_items = messaging.replies[0][2]["items"]
    assert quick_reply_items[0]["action"]["data"] == "action=end_consult"
    assert quick_reply_items[1]["action"]["text"] == "調査官相談"
    assert quick_reply_items[2]["action"]["text"] == "通報する"


@pytest.mark.asyncio
async def test_line_webhook_service_routes_after_second_chat_message() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        },
        case_message_rows=[
            {"sender_type": "user", "message_type": "text", "body": "つらいです"},
            {"sender_type": "user", "message_type": "text", "body": "上司から強く責められた"},
        ],
    )
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-6","replyToken":"reply-6",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"上司から強く責められた"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert messaging.replies[0][1] == ROUTE_DECISION_MESSAGE
    quick_reply_items = messaging.replies[0][2]["items"]
    assert quick_reply_items[1]["action"]["text"] == "調査官相談"
    assert quick_reply_items[2]["action"]["text"] == "通報する"


@pytest.mark.asyncio
async def test_line_webhook_service_guides_emergency_to_110_or_119() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        },
        case_message_rows=[
            {"sender_type": "user", "message_type": "text", "body": "殺されるかもしれない"},
        ],
    )
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-7","replyToken":"reply-7",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"殺されるかもしれない"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert messaging.replies[0][1] == EMERGENCY_RECOMMENDATION_MESSAGE
    assert "110番または119番" in messaging.replies[0][1]


@pytest.mark.asyncio
async def test_line_webhook_service_creates_case_for_report_link_trigger() -> None:
    client = FakeSupabaseClient()
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
        report_liff_url="https://liff.line.me/example",
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-report","replyToken":"reply-report",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"通報する"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert any(table == "cases" for table, _ in client.inserts)
    flex_message = messaging.message_replies[0][1][0]
    assert flex_message["altText"] == "通報する"
    button_action = flex_message["contents"]["body"]["contents"][1]["contents"][1]["action"]
    assert button_action["type"] == "uri"
    assert button_action["uri"].startswith("https://liff.line.me/example?case_code=")
    assert any(
        update[0] == "cases"
        and update[3]["route_type"] == "anonymous_report"
        and update[3]["status"] == "collecting"
        for update in client.updates
    )


@pytest.mark.asyncio
async def test_line_webhook_service_marks_anonymous_report_route() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        }
    )
    messaging = FakeLineMessagingClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
        report_liff_url="https://liff.line.me/example",
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-2","replyToken":"reply-2",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"匿名報告"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    expected_update = (
        "cases",
        "id",
        "case-uuid",
        {"route_type": "anonymous_report", "status": "collecting"},
    )
    assert expected_update in [
        update[:3] + ({"route_type": update[3]["route_type"], "status": update[3]["status"]},)
        for update in client.updates
        if update[0] == "cases"
    ]
    flex_message = messaging.message_replies[0][1][0]
    assert flex_message["altText"] == "通報する"
    button_action = flex_message["contents"]["body"]["contents"][1]["contents"][1]["action"]
    assert button_action["uri"] == "https://liff.line.me/example?case_code=K20260625-ABC123"


@pytest.mark.asyncio
async def test_line_webhook_service_shows_investigator_confirm_card() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        }
    )
    messaging = FakeLineMessagingClient()
    chatwork = FakeChatWorkClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
        chatwork_client=chatwork,
        chatwork_room_id="room-1",
    )
    body = (
        '{"events":[{"type":"message","webhookEventId":"event-3","replyToken":"reply-3",'
        '"source":{"userId":"U123"},"message":{"type":"text","text":"調査官相談"}}]}'
    ).encode()

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert chatwork.messages == []
    flex_message = messaging.message_replies[0][1][0]
    assert flex_message["altText"] == "報告せずに調査官に依頼する"
    button_action = flex_message["contents"]["body"]["contents"][1]["contents"][1]["action"]
    assert button_action["type"] == "postback"
    assert button_action["data"] == "action=investigator_consult"
    assert button_action["label"] == "調査官に依頼する"


@pytest.mark.asyncio
async def test_line_webhook_service_marks_investigator_route_after_confirm_postback() -> None:
    client = FakeSupabaseClient(
        active_case={
            "id": "case-uuid",
            "case_code": "K20260625-ABC123",
            "status": "collecting",
            "route_type": "undecided",
            "created_at": "2026-06-25T00:00:00+00:00",
        }
    )
    messaging = FakeLineMessagingClient()
    chatwork = FakeChatWorkClient()
    service = LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging,
        chatwork_client=chatwork,
        chatwork_room_id="room-1",
    )
    body = (
        b'{"events":[{"type":"postback","webhookEventId":"event-4","replyToken":"reply-4",'
        b'"source":{"userId":"U123"},"postback":{"data":"action=investigator_consult"}}]}'
    )

    result = await service.handle_raw_webhook(body)

    assert result.reply_count == 1
    assert chatwork.messages[0][0] == "room-1"
    assert "K20260625-ABC123" in chatwork.messages[0][1]
    assert any(
        update[0] == "cases"
        and update[3]["route_type"] == "investigator_consultation"
        and update[3]["status"] == "waiting_investigator"
        for update in client.updates
    )
    assert any(
        table == "chatwork_notifications" and payload["status"] == "sent"
        for table, payload in client.inserts
    )
