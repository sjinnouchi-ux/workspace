import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock
from urllib.error import URLError
from zoneinfo import ZoneInfo

from codex.hooks import codex_turn_line_notify as notifier


class FakeResponse:
    def __init__(self, body):
        self._body = body
        self.read_sizes = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, size=-1):
        self.read_sizes.append(size)
        return self._body[:size]


class ReadHookEventTests(unittest.TestCase):
    def test_reads_bounded_json_object(self):
        stream = io.BytesIO(
            json.dumps(
                {
                    "hook_event_name": "Stop",
                    "session_id": "session-secret",
                    "turn_id": "turn-secret",
                }
            ).encode("utf-8")
        )

        event = notifier.read_hook_event(stream)

        self.assertEqual(event["hook_event_name"], "Stop")

    def test_rejects_input_larger_than_65536_bytes(self):
        stream = io.BytesIO(b" " * 65_537)

        with self.assertRaisesRegex(ValueError, "too large"):
            notifier.read_hook_event(stream)

    def test_rejects_non_object_json(self):
        with self.assertRaisesRegex(ValueError, "object"):
            notifier.read_hook_event(io.BytesIO(b"[]"))


class BuildPayloadTests(unittest.TestCase):
    def setUp(self):
        self.event = {
            "hook_event_name": "Stop",
            "session_id": "session-secret",
            "turn_id": "turn-secret",
            "cwd": "C:/secret",
            "transcript_path": "C:/private/transcript.jsonl",
            "model": "private-model",
            "permission_mode": "private-mode",
        }
        self.now = datetime(2026, 7, 17, 14, 32, tzinfo=ZoneInfo("Asia/Tokyo"))

    def test_builds_exact_privacy_preserving_payload(self):
        payload = notifier.build_payload(self.event, self.now, "NUCBOX_K8_PLUS")

        self.assertEqual(
            payload,
            {
                "schema_version": 1,
                "event_id": hashlib.sha256(
                    b"session-secret:turn-secret"
                ).hexdigest(),
                "ended_at": "2026-07-17T14:32:00+09:00",
                "host_label": "NUCBOX_K8_PLUS",
            },
        )
        serialized = json.dumps(payload)
        for secret in (
            "session-secret",
            "turn-secret",
            "C:/secret",
            "C:/private/transcript.jsonl",
            "private-model",
            "private-mode",
        ):
            self.assertNotIn(secret, serialized)

    def test_event_id_is_deterministic_sha256(self):
        first = notifier.build_payload(self.event, self.now, "NUCBOX_K8_PLUS")
        second = notifier.build_payload(self.event, self.now, "NUCBOX_K8_PLUS")

        self.assertEqual(first["event_id"], second["event_id"])
        self.assertEqual(len(first["event_id"]), 64)

    def test_converts_timestamp_to_jst_with_second_precision(self):
        utc_now = datetime(2026, 7, 17, 5, 32, 59, 987654, tzinfo=timezone.utc)

        payload = notifier.build_payload(self.event, utc_now, "NUCBOX_K8_PLUS")

        self.assertEqual(payload["ended_at"], "2026-07-17T14:32:59+09:00")

    def test_rejects_non_stop_event(self):
        self.event["hook_event_name"] = "SubagentStop"

        with self.assertRaisesRegex(ValueError, "unsupported hook event"):
            notifier.build_payload(self.event, self.now, "NUCBOX_K8_PLUS")

    def test_rejects_missing_empty_and_non_string_ids(self):
        for field in ("session_id", "turn_id"):
            for value in (None, "", 123):
                with self.subTest(field=field, value=value):
                    event = dict(self.event)
                    if value is None:
                        event.pop(field)
                    else:
                        event[field] = value
                    with self.assertRaisesRegex(ValueError, f"missing {field}"):
                        notifier.build_payload(event, self.now, "NUCBOX_K8_PLUS")

    def test_rejects_invalid_host_labels(self):
        for host_label in (None, "", "bad host", "x" * 65, "-leading"):
            with self.subTest(host_label=host_label):
                with self.assertRaisesRegex(ValueError, "invalid host label"):
                    notifier.build_payload(self.event, self.now, host_label)


