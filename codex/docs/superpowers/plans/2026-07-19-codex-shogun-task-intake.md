# Codex経由Shogun Task Intake Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CodexがShogun操作依頼を受けたとき、前回taskの意図しない継続を防ぎ、新規・明示継続・曖昧の三経路を安全に扱うオンライン指示正本を実装する。

**Architecture:** `codex/CODEX_DESKTOP_STARTUP.md` に詳細なversioned intake contractと標準ガード文を置き、`codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` の貼付文面から毎回そのcontractを適用させる。Pythonの文書contract testで両ファイルの同期、三経路、診断fail-closed、権限境界を固定し、`codex/work_log.md` にsanitizedな実装記録を残す。

**Tech Stack:** Markdown、Python 3標準ライブラリ `unittest`、PowerShell、Git/GitHub

## Global Constraints

- 基準は `sjinnouchi-ux/workspace` main `c82796a06de3d3786f6d7d7493c3c1997fd9db20` とする。
- branchは `agent/codex-shogun-task-intake` を使用し、mainへ直接pushしない。
- 詳細contractのmarker名は `CODEX_SHOGUN_TASK_INTAKE_V1` とする。
- 継続の明示がないShogun操作依頼は `new` とし、前回taskを自動継続しない。
- 明示的な継続だけを `resume` とし、完了済み部分と終了済みcommandを再実行しない。
- 新規か継続か一意に決められない場合は `ambiguous` とし、Shogunへ送らずユーザーへ確認する。
- 配送前診断は既存の固定read-only contractを維持し、信頼済みの `overall=healthy` 以外では送信しない。
- 「Shogunを使って」等の明示依頼が許可するのは、指定taskを既存の承認済み入力経路へ1回配送することだけとする。
- start、stop、restart、repair、deployment、permission自動承認、新transport作成を許可しない。
- 生queue、pane、report、ログ本文、秘密値、token、認証JSON、`.env` を読み取り・記録しない。
- Shogun repo、Shogun WebUI、WSL2 runtime、tmux sessionを変更しない。
- GitHub上のCustom Instructions正本だけを更新し、各PCの設定画面への再貼付は行わない。

---

### Task 1: 文書contract testをREDにする

**Files:**
- Create: `codex/tests/test_shogun_task_intake_docs.py`
- Read: `codex/CODEX_DESKTOP_STARTUP.md:119`
- Read: `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md:11`

**Interfaces:**
- Consumes: UTF-8のstartup文書とCustom Instructions文書。
- Produces: versioned marker、三経路、標準ガード、diagnostics gate、権限境界を検査する `unittest` suite。

- [ ] **Step 1: 文書contract testを作成する**

`codex/tests/test_shogun_task_intake_docs.py` を次の内容で作成する。

```python
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
```

- [ ] **Step 2: REDを確認する**

Run:

```powershell
python codex/tests/test_shogun_task_intake_docs.py -v
```

Expected: 6 tests run、`CODEX_SHOGUN_TASK_INTAKE_V1` blockが未実装のためFAILまたはERROR。SKIPは0。

- [ ] **Step 3: RED testだけをcommitする**

```powershell
git add codex/tests/test_shogun_task_intake_docs.py
git commit -m "test(codex): define Shogun task intake contract"
```

---

### Task 2: startupとCustom Instructionsへ最小実装を追加する

**Files:**
- Modify: `codex/CODEX_DESKTOP_STARTUP.md:119-181`
- Modify: `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md:11-72`
- Test: `codex/tests/test_shogun_task_intake_docs.py`

**Interfaces:**
- Consumes: Task 1の `CODEX_SHOGUN_TASK_INTAKE_V1` contract test。
- Produces: future Codex taskが取得するversioned intake blockと、各PC用bootstrap文面。

- [ ] **Step 1: startupへversioned intake blockを追加する**

`codex/CODEX_DESKTOP_STARTUP.md` のShogun概要と `### Runtime discovery` の間へ、次を追加する。

