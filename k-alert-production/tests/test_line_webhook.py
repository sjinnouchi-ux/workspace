import base64
import hashlib
import hmac

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


def _signature(body: bytes, secret: str) -> str:
    return base64.b64encode(
        hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")


def test_line_webhook_accepts_signed_payload(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LINE_CHANNEL_SECRET", "test-secret")
    body = b'{"events":[{"type":"message","webhookEventId":"event-1"}]}'

    client = TestClient(app)
    response = client.post(
        "/webhooks/line",
        content=body,
        headers={
            "Content-Type": "application/json",
            "X-Line-Signature": _signature(body, "test-secret"),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "handled": True,
        "event_count": 1,
        "duplicate_count": 0,
        "reply_count": 0,
    }
    get_settings.cache_clear()


def test_line_webhook_rejects_bad_signature(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LINE_CHANNEL_SECRET", "test-secret")

    client = TestClient(app)
    response = client.post(
        "/webhooks/line",
        content=b'{"events":[]}',
        headers={"X-Line-Signature": "bad-signature"},
    )

    assert response.status_code == 401
    get_settings.cache_clear()


def test_line_webhook_allows_unsigned_local_payload(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.delenv("LINE_CHANNEL_SECRET", raising=False)

    client = TestClient(app)
    response = client.post("/webhooks/line", json={"events": []})

    assert response.status_code == 200
    assert response.json()["event_count"] == 0
    get_settings.cache_clear()
