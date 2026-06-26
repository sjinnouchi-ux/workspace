from fastapi.testclient import TestClient

from app.api.routes import liff_report
from app.core.config import get_settings
from app.main import app


class FakeLiffReportStore:
    async def submit_report(self, report):
        return {
            "case_id": "case-uuid",
            "case_code": report.case_code,
            "report_id": "report-uuid",
            "status": "completed",
        }


def _override_store() -> FakeLiffReportStore:
    return FakeLiffReportStore()


def test_liff_report_requires_api_key(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LIFF_REPORT_API_KEY", "secret")
    app.dependency_overrides[liff_report.get_liff_report_store] = _override_store

    client = TestClient(app)
    response = client.post("/liff/report", json={})

    assert response.status_code == 401
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_liff_report_submits_report(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LIFF_REPORT_API_KEY", "secret")
    app.dependency_overrides[liff_report.get_liff_report_store] = _override_store

    client = TestClient(app)
    response = client.post(
        "/liff/report",
        headers={"X-Liff-Report-Api-Key": "secret"},
        json={
            "case_code": "K20260626-ABC123",
            "company_name": "テスト企業",
            "reporter_name": "",
            "when_text": "今日",
            "where_text": "事務所",
            "who_text": "上司",
            "to_whom_text": "私",
            "what_how_text": "他の人の前で大声で強く叱責された",
            "free_text": "",
            "consultation_request": "希望しない",
        },
    )

    assert response.status_code == 200
    assert response.json()["report_id"] == "report-uuid"
    app.dependency_overrides.clear()
    get_settings.cache_clear()