```markdown
<!-- BEGIN CODEX_SHOGUN_TASK_INTAKE_V1 -->
### Codex-mediated Shogun task intake

ユーザーが「Shogunを使って」「Shogun経由で」「将軍へ依頼して」など、CodexからShogunを操作する意図を明示した場合に適用します。一般的な質問だけの場合はruntimeへ配送しません。

この明示依頼が許可するのは、指定されたtask本文を既存の承認済みShogun task入力経路へ1回配送することだけです。start、stop、restart、repair、deployment、permission自動承認、新しいtransportの作成は含みません。承認済み入力経路を確定できない場合は送信せず、不足する入口または承認を報告します。

配送前に、この文書の固定read-only diagnostics contractでprovenanceとschemaを検証します。信頼済み診断の再計算結果が `overall=healthy` でない場合は送信しません。診断失敗時にraw fallback、生queue、pane、report、ログ本文の直接読取を行いません。

依頼意図を次の3種類へ分類します。

1. `new`: 明示的な継続表現がない依頼。次のガードをtask本文の先頭へ付けます。

   ```text
   この依頼は新規taskです。前回の未完了task、未配送command、未処理receiptの状態を先に確認し、sanitized summaryで報告してください。前回taskを自動継続・再実行せず、今回の依頼は新しいtaskと新しいcommand epochとして開始してください。前回作業と今回の依頼が衝突する場合は実行せず、衝突理由と選択肢を報告してください。
   ```

2. `resume`: 「前回の続きをして」など継続が明示された依頼だけ。次のガードを付けます。

   ```text
   この依頼は前回taskの明示的な継続です。前回taskの現在状態と残作業を確認し、完了済み部分と終了済みcommandを再実行せず、残作業だけを継続してください。対象taskを一意に特定できない場合や状態が矛盾する場合は実行せず、sanitized summaryで確認を求めてください。
   ```

3. `ambiguous`: 「前と同じ」「さっきの件」など新規か継続か一意に決められない依頼。Shogunへ送信せず、Codexがユーザーへ確認します。既定値で継続扱いにしません。

Shogunから受け取る状態報告にも秘密値、Inbox本文、pane内容、生queue、生report、生ログを含めないよう指示します。
<!-- END CODEX_SHOGUN_TASK_INTAKE_V1 -->
```

- [ ] **Step 2: Custom Instructionsの貼付文面へbootstrapを追加する**

`codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` の `Paste This Text` code block内で、Shogunの独立運用説明の直後へ次を追加する。

```text
「Shogunを使って」「Shogun経由で」などCodexからShogunを操作する依頼では、毎回取得した共通起動手順の `CODEX_SHOGUN_TASK_INTAKE_V1` を適用してください。明示的な継続指示がない依頼は新規taskとして扱い、前回taskを自動継続しないでください。明示的な継続だけを再開し、新規か継続か曖昧な場合はShogunへ送信せず利用者へ確認してください。Shogun taskの配送許可をstart、stop、restart、repair、deployment、permission承認へ拡張しないでください。
```

同ファイルの成功条件へ次を追加する。

```markdown
- Shogun操作依頼で `CODEX_SHOGUN_TASK_INTAKE_V1` を取得し、`new`、`resume`、`ambiguous` を区別する。
- 新規taskは前回taskを自動継続せず、曖昧な依頼とunhealthy/untrusted診断では送信しない。
```

- [ ] **Step 3: GREENを確認する**

Run:

```powershell
python codex/tests/test_shogun_task_intake_docs.py -v
```

Expected: 6 passed、0 failed、0 skipped。

- [ ] **Step 4: 既存Codex hook回帰を確認する**

Run:

```powershell
python -m unittest -v codex/hooks/tests/test_codex_turn_line_notify.py
powershell -NoProfile -ExecutionPolicy Bypass -File codex/hooks/tests/test_install_codex_turn_line_hook.ps1
```

Expected: Python 19 passed、PowerShell 11 passed、failed 0、skipped 0。

- [ ] **Step 5: 実装をcommitする**

```powershell
git add codex/CODEX_DESKTOP_STARTUP.md codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md
git commit -m "docs(codex): gate Shogun task intake"
```

---

### Task 3: 作業ログと最終検証を完了する

**Files:**
- Modify: `codex/work_log.md`
- Modify: `codex/docs/superpowers/plans/2026-07-19-codex-shogun-task-intake.md`
- Verify: all files changed from `c82796a06de3d3786f6d7d7493c3c1997fd9db20`

**Interfaces:**
- Consumes: Task 1とTask 2のcommit、実測test結果、diff。
- Produces: GitHubへ残るsanitizedな作業記録とpublish可能なclean branch。

- [ ] **Step 1: work logへ実装記録を追加する**

`codex/work_log.md` の末尾へ次を追加する。test結果はTask 2で指定した全commandが期待値どおり成功した場合だけ記録する。

