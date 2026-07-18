# Codex Turn-Ended LINE Windows Client Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install a user-level Codex `Stop` hook on `NUCBOX_K8_PLUS` that runs a standard-library Python notifier and calls the verified kakeibo endpoint once per main turn without changing the existing desktop notifier.

**Architecture:** The hook hashes `session_id:turn_id`, impersonates the dedicated service account with gcloud, and POSTs only schema version, event hash, JST time, and host label. An idempotent PowerShell installer adds/removes only this handler in `~/.codex/hooks.json`; existing hooks and `notify = ["codex-computer-use.exe", "turn-ended"]` remain untouched.

**Tech Stack:** Windows PowerShell, Python 3.13 standard library, Codex lifecycle hooks, gcloud CLI, Google OIDC, unittest.

## Global Constraints

- Execute only after the server endpoint is live and verified.
- Use a task-specific `sjinnouchi-ux/workspace` clone/worktree based on current `main`.
- Target host `NUCBOX_K8_PLUS`, Windows user `jinnouchi`, Google owner `s.jinnouchi@yumekango.com`.
- Preserve existing `notify` exactly; configure `Stop`, never `SubagentStop`.
- Never read transcript, cwd, model, task title, prompt, or conversation content.
- Never store/print bearer tokens, key JSON, raw hook JSON, raw IDs, response bodies, or LINE data.
- Exact endpoint: `https://kakeibo-api-570965759130.asia-northeast1.run.app/internal/codex/turn-ended/notify`; audience is its service root; notifier SA is `codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com`.
- HTTP and token timeouts are 5 seconds; hook timeout is 10 seconds; notifier always fails open.
- No outbox, daemon, retry, or completion classification in initial release.
- No `~/.codex` write, restart, trust action, or live call before separate approval.

---

## File Map

- Create `codex/hooks/codex_turn_line_notify.py` and unit tests.
- Create `codex/hooks/install_codex_turn_line_hook.ps1` and isolated installer tests.
- Create `codex/hooks/README.md`; modify `codex/codex-windows-setup.md` and `codex/work_log.md` after verification.

### Task 1: Fail-Open Python Notifier

**Files:**
- Create: `codex/hooks/codex_turn_line_notify.py`
- Test: `codex/hooks/tests/test_codex_turn_line_notify.py`

**Interfaces:**
- Consumes bounded JSON stdin with `hook_event_name`, `session_id`, `turn_id`.
- Produces `read_hook_event`, `build_payload`, `mint_id_token`, `post_notification`, and fail-open `main`.

- [ ] **Step 1: Write failing tests** for exact payload, deterministic SHA-256, Stop-only behavior, missing/non-string IDs, 65,536-byte limit, host validation, subprocess/HTTP timeout, privacy, and `main` returning 0 on operational failures.

```python
event={"hook_event_name":"Stop","session_id":"session-secret","turn_id":"turn-secret","cwd":"C:/secret"}
payload=build_payload(event, datetime(2026,7,17,14,32,tzinfo=ZoneInfo("Asia/Tokyo")), "NUCBOX_K8_PLUS")
self.assertEqual(payload["event_id"], hashlib.sha256(b"session-secret:turn-secret").hexdigest())
self.assertNotIn("session-secret", json.dumps(payload))
self.assertEqual(set(payload), {"schema_version","event_id","ended_at","host_label"})
```

- [ ] **Step 2: Verify RED:** `python -m unittest discover -s codex\hooks\tests -p "test_codex_turn_line_notify.py" -v` must fail import.

- [ ] **Step 3: Implement bounded parse and payload**

```python
MAX_STDIN_BYTES=65_536
def build_payload(event, now, host_label):
    if event.get("hook_event_name") != "Stop": raise ValueError("unsupported hook event")
    session_id=event.get("session_id"); turn_id=event.get("turn_id")
    if not isinstance(session_id,str) or not session_id: raise ValueError("missing session_id")
    if not isinstance(turn_id,str) or not turn_id: raise ValueError("missing turn_id")
    event_id=hashlib.sha256(f"{session_id}:{turn_id}".encode()).hexdigest()
    return {"schema_version":1,"event_id":event_id,"ended_at":now.astimezone(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds"),"host_label":host_label}
```

- [ ] **Step 4: Implement token mint and POST** using `subprocess.run` argv `gcloud auth print-identity-token`, impersonation, audience, `--include-email`, `--quiet`, captured output, check, and 5-second timeout. Use `urllib.request` for JSON POST and parse at most 4,096 bytes. Return only `sent`, `deduplicated`, or `no_subscribers`; never log stdout/stderr/body.

- [ ] **Step 5: Implement fail-open logging/main.** CLI requires endpoint, audience, service-account, host-label, gcloud, log-path. Log only timestamp/status/error class. Catch validation, subprocess, timeout, URL, JSON, and OS failures; return 0.

