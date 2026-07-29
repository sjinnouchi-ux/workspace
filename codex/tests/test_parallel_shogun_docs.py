"""Contract checks for the Native Windows parallel Shogun boundary."""

from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
STARTUP = ROOT / "codex" / "CODEX_DESKTOP_STARTUP.md"
BEGIN = "<!-- BEGIN CODEX_PARALLEL_SHOGUN_V1 -->"
END = "<!-- END CODEX_PARALLEL_SHOGUN_V1 -->"
EXECUTABLE = r"C:\ProgramData\Shogun\bin\shogun-parallel.exe"
OPERATIONS = ("status", "launch", "review", "cancel")
VECTORS = tuple(f"{EXECUTABLE} {operation}" for operation in OPERATIONS)
OUTPUT_KEYS = (
    "schema_version",
    "overall",
    "stale",
    "task_id",
    "active_shogun",
    "workers",
    "review",
    "recommendation",
)
REQUEST_REGISTRY = (
    "status = schema_version,task_id",
    "launch = schema_version,approval",
    "launch.approval = task_id,idempotency_key,manifest_digest",
    "review = schema_version,task_id,caller",
    "cancel = schema_version,task_id,worker_id,approved",
)
PROJECTION_REGISTRY = (
    "output = " + ",".join(OUTPUT_KEYS),
    "worker = worker_id,state",
    "review = null|state",
    "worker.state = "
    "queued|starting|running|attention_required|blocked|failed|completed|cancelled",
    "review.state = "
    "pending|running|approved|changes_required|rejected|blocked|failed",
    "recommendation = "
    "none|wait|inspect|retry_with_approval|review_required|user_action_required",
    "active_shogun = codex|claude",
    "overall = healthy|degraded|unknown",
)
STATUS_REGISTRY = (
    "runner_reachable=false => overall=unknown,stale=true",
    "runner_reachable=true => stale=false",
    "runner_reachable=true AND operation_failure=false AND "
    "every worker.state in {completed,cancelled} AND "
    "review in {null,approved} => overall=healthy",
    "runner_reachable=true AND previous healthy condition is false "
    "=> overall=degraded",
    "consumer: overall=unknown <=> stale=true",
    "consumer: overall=healthy => every worker.state in "
    "{completed,cancelled} AND review in {null,approved}",
    "consumer: overall=degraded => stale=false",
)
ATTESTATION_REGISTRY = (
    "claude-only = claude",
    "codex-only = codex",
    "mixed-task = separate-current-receipt-per-launch",
    "receipt.keys = exact-installed-and-required-cli-set",
    "reject = missing|extra|unknown|version-mismatch|stale-generation",
)


def versioned_block(text: str) -> str:
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        return ""
    before, remainder = text.split(BEGIN, 1)
    block, after = remainder.split(END, 1)
    if not before or not block or not after:
        return ""
    return block


def normalized(text: str) -> str:
    return " ".join(text.split())


def fenced_registry(block: str, label: str) -> tuple[str, ...]:
    marker = f"{label}\n\n```text\n"
    _, found, remainder = block.partition(marker)
    if not found:
        return ()
    payload, closing_fence, _ = remainder.partition("\n```")
    if not closing_fence:
        return ()
    return tuple(line.strip() for line in payload.splitlines() if line.strip())


class ParallelShogunDocumentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.startup = STARTUP.read_text(encoding="utf-8")
        cls.block = versioned_block(cls.startup)
        cls.content = normalized(cls.block)

    def test_exact_native_windows_vectors_are_allowlisted_in_order(self) -> None:
        self.assertEqual(self.startup.count(BEGIN), 1)
        self.assertEqual(self.startup.count(END), 1)
        self.assertEqual(
            fenced_registry(
                self.block,
                "Only these four complete Native Windows vectors are eligible:",
            ),
            VECTORS,
        )
        self.assertNotIn("shogun-parallel.cmd", self.block)
        self.assertEqual(self.block.count(EXECUTABLE), len(VECTORS))

    def test_shorter_or_alternate_execution_paths_are_forbidden(self) -> None:
        for phrase in (
            "shorter `powershell.exe`",
            "`cmd.exe`",
            "Python",
            "executable-only prefix",
            "arbitrary suffix",
            "environment override",
            "alternate path",
        ):
            self.assertIn(phrase, self.content)

    def test_deployment_checkpoint_binds_reviewed_artifact_and_host_acl(
        self,
    ) -> None:
        for phrase in (
            "inactive until a one-time deployment checkpoint",
            "reviewed GitHub `main` source",
            "clean source tree at the reviewed commit",
            "source-tree hash",
            "native artifact hash",
            "fixed absolute path",
            "expected owner",
            "explicit ACL",
            "reparse point or junction",
            "matching host policy",
        ):
            self.assertIn(phrase, self.content)

    def test_request_and_status_projection_are_closed_and_bounded(self) -> None:
        self.assertEqual(
            fenced_registry(self.block, "Request shape registry:"),
            REQUEST_REGISTRY,
        )
        self.assertEqual(
            fenced_registry(self.block, "Successful projection registry:"),
            PROJECTION_REGISTRY,
        )
        self.assertEqual(
            fenced_registry(self.block, "Status calculation registry:"),
            STATUS_REGISTRY,
        )
        for phrase in (
            "bounded strict UTF-8 JSON on stdin",
            "schema version 1",
            "64 KiB",
            "duplicate keys",
            "UTF-8 BOM",
            "ASCII-only JSON",
            "empty stderr",
            "exact key order",
            "runner unreachable",
            '`overall="unknown"`',
            "`stale=true`",
            "never reports `healthy`",
        ):
            self.assertIn(phrase, self.content)

    def test_operation_authority_is_task_scoped_and_fail_closed(self) -> None:
        for phrase in (
            "`status` is read-only",
            "`launch` requires one explicit task approval",
            "sealed manifest digest",
            "idempotency key",
            "`review` requires the original approved task",
            "active Shogun",
            "`cancel` requires explicit user approval for that exact invocation",
            "exact worker ID",
            "no per-worker, per-turn, or tool-call approval",
        ):
            self.assertIn(phrase, self.content)

    def test_cli_attestation_covers_only_the_active_cli_set(self) -> None:
        self.assertEqual(
            fenced_registry(self.block, "CLI attestation registry:"),
            ATTESTATION_REGISTRY,
        )
        for phrase in (
            "`pinned_versions_for`",
            "installed and required CLI set",
            "Claude-only launch does not require Codex",
            "Codex-only launch does not require Claude",
            "mixed task uses separate current receipts",
            "must not accept an unrelated extra CLI key",
        ):
            self.assertIn(phrase, self.content)

    def test_consumer_validates_success_and_never_uses_raw_fallback(self) -> None:
        for phrase in (
            "exit code 0",
            "independently validates",
            "schema and cross-field invariants",
            "reviewed native wrapper recomputes `overall`",
            "nonzero exit",
            "invalid or partial output",
            "nonempty stderr",
            "no raw or direct-read fallback",
        ):
            self.assertIn(phrase, self.content)

    def test_parallel_contract_does_not_weaken_legacy_ops_or_privacy(self) -> None:
        for phrase in (
            "does not replace, weaken, or reuse `CODEX_SHOGUN_OPS_V1`",
            "legacy WSL2 Shogun",
            "raw queue",
            "raw report",
            "raw log",
            "pane content",
            "credentials",
            "task bodies from runtime state",
            "personal identifiers",
        ):
            self.assertIn(phrase, self.content)


if __name__ == "__main__":
    unittest.main()
