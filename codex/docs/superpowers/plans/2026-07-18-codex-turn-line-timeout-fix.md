# Codex Turn LINE Timeout Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent the trusted Codex `Stop` hook from being killed before the production notification endpoint returns successfully.

**Architecture:** Keep the existing synchronous, fail-open notifier and server contract. Separate the 5-second ID-token timeout from a 15-second HTTP timeout, and give the outer Codex command hook 30 seconds so Windows process startup and both bounded operations fit without changing public Cloud Run behavior.

**Tech Stack:** Python 3.13 `unittest`, PowerShell installer tests, Codex `hooks.json`, GitHub.

## Global Constraints

- Notify only the main `Stop` event; do not add `SubagentStop`.
- Preserve existing `config.toml`, desktop `notify`, unrelated hooks, public LIFF, webhook, Cloud Run IAM, and server deployment.
- Never log or persist bearer tokens, raw hook input, raw session/turn IDs, response bodies, or LINE data.
- Keep fail-open behavior and do not add retries, outbox, daemon, or background execution.
- ID-token timeout is 5 seconds, HTTP timeout is 15 seconds, and outer hook timeout is 30 seconds.

---

### Task 1: Timeout regression tests and implementation

**Files:**
- Modify: `codex/hooks/tests/test_codex_turn_line_notify.py`
- Modify: `codex/hooks/tests/test_install_codex_turn_line_hook.ps1`
- Modify: `codex/hooks/codex_turn_line_notify.py`
- Modify: `codex/hooks/install_codex_turn_line_hook.ps1`

**Interfaces:**
- Consumes: existing `mint_id_token()`, `post_notification()`, and installer-owned `Stop` handler.
- Produces: `TOKEN_TIMEOUT_SECONDS = 5`, `HTTP_TIMEOUT_SECONDS = 15`, and installer handler `timeout = 30`.

- [x] **Step 1: Change only the timeout expectations in tests.** Rename the HTTP test to `test_posts_json_with_bearer_and_fifteen_second_timeout`, expect `urlopen(..., timeout=15)`, and expect installer handler timeout `30`; retain the token timeout expectation `5`.

- [x] **Step 2: Run focused tests and verify RED.** Run `python -m unittest codex.hooks.tests.test_codex_turn_line_notify.PostNotificationTests.test_posts_json_with_bearer_and_fifteen_second_timeout -v` and `powershell.exe -NoProfile -ExecutionPolicy Bypass -File codex/hooks/tests/test_install_codex_turn_line_hook.ps1`. Expected: Python reports timeout `5 != 15`; installer reports timeout `10 != 30`.

- [x] **Step 3: Implement the minimal timeout split.** Replace the shared Python constant with `TOKEN_TIMEOUT_SECONDS = 5` and `HTTP_TIMEOUT_SECONDS = 15`; use them only in token mint and HTTP POST respectively. Change only the installer-owned handler timeout from `10` to `30`.

- [x] **Step 4: Run full tests and verify GREEN.** Run `python -m unittest codex.hooks.tests.test_codex_turn_line_notify -v` and `powershell.exe -NoProfile -ExecutionPolicy Bypass -File codex/hooks/tests/test_install_codex_turn_line_hook.ps1`. Expected: 19 Python tests and 10 installer tests pass with zero failures.

### Task 2: Documentation, installation, and live verification

**Files:**
- Modify: `codex/hooks/README.md`
- Modify: `codex/work_log.md`
- Install from: `codex/hooks/codex_turn_line_notify.py`
- Install with: `codex/hooks/install_codex_turn_line_hook.ps1`

**Interfaces:**
- Consumes: tested notifier and installer from Task 1.
- Produces: auditable timeout rationale, exact local handler, and live CLI/Desktop evidence.

- [x] **Step 1: Update operator documentation.** State token 5 seconds, HTTP 15 seconds, hook 30 seconds, the production latency evidence, and that the changed hook hash requires exact-hook trust review again.

- [x] **Step 2: Verify repository state.** Re-run both full test suites, inspect `git diff --check`, and confirm only the notifier, installer, tests, spec, plan, README, and work log changed.

- [ ] **Step 3: Commit and publish the reviewed source change.** Commit the timeout fix, push the task branch, open a PR, review the diff/checks, and merge to `main` before applying locally.

- [ ] **Step 4: Apply locally through the canonical installer.** Run `DryRun`, then `Apply` under Windows user `jinnouchi`; verify one owned `Stop` handler, timeout 30, identical `command`/`commandWindows`, source/installed SHA-256 equality, no `SubagentStop`, and unchanged `config.toml` notify.

- [ ] **Step 5: Re-trust and perform one live test.** Use CLI `/hooks` to review the changed hash, trust only the exact notifier hook, restart Desktop, run one main turn, and require a new `status=sent` or `status=deduplicated` log entry plus user confirmation of one official LINE notification.

### Task 3: Existing notifier atomic replacement compatibility

**Files:**
- Modify: `codex/hooks/tests/test_install_codex_turn_line_hook.ps1`
- Modify: `codex/hooks/install_codex_turn_line_hook.ps1`

**Interfaces:**
- Consumes: existing installed notifier path and same-directory atomic replacement flow.
- Produces: Windows PowerShell-compatible replacement of a stale notifier with zero temporary or replacement-backup residue.

- [x] **Step 1: Reproduce the live Apply failure.** Applying main over an existing stale notifier fails in `[IO.File]::Replace($TemporaryPath, $InstalledNotifier, $null)` with `The path is not of a legal form`; installed handler remains timeout 10 and installer temp residue remains zero.

- [x] **Step 2: Add a failing installer test.** Apply once, overwrite the installed notifier with stale bytes, Apply again, require installed/source byte equality, and require zero `*.tmp.*` and `*.replace-backup.*` files.

- [x] **Step 3: Verify RED.** Run the installer test suite and require only the stale-notifier replacement case to fail with the illegal-path error.

- [x] **Step 4: Implement a real same-directory replacement-backup path.** Pass a unique non-null path to `File.Replace` and delete that transient backup in `finally`, while preserving the existing temp cleanup.

- [x] **Step 5: Verify GREEN.** Run the installer suite twice and the Python suite once; require 11 installer tests and 19 Python tests with zero failures and no residue.
