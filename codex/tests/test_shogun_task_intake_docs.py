from __future__ import annotations

import unittest
from pathlib import Path


CODEX_DIR = Path(__file__).resolve().parents[1]
STARTUP = (CODEX_DIR / "CODEX_DESKTOP_STARTUP.md").read_text(encoding="utf-8")
CUSTOM = (CODEX_DIR / "CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md").read_text(
    encoding="utf-8"
)
BEGIN = "<!-- BEGIN CODEX_SHOGUN_TASK_INTAKE_V1 -->"
END = "<!-- END CODEX_SHOGUN_TASK_INTAKE_V1 -->"


def intake_section() -> str:
    if STARTUP.count(BEGIN) != 1 or STARTUP.count(END) != 1:
        raise AssertionError("expected one versioned Shogun intake block")
    before, remainder = STARTUP.split(BEGIN, 1)
    section, after = remainder.split(END, 1)
    if not before or not after:
        raise AssertionError("Shogun intake block must be embedded in startup")
    return section


class ShogunTaskIntakeDocsTests(unittest.TestCase):
    def test_startup_has_one_versioned_intake_contract(self) -> None:
        section = intake_section()
        self.assertIn("Codex-mediated Shogun task intake", section)
        self.assertIn("overall=healthy", section)
        self.assertIn("raw fallback", section)

    def test_new_task_guard_is_exact_and_fail_closed(self) -> None:
        section = intake_section()
        self.assertIn("この依頼は新規taskです。", section)
        self.assertIn("前回taskを自動継続・再実行せず", section)
        self.assertIn("新しいtaskと新しいcommand epoch", section)
        self.assertIn("衝突する場合は実行せず", section)

    def test_resume_requires_explicit_intent(self) -> None:
        section = intake_section()
        self.assertIn("明示的な継続", section)
        self.assertIn("完了済み部分と終了済みcommandを再実行せず", section)
        self.assertIn("対象taskを一意に特定できない場合", section)

    def test_ambiguous_intent_is_not_dispatched(self) -> None:
        section = intake_section()
        self.assertIn("ambiguous", section)
        self.assertIn("Shogunへ送信せず", section)
        self.assertIn("ユーザーへ確認", section)

    def test_intent_classification_order_is_mutually_exclusive(self) -> None:
        section = intake_section()
        self.assertIn("まず `ambiguous` を除外", section)
        self.assertIn(
            "`ambiguous` に該当せず、明示的な継続表現がない依頼", section
        )

    def test_task_authority_does_not_expand_runtime_authority(self) -> None:
        section = intake_section()
        self.assertIn("既存の承認済みShogun task入力経路へ1回", section)
        self.assertIn(
            "start、stop、restart、repair、deployment、permission自動承認、"
            "新しいtransportの作成は含みません",
            section,
        )

    def test_custom_instructions_bootstraps_the_online_contract(self) -> None:
        self.assertIn("CODEX_SHOGUN_TASK_INTAKE_V1", CUSTOM)
        self.assertIn("Shogunを使って", CUSTOM)
        self.assertIn("前回taskを自動継続しない", CUSTOM)
        self.assertIn("明示的な継続", CUSTOM)


if __name__ == "__main__":
    unittest.main()
