import base64
import hashlib
import hmac


def verify_line_signature(body: bytes, channel_secret: str, signature: str) -> bool:
    if not channel_secret or not signature:
        return False

    digest = hmac.new(
        channel_secret.encode("utf-8"),
        body,
        hashlib.sha256,
    ).digest()
    expected = base64.b64encode(digest).decode("utf-8")
    return hmac.compare_digest(expected, signature)

