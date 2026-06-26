import json
import secrets
import string
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.core.config import get_settings
from app.core.supabase import SupabaseConfigError, create_supabase_client
from app.services.ai_chat import AiChatClient, NullAiChatClient, create_ai_chat_client
from app.services.chatwork import ChatWorkApiClient, ChatWorkClient, NullChatWorkClient
from app.services.line_event_store import (
    LineEventStore,
    NullLineEventStore,
    StoredLineEvent,
    SupabaseLineEventStore,
)
from app.services.line_messaging import (
    LineMessagingApiClient,
    LineMessagingClient,
    NullLineMessagingClient,
)

CONSULT_START_TEXTS = {"相談する"}
CONSULT_START_POSTBACK = "action=consult"
CONSULT_END_POSTBACK = "action=end_consult"
INVESTIGATOR_CONSULT_POSTBACK = "action=investigator_consult"
CONSULT_END_LABEL = "相談を終了する"
REPORT_LINK_TEXTS = {"通報する"}
DEVELOPMENT_TEXTS = {"大人の保健室"}
REPORT_COMPLETION_NO_CONSULTATION_MESSAGE = (
    "🛡️ Kアラートからのメッセージ 🛡️\n\n"
    "通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。"
)
REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE = (
    "🛡️ Kアラートからのメッセージ 🛡️\n\n"
    "通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。\n\n"
    "調査官より、改めてチャットでご連絡しますのでご不安な点があればご相談ください。"
)
LEGACY_REPORT_COMPLETION_MESSAGES = (
    "報告書提出完了しました。内容は匿名で企業に提出致しますのでご安心ください。必要に応じて再度相談を行ってください。",
    (
        "通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。\n\n"
        "調査官より、改めてチャットでご連絡しますのでご不安な点があればご相談ください。"
    ),
    "通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。",
)
REPORT_COMPLETION_CHAT_MESSAGES = (
    REPORT_COMPLETION_NO_CONSULTATION_MESSAGE,
    REPORT_COMPLETION_WITH_CONSULTATION_MESSAGE,
    *LEGACY_REPORT_COMPLETION_MESSAGES,
)
ANONYMOUS_REPORT_TEXTS = {
    "匿名報告",
    "匿名報告する",
    "匿名で報告",
    "匿名で報告する",
    "報告する",
    "企業へ報告",
    "企業への匿名報告",
}
INVESTIGATOR_CONSULT_TEXTS = {
    "調査官相談",
    "調査官に相談",
    "調査官に相談する",
    "調査官への相談",
}

INTRO_MESSAGE = (
    "こんにちは。Kアラートです🛡️\n\n"
    "このLINEのチャット内容は、匿名相談として取り扱います。\n"
    "安心して、話せる範囲で大丈夫です。\n\n"
    "必要に応じて、皆さまに危害が及ばないよう担当者より対応します。\n\n"
    "今回はどのような事象がありましたか？"
)
CONSULT_END_MESSAGE = "相談を終了しました。必要なときは、また「相談する」から開始してください。"
EMPATHY_CHOICE_MESSAGE = (
    "話してくださってありがとうございます。\n\n"
    "つらい状況だったと思います。続けて、覚えている範囲で教えてください。"
)
ROUTE_DECISION_MESSAGE = (
    "今回のご相談を、匿名で会社に報告しますか？\n\n"
    "報告しない場合でも、担当の調査官にチャットで相談できます。"
)
EMERGENCY_RECOMMENDATION_MESSAGE = (
    "緊急の可能性があります。\n\n"
    "生命・身体・財産に危険がある場合は、このチャットより先に110番または119番へ"
    "連絡してください。\n\n"
    "吐き気が止まらない、意識がぼんやりする、強い痛みがある場合は119番に相談してください。"
)
DEVELOPMENT_MESSAGE = "開発中です。"
REPORT_LINK_UNAVAILABLE_MESSAGE = (
    "匿名報告フォームは現在準備中です。お急ぎの場合は「相談する」から状況をお知らせください。"
)
REPORT_LINK_TITLE = "通報する"
REPORT_LINK_BODY = "生命・身体・財産に対して急を要する場合は110番・119番してください"
REPORT_LINK_BUTTON = "通報フォームを開く"
INVESTIGATOR_CARD_TITLE = "報告せずに調査官に依頼する"
INVESTIGATOR_CARD_BUTTON = "調査官に依頼する"
ANONYMOUS_REPORT_ACCEPTED_MESSAGE = (
    "匿名報告は専用フォームで受け付けています。下のリンクから、いつ・どこで・"
    "どのようなことがあったかを入力してください。"
)
INVESTIGATOR_REQUEST_ACCEPTED_MESSAGE = (
    "調査官への相談希望として記録しました。担当者が確認できるよう準備します。"
)


