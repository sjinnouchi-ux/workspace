import base64
import hashlib
import hmac

from app.services.line_signature import verify_line_signature


def test_verify_line_signature_accepts_valid_signature() -> None:
    body = b'{"events":[]}'
    secret = "test-secret"
    signature = base64.b64encode(
        hmac.new(secret.encode("utf-8"), body, hashlib.sha256).digest()
    ).decode("utf-8")

    assert verify_line_signature(body, secret, signature) is True


def test_verify_line_signature_rejects_invalid_signature() -> None:
    assert verify_line_signature(b'{"events":[]}', "test-secret", "invalid") is False

