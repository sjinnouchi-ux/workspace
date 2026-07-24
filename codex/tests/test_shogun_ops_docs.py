"""Contract checks for the Codex-mediated Shogun Ops policy."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
STARTUP = ROOT / "codex" / "CODEX_DESKTOP_STARTUP.md"
CUSTOM = ROOT / "codex" / "CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md"
OPS_BEGIN = "<!-- BEGIN CODEX_SHOGUN_OPS_V1 -->"
OPS_END = "<!-- END CODEX_SHOGUN_OPS_V1 -->"
DIAGNOSTICS_BEGIN = "<!-- BEGIN CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->"
DIAGNOSTICS_END = "<!-- END CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->"
OPS = "/home/jinnouchi/.local/libexec/shogun-codex-ops"
DIAGNOSTICS = "/home/jinnouchi/.local/libexec/shogun-codex-diagnostics"
DIAGNOSTIC_VECTOR = (
    "wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun "
    f"{DIAGNOSTICS} summary"
)
REGISTRY_URL = (
    "https://raw.githubusercontent.com/sjinnouchi-ux/multi-agent-shogun/main/"
    "docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md"
)
VECTORS = (
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} status",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} start",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} restart-agent <allowlisted-agent>",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} restart-all",
    f"wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun {OPS} deliver",
)


def versioned_block(text: str, begin: str, end: str) -> str:
    _, found, remainder = text.partition(begin)
    if not found:
        return ""
    return remainder.partition(end)[0]


def normalized(text: str) -> str:
    return " ".join(text.split())


def first_pasteable_block(text: str) -> tuple[str, bool]:
    """Return the first fenced Paste This Text block and whether it closes."""
    _, found, remainder = text.partition("## Paste This Text\n\n```text\n")
    if not found:
        return "", False
    payload, closing_fence, _ = remainder.partition("\n```")
    return payload, bool(closing_fence)


def ops_command_lines(block: str) -> list[str]:
    return [line.strip() for line in block.splitlines() if line.strip().startswith("wsl.exe")]


class ShogunOpsDocumentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.startup = STARTUP.read_text(encoding="utf-8")
        cls.custom = CUSTOM.read_text(encoding="utf-8")
        cls.custom_pasteable, cls.custom_pasteable_closed = first_pasteable_block(
            cls.custom
        )
        cls.startup_ops = versioned_block(cls.startup, OPS_BEGIN, OPS_END)
        cls.custom_ops = versioned_block(cls.custom, OPS_BEGIN, OPS_END)
        cls.ops_blocks = (cls.startup_ops, cls.custom_ops)
        cls.startup_diagnostics = versioned_block(
            cls.startup, DIAGNOSTICS_BEGIN, DIAGNOSTICS_END
        )
        cls.custom_diagnostics = versioned_block(
            cls.custom, DIAGNOSTICS_BEGIN, DIAGNOSTICS_END
        )
        cls.diagnostics_blocks = (
            cls.startup_diagnostics,
            cls.custom_diagnostics,
        )

    def test_custom_pasteable_block_is_intact_and_complete(self) -> None:
        self.assertTrue(self.custom_pasteable_closed)
        self.assertNotIn("```text", self.custom_pasteable)
        for marker in (OPS_BEGIN, OPS_END, DIAGNOSTICS_BEGIN, DIAGNOSTICS_END):
            self.assertIn(marker, self.custom_pasteable)
        for phrase in (
            "`restart-all` always requires explicit user approval",
            "must not read or display raw queue/report/log/pane content",
            "Rollback removes the exact host/Workspace exception",
        ):
            self.assertIn(phrase, normalized(self.custom_pasteable))

    def test_markers_are_unique_and_ops_follow_diagnostics(self) -> None:
        for text in (self.startup, self.custom):
            self.assertEqual(text.count(OPS_BEGIN), 1)
            self.assertEqual(text.count(OPS_END), 1)
            self.assertEqual(text.count(DIAGNOSTICS_BEGIN), 1)
            self.assertEqual(text.count(DIAGNOSTICS_END), 1)
            self.assertGreater(text.index(OPS_BEGIN), text.index(DIAGNOSTICS_END))

    def test_legacy_diagnostics_do_not_require_per_call_github_provenance(
        self,
    ) -> None:
        for text in (self.startup, self.custom):
            self.assertNotIn(REGISTRY_URL, text)
        for block in self.diagnostics_blocks:
            for phrase in (
                "Immediately before each diagnostic invocation",
                "schema-version-1 JSON registry",
                "exactly one active deployment",
                "`tool.source_sha256`",
                "GitHub provenance retrieval or validation failure",
                "no active deployment",
                "multiple active deployments",
                "source-hash mismatch",
                "`diagnostic_provenance_untrusted`",
            ):
                self.assertNotIn(phrase, block)

    def test_only_the_exact_legacy_diagnostic_vector_remains_allowlisted(
        self,
    ) -> None:
        for block in self.diagnostics_blocks:
            self.assertEqual(block.count(DIAGNOSTICS), 1)
            self.assertEqual(block.count(DIAGNOSTIC_VECTOR), 1)

    def test_legacy_diagnostics_retain_local_validation_and_fail_closed_guards(
        self,
    ) -> None:
        for block in self.diagnostics_blocks:
            content = normalized(block)
            for phrase in (
                "mode-`0555`",
                "schema-version-1 JSON",
                "ASCII-only bytes",
                "exact key order",
                "cross-field invariants",
                "recomputed `overall`",
                "nonempty stderr",
                "10 seconds",
                "do not use any raw or direct-read fallback",
            ):
                self.assertIn(phrase, content)

    def test_only_the_five_exact_ops_vectors_are_allowlisted_in_order(self) -> None:
        for block in self.ops_blocks:
            self.assertEqual(ops_command_lines(block), list(VECTORS))

    def test_broader_prefixes_remain_forbidden_in_both_ops_blocks(self) -> None:
        for block in self.ops_blocks:
            content = normalized(block)
            for phrase in (
                "shorter `wsl.exe`",
                "`bash -lc`",
                "Python",
                "repo script",
                "arbitrary path",
                "suffix",
                "environment prefix",
            ):
                self.assertIn(phrase, content)

    def test_deployment_preconditions_apply_to_both_ops_blocks(self) -> None:
        for block in self.ops_blocks:
            content = normalized(block)
            for phrase in (
                "one-time deployment checkpoint",
                "reviewed GitHub `main` source",
                "clean runtime repo at the reviewed commit",
                "fixed repo venv/PyYAML dependency",
                "user-owned regular mode-`0555` snapshot",
                "matching host policy",
                "no per-call GitHub registry or source-hash lookup",
            ):
                self.assertIn(phrase, content)

    def test_authorizations_apply_to_both_ops_blocks(self) -> None:
        for block in self.ops_blocks:
            content = normalized(block)
            for phrase in (
                "`status` is routine read-only monitoring",
                "`start` may run once without a new approval",
                "sanitized status is `stopped`",
                "no active task exists",
                "exactly one allowlisted stalled agent",
                "`restart-all` always requires explicit user approval",
            ):
                self.assertIn(phrase, content)

    def test_delivery_and_privacy_boundaries_apply_to_both_ops_blocks(self) -> None:
        for block in self.ops_blocks:
            content = normalized(block)
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
                self.assertIn(phrase, content)

    def test_failure_test_scope_and_rollback_apply_to_both_ops_blocks(self) -> None:
        for block in self.ops_blocks:
            content = normalized(block)
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
                self.assertIn(phrase, content)


if __name__ == "__main__":
    unittest.main()