```markdown
## 2026-07-19 — Codex経由Shogun task intake

- `workspace` main `c82796a06de3d3786f6d7d7493c3c1997fd9db20` からbranch `agent/codex-shogun-task-intake` を作成した。
- 毎task取得されるstartupへversioned `CODEX_SHOGUN_TASK_INTAKE_V1` contractを追加し、Custom Instructions正本から適用する二層構成とした。
- 明示的な継続がない依頼は新規taskとして前回taskを自動継続せず、明示継続だけを再開し、曖昧な依頼は配送前にユーザーへ確認する。
- Shogun task配送の権限をstart、stop、restart、repair、deployment、permission承認へ拡張しない。
- 文書contract test 6件、既存Python hook test 19件、PowerShell installer test 11件が成功し、失敗0、SKIP 0だった。
- Shogun repo、WebUI、WSL2 runtime、tmux session、各PCのCustom Instructions設定は変更していない。
```

- [ ] **Step 2: planの完了checkboxと実測結果を更新する**

完了した各stepの `- [ ]` を `- [x]` に変更し、末尾へ次の形式で実測結果を追加する。

```markdown
## Results

- Contract tests: 6 passed / 0 failed / 0 skipped
- Existing Python hook tests: 19 passed / 0 failed / 0 skipped
- Existing PowerShell installer tests: 11 passed / 0 failed / 0 skipped
- `git diff --check`: passed
- Shogun runtime deployment: not performed
- Local Custom Instructions update: not performed
```

- [ ] **Step 3: 全検証を再実行する**

Run:

```powershell
python codex/tests/test_shogun_task_intake_docs.py -v
python -m unittest -v codex/hooks/tests/test_codex_turn_line_notify.py
powershell -NoProfile -ExecutionPolicy Bypass -File codex/hooks/tests/test_install_codex_turn_line_hook.ps1
git diff --check c82796a06de3d3786f6d7d7493c3c1997fd9db20...HEAD
git diff --check
git status --short
```

Expected: 6 + 19 + 11 tests passed、failed 0、skipped 0、diff check出力なし。statusには意図したwork logとplan変更だけが表示される。

- [ ] **Step 4: secretsとscopeを確認する**

Run:

```powershell
git diff --stat c82796a06de3d3786f6d7d7493c3c1997fd9db20...HEAD
git diff --name-only c82796a06de3d3786f6d7d7493c3c1997fd9db20...HEAD
git diff c82796a06de3d3786f6d7d7493c3c1997fd9db20...HEAD
```

Expected: 変更はdesign、plan、startup、Custom Instructions、contract test、work logだけ。秘密値、runtime本文、Shogun/WebUI code差分なし。

- [ ] **Step 5: work logとplanをcommitする**

```powershell
git add codex/work_log.md codex/docs/superpowers/plans/2026-07-19-codex-shogun-task-intake.md
git commit -m "docs(codex): record Shogun intake rollout"
```

---

### Task 4: 独立reviewとdraft PR公開

**Files:**
- Review: `git diff c82796a06de3d3786f6d7d7493c3c1997fd9db20...HEAD`
- Publish: branch `agent/codex-shogun-task-intake`

**Interfaces:**
- Consumes: cleanで全test成功のbranch。
- Produces: `sjinnouchi-ux/workspace` main向けdraft PR。

- [ ] **Step 1: 独立reviewを実施する**

review観点:

- startupとCustom Instructionsの責務分離が守られている。
- new/resume/ambiguousが相互排他的である。
- 新規依頼が古いtaskまたはcommandを再実行しない。
- task配送許可がruntime管理権限へ拡張されていない。
- diagnosticsのprovenance、schema、raw fallback禁止を弱めていない。
- 生runtimeデータ、秘密値、実運用内容がない。

CriticalまたはImportant findingがあれば、再現する失敗testを先に追加して修正し、Task 3の全検証を再実行する。

- [ ] **Step 2: pushする**

```powershell
git push -u origin agent/codex-shogun-task-intake
```

- [ ] **Step 3: draft PRを作成する**

PR title:

```text
docs(codex): gate Shogun task intake
```

PR本文へ、base SHA、目的、変更ファイル、6/19/11のtest実数、failed/skip 0、独立review、既知制約、rollback、Shogun runtime/WebUI/Custom Instructions未変更を記載する。

- [ ] **Step 4: PRとlocal stateを確認する**

```powershell
gh pr checks --watch
git status --short --branch
```

Expected: 必須check成功、branchはoriginを追跡、未commit・未push変更なし。mergeはユーザーの別承認があるまで行わない。