- [ ] **Step 6: Verify:** run unittest; run `rg -n "transcript_path|cwd|model|permission_mode" codex\hooks\codex_turn_line_notify.py`, expecting no matches.

- [ ] **Step 7: Commit:** `git commit -m "feat(codex): add fail-open turn notifier"` with source/tests.

### Task 2: Idempotent Hook Installer

**Files:**
- Create: `codex/hooks/install_codex_turn_line_hook.ps1`
- Test: `codex/hooks/tests/test_install_codex_turn_line_hook.ps1`

- [ ] **Step 1: Write isolated tests** using an explicit temporary `-CodexUserDir` without changing `$HOME`, `$home`, or `$CODEX_HOME`. Cover dry-run no-write, apply, second apply idempotency, unrelated handler preservation, remove-only-owned-handler, and no `config.toml` modification.
- [ ] **Step 2: Verify RED** by running the PowerShell test file.
- [ ] **Step 3: Implement mutually exclusive `-DryRun`, `-Apply`, `-Remove` plus required CodexUserDir/PythonPath/GcloudPath and exact non-secret defaults. Reject filesystem-root targets.
- [ ] **Step 4: Merge safely.** The handler is `type=command`, `timeout=10`, `statusMessage="Sending LINE turn notification"`, required `command`, and Windows override `commandWindows`. Set `command` and `commandWindows` to the same safe invocation of the installed script with exact endpoint/audience/SA/host. Match ownership only by exact script filename plus endpoint. Preserve unrelated events/groups/handlers. Backup only for Apply/Remove; write same-directory temp then atomic rename. Resolve and accept `gcloud.cmd`, not the PowerShell `gcloud.ps1` wrapper, because the notifier launches it directly with Python `subprocess`.
- [ ] **Step 5: Run installer tests twice**, expecting both pass and no temporary residue.
- [ ] **Step 6: Commit:** `git commit -m "feat(codex): install turn notification hook safely"`.

### Task 3: Documentation and Code PR

**Files:**
- Create: `codex/hooks/README.md`
- Modify: `codex/work_log.md`

- [ ] **Step 1:** Document exact dry-run/apply/remove, trust review, diagnostics, rollback, and preserved notify state.
- [ ] **Step 2:** Run all unittest, installer tests, compileall, and `git diff --check`.
- [ ] **Step 3:** Record base SHA, commits, test counts, and that local install/live remain unperformed.
- [ ] **Step 4:** Commit, push, and open Draft PR; merge only after review and live server availability.

### Task 4: Correct-Boundary Installation and E2E

**Files:**
- Modify after verification: `codex/codex-windows-setup.md`, `codex/work_log.md`

- [ ] **Step 1: Read-only preflight**

```powershell
if($env:USERNAME -ne "jinnouchi"){throw "Wrong Windows user"}
if($env:COMPUTERNAME -ne "NUCBOX_K8_PLUS"){throw "Wrong host"}
$PythonCandidates=@(Get-Command python.exe -CommandType Application -All -ErrorAction Stop | Where-Object { $_.Source -notlike '*\Microsoft\WindowsApps\python.exe' })
if($PythonCandidates.Count -eq 0){throw "Runnable Python was not found"}
$PythonPath=[string]$PythonCandidates[0].Source
& $PythonPath --version
if($LASTEXITCODE -ne 0){throw "Selected Python is not runnable"}
$GcloudPath=(Get-Command gcloud.cmd -CommandType Application -ErrorAction Stop).Source
$CodexUserDir=Join-Path $env:USERPROFILE ".codex"
gcloud auth list --filter="status:ACTIVE" --format="value(account)"
```

Require business account. Inspect only hook counts and notify executable/first-argument leaves.

- [ ] **Step 2: Verify impersonation without outputting token**

```powershell
$IdToken=& $GcloudPath auth print-identity-token --impersonate-service-account=codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com --audiences=https://kakeibo-api-570965759130.asia-northeast1.run.app --include-email --quiet 2>$null
if([string]::IsNullOrWhiteSpace($IdToken)){throw "OIDC impersonation failed"}
$IdToken=$null
```

- [ ] **Step 3:** Run installer DryRun and obtain explicit local-install approval.
- [ ] **Step 4:** Apply, restart if required, review/trust exact hook hash; never bypass trust.
- [ ] **Step 5:** Run harmless main turn ending with `通知テスト終了`; confirm exactly one minimal LINE message with JST time.
- [ ] **Step 6:** Verify dedup via test harness and no SubagentStop notification.
- [ ] **Step 7:** Verify fail-open against unreachable local test endpoint; installed production endpoint is not changed.
- [ ] **Step 8:** Test Remove preserves other hooks/notify, then re-Apply and confirm exactly one owned handler.
- [ ] **Step 9:** Publish evidence, commit/push, verify no uncommitted/untracked/unpushed task data, then clean task workspace.