@dataclass(frozen=True)
class LineWebhookResult:
    handled: bool
    event_count: int
    duplicate_count: int = 0
    reply_count: int = 0


class LineWebhookService:
    def __init__(
        self,
        event_store: LineEventStore | None = None,
        messaging_client: LineMessagingClient | None = None,
        chatwork_client: ChatWorkClient | None = None,
        ai_chat_client: AiChatClient | None = None,
        chatwork_room_id: str = "",
        report_liff_url: str = "",
    ) -> None:
        self.event_store = event_store or NullLineEventStore()
        self.messaging_client = messaging_client or NullLineMessagingClient()
        self.chatwork_client = chatwork_client or NullChatWorkClient()
        self.ai_chat_client = ai_chat_client or NullAiChatClient()
        self.chatwork_room_id = chatwork_room_id
        self.report_liff_url = report_liff_url

    async def handle_raw_webhook(self, body: bytes) -> LineWebhookResult:
        payload = self._parse_payload(body)
        events = payload.get("events", [])
        if not isinstance(events, list):
            return LineWebhookResult(handled=False, event_count=0)

        duplicate_count = 0
        reply_count = 0
        for event in events:
            if not isinstance(event, dict):
                continue
            stored = await self.event_store.store_event(event)
            if not stored.stored:
                duplicate_count += 1
                continue
            await self._refresh_line_user_profile(stored)
            replied = await self._reply_to_event(stored, event)
            if replied:
                reply_count += 1

        return LineWebhookResult(
            handled=True,
            event_count=len(events),
            duplicate_count=duplicate_count,
            reply_count=reply_count,
        )

    def _parse_payload(self, body: bytes) -> dict[str, Any]:
        try:
            payload = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return {}
        return payload if isinstance(payload, dict) else {}

    async def _reply_to_event(self, stored: StoredLineEvent, event: dict[str, Any]) -> bool:
        reply_token = event.get("replyToken")
        if not isinstance(reply_token, str) or not reply_token:
            return False

        if stored.postback_data == CONSULT_START_POSTBACK:
            case = await self._start_or_get_case(stored)
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=INTRO_MESSAGE,
                case_id=_case_id(case),
                raw_message_type="consult_start",
                quick_reply=_consult_quick_reply(),
            )
            return True

        if stored.postback_data == CONSULT_END_POSTBACK:
            case = await self._get_active_case(stored)
            if case:
                await self.event_store.close_case(case_id=str(case["id"]))
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=CONSULT_END_MESSAGE,
                case_id=_case_id(case),
                raw_message_type="consult_end",
            )
            return True

        if stored.postback_data == INVESTIGATOR_CONSULT_POSTBACK:
            case = await self._get_active_case(stored)
            case_id = _case_id(case)
            if case_id:
                await self.event_store.update_case_route(
                    case_id=case_id,
                    route_type="investigator_consultation",
                    status="waiting_investigator",
                )
                await self._notify_investigator(case=case)
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=INVESTIGATOR_REQUEST_ACCEPTED_MESSAGE,
                case_id=case_id,
                raw_message_type="investigator_consult_confirmed",
            )
            return True

        if stored.event_type != "message":
            return False
        text = (stored.message_text or "").strip()
        if not text:
            return False

        if text in REPORT_COMPLETION_CHAT_MESSAGES:
            return False

        if text in REPORT_LINK_TEXTS:
            case = await self._start_or_get_case(stored)
            case_id = _case_id(case)
            if case_id and stored.webhook_event_id:
                await self.event_store.attach_message_to_case(
                    webhook_event_id=stored.webhook_event_id,
                    case_id=case_id,
                )
                await self.event_store.update_case_route(
                    case_id=case_id,
                    route_type="anonymous_report",
                    status="collecting",
                )
            await self._reply_report_link(
                stored,
                reply_token=reply_token,
                case_id=case_id,
                case_code=_case_code(case),
                intro_text=ANONYMOUS_REPORT_ACCEPTED_MESSAGE,
            )
            return True

        if text in DEVELOPMENT_TEXTS:
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=DEVELOPMENT_MESSAGE,
                raw_message_type="development",
            )
            return True

        if text in CONSULT_START_TEXTS:
            case = await self._start_or_get_case(stored)
            case_id = _case_id(case)
            if case_id and stored.webhook_event_id:
                await self.event_store.attach_message_to_case(
                    webhook_event_id=stored.webhook_event_id,
                    case_id=case_id,
                )
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=INTRO_MESSAGE,
                case_id=case_id,
                raw_message_type="consult_start",
                quick_reply=_consult_quick_reply(),
            )
            return True

        case = await self._get_active_case(stored)
        if not case:
            return False

        case_id = _case_id(case)
        if case_id and stored.webhook_event_id:
            await self.event_store.attach_message_to_case(
                webhook_event_id=stored.webhook_event_id,
                case_id=case_id,
            )

        if text in ANONYMOUS_REPORT_TEXTS and case_id:
            await self.event_store.update_case_route(
                case_id=case_id,
                route_type="anonymous_report",
                status="collecting",
            )
            await self._reply_report_link(
                stored,
                reply_token=reply_token,
                case_id=case_id,
                case_code=_case_code(case),
                intro_text=ANONYMOUS_REPORT_ACCEPTED_MESSAGE,
            )
            return True

        if text in INVESTIGATOR_CONSULT_TEXTS and case_id:
            await self._reply_investigator_confirm_card(
                stored,
                reply_token=reply_token,
                case_id=case_id,
            )
            return True

        user_message_count = await self.event_store.count_case_user_messages(case_id=case_id)
        emergency_hint = _is_emergency_text(text)
        ai_result = await self._generate_ai_reply(
            text=text,
            turn_count=user_message_count,
            emergency_hint=emergency_hint,
        )
        if ai_result.emergency:
            body = EMERGENCY_RECOMMENDATION_MESSAGE
            raw_message_type = "emergency_recommendation"
            if user_message_count >= 2:
                body = _join_ai_or_fallback(
                    primary=ai_result.reply_text,
                    fallback=f"{body}\n\n{ROUTE_DECISION_MESSAGE}",
                )
                raw_message_type = "emergency_route_decision"
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=body,
                case_id=case_id,
                raw_message_type=raw_message_type,
                quick_reply=_consult_quick_reply(),
            )
            return True

        if user_message_count >= 2:
            await self._reply_and_store(
                stored,
                reply_token=reply_token,
                body=_join_ai_or_fallback(
                    primary=ai_result.reply_text,
                    fallback=ROUTE_DECISION_MESSAGE,
                ),
                case_id=case_id,
                raw_message_type="ai_route_decision",
                quick_reply=_consult_quick_reply(),
            )
            return True

        await self._reply_and_store(
            stored,
            reply_token=reply_token,
            body=_join_ai_or_fallback(
                primary=ai_result.reply_text,
                fallback=EMPATHY_CHOICE_MESSAGE,
            ),
            case_id=case_id,
            raw_message_type="ai_empathy",
            quick_reply=_route_choice_quick_reply(),
        )
        return True

    async def _generate_ai_reply(
        self,
        *,
        text: str,
        turn_count: int,
        emergency_hint: bool,
    ):
        try:
            return await self.ai_chat_client.generate_consultation_reply(
                user_text=text,
                turn_count=turn_count,
                emergency_hint=emergency_hint,
            )
        except Exception:
            return await NullAiChatClient().generate_consultation_reply(
                user_text=text,
                turn_count=turn_count,
                emergency_hint=emergency_hint,
            )

    async def _refresh_line_user_profile(self, stored: StoredLineEvent) -> None:
        if not stored.line_user_id or not stored.line_user_db_id:
            return
        try:
            profile = await self.messaging_client.get_profile(user_id=stored.line_user_id)
        except Exception:
            return
        if not profile:
            return
        display_name = profile.get("displayName")
        picture_url = profile.get("pictureUrl")
        await self.event_store.update_line_user_profile(
            line_user_db_id=stored.line_user_db_id,
            display_name=display_name if isinstance(display_name, str) else None,
            picture_url=picture_url if isinstance(picture_url, str) else None,
        )

    async def _notify_investigator(self, *, case: dict[str, Any]) -> None:
        case_id = _case_id(case)
        if not case_id:
            return

        case_code = str(case.get("case_code") or case_id)
        message_body = (
            "[Kアラート]\n"
            "調査官相談の希望が入りました。\n"
            f"case_code: {case_code}\n"
            f"対応開始時は「対応開始 {case_code}」を送信してください。"
        )
        if not self.chatwork_room_id:
            await self.event_store.create_chatwork_notification(
                case_id=case_id,
                room_id="",
                message_body=message_body,
                status="pending",
                error_message="CHATWORK_ROOM_ID is not configured.",
            )
            return

        try:
            message_id = await self.chatwork_client.send_message(
                room_id=self.chatwork_room_id,
                body=message_body,
            )
        except Exception as exc:
            await self.event_store.create_chatwork_notification(
                case_id=case_id,
                room_id=self.chatwork_room_id,
                message_body=message_body,
                status="failed",
                error_message=type(exc).__name__,
            )
            return

        await self.event_store.create_chatwork_notification(
            case_id=case_id,
            room_id=self.chatwork_room_id,
            message_body=message_body,
            status="sent" if message_id else "pending",
            chatwork_message_id=message_id,
        )

    async def _reply_report_link(
        self,
        stored: StoredLineEvent,
        *,
        reply_token: str,
        case_id: str | None = None,
        case_code: str | None = None,
        intro_text: str | None = None,
    ) -> None:
        if self.report_liff_url:
            report_url = _with_case_code(self.report_liff_url, case_code)
            body = f"{intro_text or '匿名報告フォームはこちらです。'}\n{report_url}"
            raw_message_type = "report_link"
            await self.messaging_client.reply_messages(
                reply_token=reply_token,
                messages=[_report_link_flex_message(report_url)],
            )
            if stored.webhook_event_id:
                await self.event_store.store_ai_message(
                    reply_to_webhook_event_id=stored.webhook_event_id,
                    body=body,
                    case_id=case_id,
                    raw_payload={
                        "replyToken": reply_token,
                        "message_type": raw_message_type,
                        "line_message_type": "flex",
                    },
                )
            return
        else:
            body = REPORT_LINK_UNAVAILABLE_MESSAGE
            raw_message_type = "report_link_unavailable"
        await self._reply_and_store(
            stored,
            reply_token=reply_token,
            body=body,
            case_id=case_id,
            raw_message_type=raw_message_type,
        )

    async def _reply_and_store(
        self,
        stored: StoredLineEvent,
        *,
        reply_token: str,
        body: str,
        case_id: str | None = None,
        raw_message_type: str,
        quick_reply: dict[str, Any] | None = None,
    ) -> None:
        await self.messaging_client.reply_text(
            reply_token=reply_token,
            text=body,
            quick_reply=quick_reply,
        )
        if stored.webhook_event_id:
            await self.event_store.store_ai_message(
                reply_to_webhook_event_id=stored.webhook_event_id,
                body=body,
                case_id=case_id,
                raw_payload={"replyToken": reply_token, "message_type": raw_message_type},
        )

    async def _reply_investigator_confirm_card(
        self,
        stored: StoredLineEvent,
        *,
        reply_token: str,
        case_id: str | None = None,
    ) -> None:
        await self.messaging_client.reply_messages(
            reply_token=reply_token,
            messages=[_investigator_confirm_flex_message()],
        )
        if stored.webhook_event_id:
            await self.event_store.store_ai_message(
                reply_to_webhook_event_id=stored.webhook_event_id,
                body=INVESTIGATOR_CARD_TITLE,
                case_id=case_id,
                raw_payload={
                    "replyToken": reply_token,
                    "message_type": "investigator_consult_confirm_card",
                    "line_message_type": "flex",
                },
            )

    async def _start_or_get_case(self, stored: StoredLineEvent) -> dict[str, Any] | None:
        active_case = await self._get_active_case(stored)
        if active_case:
            return active_case
        if not stored.line_user_db_id:
            return None
        return await self.event_store.create_case(
            line_user_db_id=stored.line_user_db_id,
            case_code=_new_case_code(),
        )

    async def _get_active_case(self, stored: StoredLineEvent) -> dict[str, Any] | None:
        if not stored.line_user_db_id:
            return None
        return await self.event_store.get_active_case(line_user_db_id=stored.line_user_db_id)