class MintIdTokenTests(unittest.TestCase):
    @mock.patch("codex.hooks.codex_turn_line_notify.subprocess.run")
    def test_mints_with_exact_argv_and_five_second_timeout(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, stdout="id-token\n")

        token = notifier.mint_id_token(
            "C:/GoogleCloudSDK/gcloud.cmd",
            "codex-turn-notifier@example.iam.gserviceaccount.com",
            "https://service.example",
        )

        self.assertEqual(token, "id-token")
        run.assert_called_once_with(
            [
                "C:/GoogleCloudSDK/gcloud.cmd",
                "auth",
                "print-identity-token",
                "--impersonate-service-account=codex-turn-notifier@example.iam.gserviceaccount.com",
                "--audiences=https://service.example",
                "--include-email",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

    @mock.patch("codex.hooks.codex_turn_line_notify.subprocess.run")
    def test_rejects_empty_token(self, run):
        run.return_value = subprocess.CompletedProcess([], 0, stdout=" \n")

        with self.assertRaisesRegex(ValueError, "empty identity token"):
            notifier.mint_id_token("gcloud", "notifier@example.com", "https://example")

    @unittest.skipUnless(os.name == "nt", "Windows command-wrapper integration")
    def test_mints_through_a_real_cmd_wrapper(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            wrapper = Path(temp_dir) / "gcloud.cmd"
            wrapper.write_text("@echo synthetic-id-token\n", encoding="ascii")

            token = notifier.mint_id_token(
                str(wrapper),
                "codex-turn-notifier@example.iam.gserviceaccount.com",
                "https://service.example",
            )

        self.assertEqual(token, "synthetic-id-token")


class PostNotificationTests(unittest.TestCase):
    @mock.patch("codex.hooks.codex_turn_line_notify.request.urlopen")
    def test_posts_json_with_bearer_and_thirty_second_timeout(self, urlopen):
        response = FakeResponse(b'{"status":"sent"}')
        urlopen.return_value = response
        payload = {
            "schema_version": 1,
            "event_id": "a" * 64,
            "ended_at": "2026-07-17T14:32:00+09:00",
            "host_label": "NUCBOX_K8_PLUS",
        }

        result = notifier.post_notification(
            "https://service.example/internal/codex/turn-ended/notify",
            "secret-token",
            payload,
        )

        self.assertEqual(result, "sent")
        request_arg = urlopen.call_args.args[0]
        self.assertEqual(request_arg.full_url, "https://service.example/internal/codex/turn-ended/notify")
        self.assertEqual(request_arg.get_method(), "POST")
        self.assertEqual(request_arg.headers["Authorization"], "Bearer secret-token")
        self.assertEqual(request_arg.headers["Content-type"], "application/json")
        self.assertEqual(json.loads(request_arg.data), payload)
        self.assertEqual(urlopen.call_args.kwargs, {"timeout": 30})
        self.assertEqual(response.read_sizes, [4_097])

    @mock.patch("codex.hooks.codex_turn_line_notify.request.urlopen")
    def test_returns_only_supported_server_statuses(self, urlopen):
        for status in ("sent", "deduplicated", "no_subscribers"):
            with self.subTest(status=status):
                urlopen.return_value = FakeResponse(
                    json.dumps({"status": status, "private": "ignored"}).encode("utf-8")
                )
                self.assertEqual(
                    notifier.post_notification("https://example", "token", {}), status
                )

    @mock.patch("codex.hooks.codex_turn_line_notify.request.urlopen")
    def test_rejects_response_larger_than_4096_bytes(self, urlopen):
        urlopen.return_value = FakeResponse(b"{" + b" " * 4_096)

        with self.assertRaisesRegex(ValueError, "too large"):
            notifier.post_notification("https://example", "token", {})

    @mock.patch("codex.hooks.codex_turn_line_notify.request.urlopen")
    def test_rejects_unknown_status_without_returning_body(self, urlopen):
        urlopen.return_value = FakeResponse(b'{"status":"private-server-detail"}')

        with self.assertRaisesRegex(ValueError, "unexpected notification status") as caught:
            notifier.post_notification("https://example", "token", {})

        self.assertNotIn("private-server-detail", str(caught.exception))


class MainTests(unittest.TestCase):
    def argv(self, log_path):
        return [
            "--endpoint",
            "https://service.example/internal/codex/turn-ended/notify",
            "--audience",
            "https://service.example",
            "--service-account",
            "codex-turn-notifier@example.iam.gserviceaccount.com",
            "--host-label",
            "NUCBOX_K8_PLUS",
            "--gcloud",
            "C:/GoogleCloudSDK/gcloud.cmd",
            "--log-path",
            str(log_path),
        ]

    @mock.patch("codex.hooks.codex_turn_line_notify.post_notification", return_value="sent")
    @mock.patch("codex.hooks.codex_turn_line_notify.mint_id_token", return_value="secret-token")
    def test_success_returns_zero_and_logs_only_timestamp_and_status(self, mint, post):
        raw_event = (
            b'{"hook_event_name":"Stop","session_id":"session-secret",'
            b'"turn_id":"turn-secret","cwd":"C:/private"}'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "notify.log"

            result = notifier.main(self.argv(log_path), stdin=io.BytesIO(raw_event))

            self.assertEqual(result, 0)
            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("status=sent", log_text)
            for private in ("session-secret", "turn-secret", "C:/private", "secret-token"):
                self.assertNotIn(private, log_text)
            self.assertNotIn("response", log_text.lower())

    def test_operational_failures_return_zero_and_log_only_error_class(self):
        raw_event = (
            b'{"hook_event_name":"Stop","session_id":"session-secret",'
            b'"turn_id":"turn-secret"}'
        )
        failures = (
            subprocess.TimeoutExpired("gcloud secret args", 5, output="secret-output"),
            URLError("private-url-detail"),
            OSError("private-os-detail"),
            ValueError("private-validation-detail"),
        )
        for failure in failures:
            with self.subTest(failure=type(failure).__name__):
                with tempfile.TemporaryDirectory() as temp_dir:
                    log_path = Path(temp_dir) / "notify.log"
                    with mock.patch(
                        "codex.hooks.codex_turn_line_notify.mint_id_token",
                        side_effect=failure,
                    ):
                        result = notifier.main(
                            self.argv(log_path), stdin=io.BytesIO(raw_event)
                        )

                    self.assertEqual(result, 0)
                    log_text = log_path.read_text(encoding="utf-8")
                    self.assertIn(f"error={type(failure).__name__}", log_text)
                    for private in (
                        "session-secret",
                        "turn-secret",
                        "secret-output",
                        "private-url-detail",
                        "private-os-detail",
                        "private-validation-detail",
                    ):
                        self.assertNotIn(private, log_text)

    def test_log_write_failure_also_returns_zero(self):
        with mock.patch(
            "codex.hooks.codex_turn_line_notify.read_hook_event",
            side_effect=ValueError("invalid"),
        ), mock.patch(
            "codex.hooks.codex_turn_line_notify._write_log",
            side_effect=OSError("disk error"),
        ):
            result = notifier.main(
                self.argv("Z:/unavailable/notify.log"), stdin=io.BytesIO(b"{}")
            )

        self.assertEqual(result, 0)


if __name__ == "__main__":
    unittest.main()
