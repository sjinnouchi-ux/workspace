"""Contract checks for the Codex-mediated Shogun Ops policy."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
STARTUP = ROOT / "codex" / "CODEX_DESKTOP_STARTUP.md"
CUSTOM = ROOT / "codex" / "CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md"
BEGIN = "<!-- BEGIN CODEX_SHOGUN_OPS_V1 -->"
END = "<!-- END CODEX_SHOGUN_OPS_V1 -->"
OPS = "/home/jinnouchi/.local/libexec/shogun-codex-ops"
VECTORS = (
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} status",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} start",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} restart-agent <allowlisted-agent>",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} restart-all",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} deliver",
)


def versioned_block(text: str) -> str:
    _, found, remainder = text.partition(BEGIN)
    if not found:
        return ""
    return " ".join(remainder.partition(END)[0].split())


def pasteable_block(text: str) -> str:
    _, found, remainder = text.partition("## Paste This Text\n\n```text\n")
    if not found:
        return ""
    return remainder.rpartition("\n```")[0]


class ShogunOpsDocumentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.startup = STARTUP.read_text(encoding="utf-8")
        cls.custom = CUSTOM.read_text(encoding="utf-8")
        cls.startup_ops = versioned_block(cls.startup)
        cls.custom_ops = versioned_block(cls.custom)

    def test_ops_marker_pair_exists_once_in_each_required_document(self) -> None:
        self.assertEqual(self.startup.count(BEGIN), 1)
        self.assertEqual(self.startup.count(END), 1)
        self.assertEqual(self.custom.count(BEGIN), 1)
        self.assertEqual(self.custom.count(END), 1)
        self.assertIn(BEGIN, pasteable_block(self.custom))
        self.assertIn(END, pasteable_block(self.custom))

    def test_all_exact_ops_vectors_are_documented(self) -> None:
        for vector in VECTORS:
            self.assertIn(vector, self.startup_ops)
            self.assertIn(vector, self.custom_ops)

    def test_broader_prefixes_remain_forbidden(self) -> None:
        for phrase in (
            "shorter `wsl.exe`",
            "`bash -lc`",
            "Python",
            "repo script",
            "arbitrary path",
            "suffix",
            "environment prefix",
        ):
            self.assertIn(phrase, self.startup_ops)

    def test_deployment_precondition_and_no_per_call_lookup_are_required(self) -> None:
        for phrase in (
            "one-time deployment checkpoint",
            "reviewed GitHub `main` source",
            "clean runtime repo at the reviewed commit",
            "fixed repo venv/PyYAML dependency",
            "user-owned regular mode-`0555` snapshot",
            "matching host policy",
            "no per-call GitHub registry or source-hash lookup",
        ):
            self.assertIn(phrase, self.startup_ops)

    def test_operational_authorizations_are_bounded(self) -> None:
        for phrase in (
            "`status` is routine read-only monitoring",
            "`start` may run once without a new approval",
            "sanitized status is `stopped`",
            "no active task exists",
            "exactly one allowlisted stalled agent",
            "`restart-all` always requires explicit user approval",
        ):
            self.assertIn(phrase, self.startup_ops)

    def test_delivery_keeps_intake_and_sanitized_boundary(self) -> None:
        for phrase in (
            "`CODEX_SHOGUN_TASK_INTAKE_V1`",
            "sanitized status is `healthy`",
            "exact bounded validated UTF-8 JSON document on stdin",
            "idempotency key",
            "only the sanitized fixed JSON contract",
            "must not read or display raw queue/report/log/pane content",
            "task bodies from runtime state",
            "personal identifiers",
        ):
            self.assertIn(phrase, self.startup_ops)

    def test_failure_boundary_and_test_scope_are_explicit(self) -> None:
        for phrase in (
            "Unknown/degraded state",
            "multiple stalled agents",
            "failed/ambiguous task state",
            "without raw fallback or automatic repair",
            "focused contract tests plus a real-task canary",
            "Full-suite work is reserved for core orchestration",
            "Rollback removes the exact host/Workspace exception",
            "without deleting existing runtime task records",
        ):
            self.assertIn(phrase, self.startup_ops)


if __name__ == "__main__":
    unittest.main()