def get_line_webhook_service() -> LineWebhookService:
    settings = get_settings()
    try:
        client = create_supabase_client(settings)
    except SupabaseConfigError:
        if settings.app_env in {"local", "test"}:
            return LineWebhookService()
        raise

    messaging_client: LineMessagingClient
    if settings.line_channel_access_token:
        messaging_client = LineMessagingApiClient(settings.line_channel_access_token)
    elif settings.app_env in {"local", "test"}:
        messaging_client = NullLineMessagingClient()
    else:
        raise RuntimeError("LINE channel access token is not configured.")

    chatwork_client: ChatWorkClient
    if settings.chatwork_api_token:
        chatwork_client = ChatWorkApiClient(settings.chatwork_api_token)
    else:
        chatwork_client = NullChatWorkClient()

    return LineWebhookService(
        event_store=SupabaseLineEventStore(client),
        messaging_client=messaging_client,
        chatwork_client=chatwork_client,
        ai_chat_client=create_ai_chat_client(settings),
        chatwork_room_id=settings.chatwork_room_id,
        report_liff_url=getattr(settings, "k_alert_liff_url", ""),
    )


def _consult_quick_reply() -> dict[str, Any]:
    return {
        "items": [
            {
                "type": "action",
                "action": {
                    "type": "postback",
                    "label": CONSULT_END_LABEL,
                    "data": CONSULT_END_POSTBACK,
                    "displayText": CONSULT_END_LABEL,
                },
            },
            {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "調査を依頼する",
                    "text": "調査官相談",
                },
            },
            {
                "type": "action",
                "action": {
                    "type": "message",
                    "label": "通報する",
                    "text": "通報する",
                },
            },
        ]
    }


