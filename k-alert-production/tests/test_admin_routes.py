from fastapi.testclient import TestClient

from app.api.routes import admin
from app.core.config import get_settings
from app.main import app


class FakeAdminStore:
    def __init__(self) -> None:
        self.created_rules: list[dict] = []
        self.export_args: dict | None = None

    async def list_cases(self, *, limit: int = 50, status: str | None = None) -> list[dict]:
        return [
            {
                "id": "case-uuid",
                "case_code": "K20260626-ABC123",
                "status": status or "collecting",
                "route_type": "undecided",
            }
        ]

    async def get_case(self, *, case_id: str) -> dict | None:
        if case_id != "case-uuid":
            return None
        return {
            "id": "case-uuid",
            "case_code": "K20260626-ABC123",
            "messages": [],
            "chatwork_notifications": [],
        }

    async def list_ai_response_rules(
        self,
        *,
        limit: int = 100,
        active: bool | None = None,
    ) -> list[dict]:
        return [
            {
                "id": "rule-uuid",
                "title": "緊急時案内",
                "trigger_type": "contains_text_reply",
                "trigger_text": "危険",
                "instruction": "身の安全を最優先にしてください。",
                "priority": 10,
                "active": active if active is not None else True,
            }
        ]

    async def create_ai_response_rule(
        self,
        *,
        title: str,
        trigger_type: str,
        instruction: str,
        trigger_text: str | None = None,
        priority: int = 100,
        active: bool = False,
    ) -> dict:
        rule = {
            "id": "created-rule-uuid",
            "title": title,
            "trigger_type": trigger_type,
            "trigger_text": trigger_text,
            "instruction": instruction,
            "priority": priority,
            "active": active,
        }
        self.created_rules.append(rule)
        return rule

    async def export_reports_for_sheet(
        self,
        *,
        start_date=None,
        end_date=None,
        company_name: str = "全社",
        status: str = "すべて",
        limit: int = 500,
    ) -> list[dict]:
        self.export_args = {
            "start_date": start_date,
            "end_date": end_date,
            "company_name": company_name,
            "status": status,
            "limit": limit,
        }
        return [
            {
                "受付日時": "2026-06-26 08:18",
                "case_code": "DEMO-SHEET-001",
                "企業名": "〇〇病院",
                "名前": "匿名",
                "相談希望": "希望する",
                "提出状態": "未提出",
            }
        ]

    async def export_report_company_candidates(self, *, limit: int = 500) -> list[str]:
        return ["全社", "〇〇病院", "△△介護"]

    async def export_ai_responses_for_sheet(
        self,
        *,
        start_date=None,
        end_date=None,
        limit: int = 500,
    ) -> list[dict]:
        self.export_args = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        }
        return [
            {
                "ユーザー名": "ジンノウチさん",
                "応答日時": "2026-06-26 08:20",
                "case_code": "DEMO-SHEET-001",
                "ユーザー発言": "つらいです",
                "AI応答": "話してくださってありがとうございます。",
                "応答種別": "同調返信",
                "LINE userId": "U123",
            }
        ]

    async def export_ai_chat_summaries_for_sheet(
        self,
        *,
        start_date=None,
        end_date=None,
        limit: int = 500,
    ) -> list[dict]:
        self.export_args = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
        }
        return [
            {
                "ユーザー名": "ジンノウチさん",
                "LINE userId": "U123",
                "case_code": "DEMO-SHEET-001",
                "開始日時": "2026-06-26 08:18",
                "最終日時": "2026-06-26 08:22",
                "終了区分": "途中中断",
                "ルート": "未分岐",
                "ユーザー発言数": 2,
                "AI応答数": 2,
                "会話ログ": "[2026-06-26 08:18] ユーザー: つらいです",
                "case_id": "case-uuid",
            }
        ]


def _override_store() -> FakeAdminStore:
    return FakeAdminStore()


