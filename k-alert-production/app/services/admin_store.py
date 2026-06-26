from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from app.core.supabase import SupabaseRestClient

REPORT_SUBMISSION_STATUS_LABELS = {
    "unsubmitted": "未提出",
    "submitted": "提出済",
}

AI_RESPONSE_MESSAGE_TYPE_LABELS = {
    "ai_empathy": "同調返信",
    "ai_route_decision": "分岐案内",
    "emergency_recommendation": "緊急案内",
    "emergency_route_decision": "緊急案内・分岐",
    "consult_start": "相談開始",
    "consult_end": "相談終了",
    "report_link": "通報フォーム案内",
    "investigator_consult_confirm_card": "調査官依頼確認",
    "investigator_consult_confirmed": "調査官依頼受付",
}

SENDER_LABELS = {
    "user": "ユーザー",
    "ai": "AI",
    "investigator": "調査官",
    "system": "システム",
}


@dataclass(frozen=True)
class AdminStore:
    client: SupabaseRestClient

    async def list_cases(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        filters: dict[str, str] = {"deleted_at": "is.null"}
        if status:
            filters["status"] = f"eq.{status}"
        return await self.client.select(
            "cases",
            select=(
                "id,case_code,route_type,status,urgency,category,ai_summary,"
                "created_at,updated_at,completed_at"
            ),
            filters=filters,
            order="created_at.desc",
            limit=limit,
        )

    async def get_case(self, *, case_id: str) -> dict[str, Any] | None:
        rows = await self.client.select_by_eq(
            "cases",
            "id",
            case_id,
            select=(
                "id,case_code,route_type,status,urgency,category,ai_summary,"
                "created_at,updated_at,completed_at"
            ),
            limit=1,
        )
        if not rows:
            return None
        case = rows[0]
        case["messages"] = await self.client.select(
            "messages",
            select="id,sender_type,channel,body,message_type,created_at",
            filters={"case_id": f"eq.{case_id}"},
            order="created_at.asc",
            limit=500,
        )
        case["chatwork_notifications"] = await self.client.select(
            "chatwork_notifications",
            select="id,room_id,status,error_message,sent_at,created_at",
            filters={"case_id": f"eq.{case_id}"},
            order="created_at.asc",
            limit=100,
        )
        return case

    async def list_ai_response_rules(
        self,
        *,
        limit: int = 100,
        active: bool | None = None,
    ) -> list[dict[str, Any]]:
        filters: dict[str, str] = {}
        if active is not None:
            filters["active"] = f"eq.{str(active).lower()}"
        return await self.client.select(
            "ai_response_rules",
            select=(
                "id,title,trigger_type,trigger_text,instruction,priority,active,"
                "approved_by,approved_at,created_at,updated_at"
            ),
            filters=filters,
            order="priority.asc,created_at.desc",
            limit=limit,
        )

    async def create_ai_response_rule(
        self,
        *,
        title: str,
        trigger_type: str,
        instruction: str,
        trigger_text: str | None = None,
        priority: int = 100,
        active: bool = False,
    ) -> dict[str, Any]:
        rows = await self.client.insert(
            "ai_response_rules",
            {
                "title": title,
                "trigger_type": trigger_type,
                "trigger_text": trigger_text,
                "instruction": instruction,
                "priority": priority,
                "active": active,
            },
        )
        return rows[0] if rows else {}

    async def export_reports_for_sheet(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        company_name: str = "全社",
        status: str = "すべて",
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        filters: dict[str, str] = {
            "report_type": "eq.anonymous_report",
            "deleted_at": "is.null",
        }
        if start_date:
            filters["submitted_at"] = f"gte.{start_date.isoformat()}"
        if end_date:
            filters["submitted_at"] = f"lt.{(end_date + timedelta(days=1)).isoformat()}"

        reports = await self.client.select(
            "reports",
            select=(
                "id,case_id,status,body,submission_status,"
                "submitted_to_company_at,submitted_at,created_at,updated_at"
            ),
            filters=filters,
            order="submitted_at.desc",
            limit=limit,
        )

        rows: list[dict[str, Any]] = []
        for report in reports:
            case = await self._get_export_case(case_id=str(report["case_id"]))
            if not case:
                continue
            body = _parse_report_body(report.get("body"))
            submission_status_label = REPORT_SUBMISSION_STATUS_LABELS.get(
                str(report.get("submission_status") or "unsubmitted"),
                "未提出",
            )
            if company_name != "全社" and body.get("company_name") != company_name:
                continue
            if status != "すべて" and submission_status_label != status:
                continue

            line_user = await self._get_line_user(line_user_id=str(case.get("line_user_id") or ""))
            submitted_or_created = report.get("submitted_at") or report.get("created_at")
            rows.append(
                {
                    "提出状態": submission_status_label,
                    "受付日時": _compact_datetime(submitted_or_created),
                    "case_code": case.get("case_code") or "",
                    "企業名": body.get("company_name") or "",
                    "名前": body.get("reporter_name") or "匿名",
                    "いつ": body.get("when_text") or "",
                    "どこで": body.get("where_text") or "",
                    "誰が": body.get("who_text") or "",
                    "誰に": body.get("to_whom_text") or "",
                    "内容要約": body.get("what_how_text") or "",
                    "相談希望": body.get("consultation_request") or "",
                    "LINE userId": line_user.get("line_user_id") or "",
                    "report_id": report.get("id") or "",
                    "case_id": case.get("id") or "",
                    "提出日時": report.get("submitted_at") or "",
                    "更新日時": report.get("updated_at") or "",
                    "メモ": body.get("free_text") or "",
                    "内部フラグ": "demo" if body.get("demo") else "",
                }
            )
        return rows

    async def export_report_company_candidates(self, *, limit: int = 500) -> list[str]:
        rows = await self.export_reports_for_sheet(limit=limit)
        companies = sorted({str(row.get("企業名") or "") for row in rows if row.get("企業名")})
        return ["全社", *companies]

    async def export_ai_responses_for_sheet(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        filters: dict[str, str] = {
            "sender_type": "eq.ai",
            "channel": "eq.line",
        }
        if start_date:
            filters["created_at"] = f"gte.{start_date.isoformat()}"
        if end_date:
            filters["created_at"] = f"lt.{(end_date + timedelta(days=1)).isoformat()}"

        messages = await self.client.select(
            "messages",
            select="id,case_id,webhook_event_id,body,message_type,raw_payload,created_at",
            filters=filters,
            order="created_at.desc",
            limit=limit,
        )

        rows: list[dict[str, Any]] = []
        for message in messages:
            case = await self._get_export_case(case_id=str(message.get("case_id") or "")) or {}
            line_user = await self._get_line_user(line_user_id=str(case.get("line_user_id") or ""))
            raw_payload = _as_dict(message.get("raw_payload"))
            message_type = str(raw_payload.get("message_type") or message.get("message_type") or "")
            rows.append(
                {
                    "ユーザー名": line_user.get("display_name") or "",
                    "応答日時": _compact_datetime(message.get("created_at")),
                    "case_code": case.get("case_code") or "",
                    "ユーザー発言": await self._get_user_message_body(
                        webhook_event_id=str(message.get("webhook_event_id") or "")
                    ),
                    "AI応答": message.get("body") or "",
                    "応答種別": AI_RESPONSE_MESSAGE_TYPE_LABELS.get(message_type, message_type),
                    "LINE userId": line_user.get("line_user_id") or "",
                    "message_id": message.get("id") or "",
                    "case_id": message.get("case_id") or "",
                    "raw_type": message_type,
                }
            )
        return rows

    async def export_ai_chat_summaries_for_sheet(
        self,
        *,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 500,
    ) -> list[dict[str, Any]]:
        filters: dict[str, str] = {"deleted_at": "is.null"}
        if start_date:
            filters["created_at"] = f"gte.{start_date.isoformat()}"
        if end_date:
            filters["created_at"] = f"lt.{(end_date + timedelta(days=1)).isoformat()}"

        cases = await self.client.select(
            "cases",
            select=(
                "id,case_code,status,route_type,urgency,line_user_id,"
                "created_at,updated_at,completed_at"
            ),
            filters=filters,
            order="created_at.desc",
            limit=limit,
        )

        rows: list[dict[str, Any]] = []
        for case in cases:
            case_id = str(case.get("id") or "")
            messages = await self.client.select(
                "messages",
                select="id,sender_type,body,message_type,raw_payload,created_at",
                filters={"case_id": f"eq.{case_id}"},
                order="created_at.asc",
                limit=1000,
            )
            if not messages:
                continue

            line_user = await self._get_line_user(line_user_id=str(case.get("line_user_id") or ""))
            reports = await self.client.select(
                "reports",
                select="id,body,report_type,status,submitted_at,created_at",
                filters={"case_id": f"eq.{case_id}", "deleted_at": "is.null"},
                order="created_at.desc",
                limit=5,
            )
            end_type = _chat_end_type(case=case, messages=messages, reports=reports)
            user_count = sum(1 for message in messages if message.get("sender_type") == "user")
            ai_count = sum(1 for message in messages if message.get("sender_type") == "ai")
            started_at = messages[0].get("created_at") or case.get("created_at")
            last_at = messages[-1].get("created_at") or case.get("updated_at")
            rows.append(
                {
                    "ユーザー名": line_user.get("display_name") or "",
                    "LINE userId": line_user.get("line_user_id") or "",
                    "case_code": case.get("case_code") or "",
                    "開始日時": _compact_datetime(started_at),
                    "最終日時": _compact_datetime(last_at),
                    "終了区分": end_type,
                    "ルート": _route_type_label(str(case.get("route_type") or "")),
                    "ユーザー発言数": user_count,
                    "AI応答数": ai_count,
                    "会話ログ": _format_conversation_log(messages),
                    "case_id": case_id,
                }
            )
        return rows

    async def _get_export_case(self, *, case_id: str) -> dict[str, Any] | None:
        if not case_id:
            return {}
        rows = await self.client.select_by_eq(
            "cases",
            "id",
            case_id,
            select="id,case_code,status,route_type,urgency,line_user_id,created_at,updated_at",
            limit=1,
        )
        return rows[0] if rows else None

    async def _get_line_user(self, *, line_user_id: str) -> dict[str, Any]:
        if not line_user_id:
            return {}
        rows = await self.client.select_by_eq(
            "line_users",
            "id",
            line_user_id,
            select="id,line_user_id,display_name",
            limit=1,
        )
        return rows[0] if rows else {}

    async def _get_user_message_body(self, *, webhook_event_id: str) -> str:
        if not webhook_event_id:
            return ""
        rows = await self.client.select(
            "messages",
            select="body",
            filters={
                "webhook_event_id": f"eq.{webhook_event_id}",
                "sender_type": "eq.user",
            },
            limit=1,
        )
        if not rows:
            return ""
        return str(rows[0].get("body") or "")


def _parse_report_body(raw_body: Any) -> dict[str, Any]:
    parsed = _as_dict(raw_body)
    if parsed:
        return parsed
    if not raw_body:
        return {}
    try:
        parsed = json.loads(str(raw_body))
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _compact_datetime(value: Any) -> str:
    text = str(value or "")
    return text[:16].replace("T", " ")


def _route_type_label(value: str) -> str:
    return {
        "undecided": "未分岐",
        "anonymous_report": "匿名報告",
        "investigator_consultation": "調査官相談",
    }.get(value, value)


def _chat_end_type(
    *,
    case: dict[str, Any],
    messages: list[dict[str, Any]],
    reports: list[dict[str, Any]],
) -> str:
    if any(_message_raw_type(message) == "consult_end" for message in messages):
        return "相談終了"
    if reports:
        return "通報完了"
    if case.get("status") in {"completed", "closed"}:
        return "相談終了"
    return "途中中断"


def _message_raw_type(message: dict[str, Any]) -> str:
    raw_payload = _as_dict(message.get("raw_payload"))
    return str(raw_payload.get("message_type") or message.get("message_type") or "")


def _format_conversation_log(messages: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for message in messages:
        body = str(message.get("body") or "").strip()
        if not body:
            continue
        sender = SENDER_LABELS.get(str(message.get("sender_type") or ""), "不明")
        lines.append(f"{sender}: {body}")
    return "\n".join(lines)