def _route_choice_quick_reply() -> dict[str, Any]:
    return _consult_quick_reply()


def _is_emergency_text(text: str) -> bool:
    emergency_keywords = {
        "110",
        "119",
        "救急",
        "警察",
        "殺",
        "死ね",
        "死ぬ",
        "命",
        "生命",
        "身体",
        "財産",
        "危険",
        "暴力",
        "脅迫",
        "刃物",
        "痛み",
        "吐き気",
        "意識",
        "倒れ",
    }
    return any(keyword in text for keyword in emergency_keywords)


def _join_ai_or_fallback(*, primary: str, fallback: str) -> str:
    normalized = primary.strip()
    return normalized if normalized else fallback


def _report_link_flex_message(report_url: str) -> dict[str, Any]:
    return {
        "type": "flex",
        "altText": REPORT_LINK_TITLE,
        "contents": {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "0px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#142d52",
                        "paddingTop": "7px",
                        "paddingBottom": "7px",
                        "paddingStart": "12px",
                        "paddingEnd": "12px",
                        "contents": [
                            {
                                "type": "text",
                                "text": REPORT_LINK_TITLE,
                                "color": "#ffd84a",
                                "weight": "bold",
                                "size": "sm",
                            }
                        ],
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "paddingAll": "12px",
                        "spacing": "8px",
                        "contents": [
                            {
                                "type": "text",
                                "text": REPORT_LINK_BODY,
                                "color": "#4b5563",
                                "size": "xs",
                                "wrap": True,
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "color": "#5ecf5f",
                                "action": {
                                    "type": "uri",
                                    "label": REPORT_LINK_BUTTON,
                                    "uri": report_url,
                                },
                            },
                        ],
                    },
                ],
            },
        },
    }


