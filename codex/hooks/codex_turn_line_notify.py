"""Fail-open Codex Stop-hook notifier for the kakeibo LINE endpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Sequence, TextIO
from urllib import request
from zoneinfo import ZoneInfo


MAX_STDIN_BYTES = 65_536
MAX_RESPONSE_BYTES = 4_096
TOKEN_TIMEOUT_SECONDS = 5
HTTP_TIMEOUT_SECONDS = 15
JST = ZoneInfo("Asia/Tokyo")
HOST_LABEL_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}\Z")
SUPPORTED_STATUSES = frozenset({"sent", "deduplicated", "no_subscribers"})


def read_hook_event(stream: BinaryIO | TextIO) -> dict[str, object]:
    """Read one bounded JSON object from the hook's standard input."""
    raw = stream.read(MAX_STDIN_BYTES + 1)
    if isinstance(raw, str):
        raw_bytes = raw.encode("utf-8")
    else:
        raw_bytes = raw
    if len(raw_bytes) > MAX_STDIN_BYTES:
        raise ValueError("hook input too large")
    event = json.loads(raw_bytes.decode("utf-8"))
    if not isinstance(event, dict):
        raise ValueError("hook input must be a JSON object")
    return event


def build_payload(
    event: dict[str, object], now: datetime, host_label: str
) -> dict[str, object]:
    """Build the minimal notification payload without retaining raw identifiers."""
    if event.get("hook_event_name") != "Stop":
        raise ValueError("unsupported hook event")
    session_id = event.get("session_id")
    turn_id = event.get("turn_id")
    if not isinstance(session_id, str) or not session_id:
        raise ValueError("missing session_id")
    if not isinstance(turn_id, str) or not turn_id:
        raise ValueError("missing turn_id")
    if not isinstance(host_label, str) or not HOST_LABEL_PATTERN.fullmatch(host_label):
        raise ValueError("invalid host label")

    event_id = hashlib.sha256(f"{session_id}:{turn_id}".encode("utf-8")).hexdigest()
    return {
        "schema_version": 1,
        "event_id": event_id,
        "ended_at": now.astimezone(JST).isoformat(timespec="seconds"),
        "host_label": host_label,
    }


def mint_id_token(gcloud: str, service_account: str, audience: str) -> str:
    """Mint an OIDC identity token through service-account impersonation."""
    completed = subprocess.run(
        [
            gcloud,
            "auth",
            "print-identity-token",
            f"--impersonate-service-account={service_account}",
            f"--audiences={audience}",
            "--include-email",
            "--quiet",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=TOKEN_TIMEOUT_SECONDS,
    )
    token = completed.stdout.strip()
    if not token:
        raise ValueError("empty identity token")
    return token


def post_notification(endpoint: str, token: str, payload: dict[str, object]) -> str:
    """POST a notification and return only its allowlisted status."""
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    http_request = request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(http_request, timeout=HTTP_TIMEOUT_SECONDS) as response:
        response_body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(response_body) > MAX_RESPONSE_BYTES:
        raise ValueError("notification response too large")
    decoded = json.loads(response_body.decode("utf-8"))
    status = decoded.get("status") if isinstance(decoded, dict) else None
    if status not in SUPPORTED_STATUSES:
        raise ValueError("unexpected notification status")
    return status


def _write_log(log_path: str | Path, *, status: str | None = None, error: str | None = None) -> None:
    timestamp = datetime.now(JST).isoformat(timespec="seconds")
    outcome = f"status={status}" if status is not None else f"error={error}"
    with Path(log_path).open("a", encoding="utf-8") as log_file:
        log_file.write(f"timestamp={timestamp} {outcome}\n")


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", required=True)
    parser.add_argument("--audience", required=True)
    parser.add_argument("--service-account", required=True)
    parser.add_argument("--host-label", required=True)
    parser.add_argument("--gcloud", required=True)
    parser.add_argument("--log-path", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None, *, stdin: BinaryIO | TextIO | None = None) -> int:
    """Run the notification flow and always fail open after argument parsing."""
    args = _parse_args(argv)
    source = stdin if stdin is not None else sys.stdin.buffer
    try:
        event = read_hook_event(source)
        payload = build_payload(event, datetime.now(JST), args.host_label)
        token = mint_id_token(args.gcloud, args.service_account, args.audience)
        status = post_notification(args.endpoint, token, payload)
        _write_log(args.log_path, status=status)
    except Exception as exc:
        try:
            _write_log(args.log_path, error=type(exc).__name__)
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
