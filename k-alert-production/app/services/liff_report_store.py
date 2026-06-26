from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from app.core.supabase import SupabaseRestClient


@dataclass(frozen=True)
class LiffReportSubmission:
    case_code: str
    company_name: str
    reporter_name: str
    when_text: str
    where_text: str
    who_text: str
    to_whom_text: str
    what_how_text: str
    free_text: str
    consultation_request: str


@dataclass(frozen=True)
class LiffReportStore:
    client: SupabaseRestClient

    async def submit_report(self, report: LiffReportSubmission) -> dict[str, Any]:
        case = await self._get_case_by_code(report.case_code)
        if not case:
            raise ValueError("case_not_found")

        case_id = str(case["id"])
        report_body = {
            "company_name": report.company_name,
            "reporter_name": report.reporter_name,
            "when_text": report.when_text,
            "where_text": report.where_text,
            "who_text": report.who_text,
            "to_whom_text": report.to_whom_text,
            "what_how_text": report.what_how_text,
            "free_text": report.free_text,
            "consultation_request": report.consultation_request,
        }
        report_rows = await self.client.insert(
            "reports",
            {
                "case_id": case_id,
                "report_type": "anonymous_report",
                "status": "submitted",
                "body": json.dumps(report_body, ensure_ascii=False),
                "submitted_at": _now_iso(),
            },
        )
        await self.client.insert(
            "ai_extractions",
            {
                "case_id": case_id,
                "when_text": report.when_text,
                "where_text": report.where_text,
                "who_text": report.who_text,
                "to_whom_text": report.to_whom_text,
                "what_text": report.what_how_text,
                "how_text": "",
                "urgency": "unknown",
                "notes": report.free_text,
                "model": "liff_form",
                "prompt_version": "manual_v1",
            },
        )
        next_status = (
            "waiting_investigator" if report.consultation_request == "希望する" else "completed"
        )
        payload: dict[str, Any] = {"route_type": "anonymous_report", "status": next_status}
        if next_status == "completed":
            payload["completed_at"] = _now_iso()
        await self.client.update_by_eq("cases", "id", case_id, payload)
        return {
            "case_id": case_id,
            "case_code": report.case_code,
            "report_id": report_rows[0]["id"] if report_rows else None,
            "status": next_status,
        }

    async def _get_case_by_code(self, case_code: str) -> dict[str, Any] | None:
        rows = await self.client.select_by_eq(
            "cases",
            "case_code",
            case_code,
            select="id,case_code,status,route_type",
            limit=1,
        )
        return rows[0] if rows else None


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()