def _investigator_confirm_flex_message() -> dict[str, Any]:
    return {
        "type": "flex",
        "altText": INVESTIGATOR_CARD_TITLE,
        "contents": {
            "type": "bubble",
            "size": "kilo",
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "0px",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#142d52",
                        "paddingTop": "7px",
                        "paddingBottom": "7px",
                        "paddingStart": "12px",
                        "paddingEnd": "12px",
                        "contents": [
                            {
                                "type": "text",
                                "text": INVESTIGATOR_CARD_TITLE,
                                "color": "#ffd84a",
                                "weight": "bold",
                                "size": "sm",
                                "wrap": True,
                            }
                        ],
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "paddingAll": "12px",
                        "spacing": "8px",
                        "contents": [
                            {
                                "type": "text",
                                "text": REPORT_LINK_BODY,
                                "color": "#4b5563",
                                "size": "xs",
                                "wrap": True,
                            },
                            {
                                "type": "button",
                                "style": "primary",
                                "height": "sm",
                                "color": "#5ecf5f",
                                "action": {
                                    "type": "postback",
                                    "label": INVESTIGATOR_CARD_BUTTON,
                                    "data": INVESTIGATOR_CONSULT_POSTBACK,
                                    "displayText": INVESTIGATOR_CARD_BUTTON,
                                },
                            },
                        ],
                    },
                ],
            },
        },
    }


def _case_id(case: dict[str, Any] | None) -> str | None:
    if not case:
        return None
    value = case.get("id")
    return value if isinstance(value, str) else None


def _case_code(case: dict[str, Any] | None) -> str | None:
    if not case:
        return None
    value = case.get("case_code")
    return value if isinstance(value, str) else None


def _with_case_code(url: str, case_code: str | None) -> str:
    if not case_code:
        return url
    delimiter = "&" if "?" in url else "?"
    return f"{url}{delimiter}case_code={case_code}"


def _new_case_code() -> str:
    date_part = datetime.now(UTC).strftime("%Y%m%d")
    random_part = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    return f"K{date_part}-{random_part}"