def test_admin_cases_requires_admin_api_key(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.get("/admin/cases")

    assert response.status_code == 401
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_cases_returns_case_list(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.get("/admin/cases?status=collecting", headers={"X-Admin-Api-Key": "secret"})

    assert response.status_code == 200
    assert response.json()["cases"][0]["case_code"] == "K20260626-ABC123"
    assert response.json()["cases"][0]["status"] == "collecting"
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_case_detail_returns_messages(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.get("/admin/cases/case-uuid", headers={"X-Admin-Api-Key": "secret"})

    assert response.status_code == 200
    assert response.json()["case"]["messages"] == []
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_exports_reports_for_sheet(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    store = FakeAdminStore()
    app.dependency_overrides[admin.get_admin_store] = lambda: store

    client = TestClient(app)
    response = client.get(
        "/admin/exports/reports"
        "?start_date=2026-06-01&end_date=2026-06-26"
        "&company_name=%E3%80%87%E3%80%87%E7%97%85%E9%99%A2"
        "&status=%E6%9C%AA%E6%8F%90%E5%87%BA&limit=100",
        headers={"X-Admin-Api-Key": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["rows"][0]["case_code"] == "DEMO-SHEET-001"
    assert store.export_args is not None
    assert store.export_args["company_name"] == "〇〇病院"
    assert store.export_args["status"] == "未提出"
    assert store.export_args["limit"] == 100
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_exports_report_companies(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.get(
        "/admin/exports/report-companies",
        headers={"X-Admin-Api-Key": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["companies"] == ["全社", "〇〇病院", "△△介護"]
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_exports_ai_responses_for_sheet(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    store = FakeAdminStore()
    app.dependency_overrides[admin.get_admin_store] = lambda: store

    client = TestClient(app)
    response = client.get(
        "/admin/exports/ai-responses?start_date=2026-06-01&end_date=2026-06-26&limit=100",
        headers={"X-Admin-Api-Key": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["rows"][0]["ユーザー名"] == "ジンノウチさん"
    assert response.json()["rows"][0]["AI応答"] == "話してくださってありがとうございます。"
    assert store.export_args is not None
    assert store.export_args["limit"] == 100
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_exports_ai_chat_summaries_for_sheet(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    store = FakeAdminStore()
    app.dependency_overrides[admin.get_admin_store] = lambda: store

    client = TestClient(app)
    response = client.get(
        "/admin/exports/ai-chat-summaries?start_date=2026-06-01&end_date=2026-06-26&limit=100",
        headers={"X-Admin-Api-Key": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["rows"][0]["ユーザー名"] == "ジンノウチさん"
    assert response.json()["rows"][0]["終了区分"] == "途中中断"
    assert "ユーザー: つらいです" in response.json()["rows"][0]["会話ログ"]
    assert store.export_args is not None
    assert store.export_args["limit"] == 100
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_lists_ai_response_rules(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.get(
        "/admin/ai-response-rules?active=true",
        headers={"X-Admin-Api-Key": "secret"},
    )

    assert response.status_code == 200
    assert response.json()["rules"][0]["trigger_type"] == "contains_text_reply"
    app.dependency_overrides.clear()
    get_settings.cache_clear()


def test_admin_creates_ai_response_rule_inactive_by_default(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("ADMIN_API_KEY", "secret")
    app.dependency_overrides[admin.get_admin_store] = _override_store

    client = TestClient(app)
    response = client.post(
        "/admin/ai-response-rules",
        headers={"X-Admin-Api-Key": "secret"},
        json={
            "title": "初期案内",
            "trigger_type": "exact_text_reply",
            "trigger_text": "助けて",
            "instruction": "安全な場所に移動できる場合は、まず移動してください。",
        },
    )

    assert response.status_code == 201
    assert response.json()["rule"]["active"] is False
    app.dependency_overrides.clear()
    get_settings.cache_clear()
