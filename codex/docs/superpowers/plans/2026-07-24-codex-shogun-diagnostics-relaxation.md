# Codex Shogun Diagnostics Relaxation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove per-call GitHub registry and source-hash verification from Shogun diagnostics and make fixed Ops `status` the sole delivery preflight.

**Architecture:** This is a Workspace policy-only change. The versioned task-intake block routes deployed Shogun operations and delivery to the fixed Ops wrapper, while the legacy diagnostics block retains its exact argv, sanitized schema validation, timeout, and raw-fallback prohibition without network provenance lookup. Startup and the pasteable Custom Instructions remain semantically identical where the contracts overlap.

**Tech Stack:** Markdown policy contracts, Python `unittest`, Git/GitHub branch and PR workflow, atomic Windows host-policy installer.

## Global Constraints

- Base branch is `workspace/main` at or after `62b45fb2a2a5ec922d86e4ade9e63e8955613812`.
- Work only on `agent/codex-shogun-diagnostics-relaxation`; never push directly to `main`.
- Preserve the exact five fixed Ops vectors and the exact one fixed legacy diagnostic vector.
- Do not modify Shogun executables, WSL runtime, queue/report schema, tmux sessions, Finance repositories, or production services.
- Do not read or display raw queue, report, log, pane, secret, environment, task-body, or personal-identifier content.
- Run only the two focused document contract test files and `git diff --check`; do not run the full workspace suite.
- Merge and real-host policy installation are separate explicit checkpoints.

---

### Task 1: Make the policy contract tests express the relaxed routing

**Files:**
- Modify: `codex/tests/test_shogun_task_intake_docs.py`
- Modify: `codex/tests/test_shogun_ops_docs.py`

**Interfaces:**
- Consumes: versioned blocks `CODEX_SHOGUN_TASK_INTAKE_V1`, `CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1`, and `CODEX_SHOGUN_OPS_V1`.
- Produces: executable assertions that define Ops-first delivery routing and prohibit per-call registry/source-hash prerequisites.

- [ ] **Step 1: Add failing intake-routing assertions**

Add this method to `ShogunTaskIntakeDocsTests`:

```python
    def test_deployed_ops_status_is_the_only_delivery_preflight(self) -> None:
        section = intake_section()
        self.assertIn("`CODEX_SHOGUN_OPS_V1`", section)
        self.assertIn("固定 `status`", section)
        self.assertIn("先行または並行実行しません", section)
        self.assertNotIn(
            "配送前に、この文書の固定read-only diagnostics contract", section
        )
```

- [ ] **Step 2: Add failing diagnostics-relaxation assertions**

In `codex/tests/test_shogun_ops_docs.py`, add constants for the legacy command and removed registry URL:

```python
DIAGNOSTICS = "/home/jinnouchi/.local/libexec/shogun-codex-diagnostics"
DIAGNOSTIC_VECTOR = (
    "wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun "
    f"{DIAGNOSTICS} summary"
)
REGISTRY_URL = (
    "https://raw.githubusercontent.com/sjinnouchi-ux/multi-agent-shogun/main/"
    "docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md"
)
```

Add a diagnostics block extractor in `setUpClass` and these two methods:

```python
    def test_legacy_diagnostics_has_no_per_call_github_provenance(self) -> None:
        for text in (self.startup, self.custom):
            self.assertNotIn(REGISTRY_URL, text)
            self.assertNotIn("active deployment", text)
            self.assertNotIn("registry source hash", text)
            self.assertIn(DIAGNOSTIC_VECTOR, text)

    def test_retained_diagnostics_safety_contract(self) -> None:
        for block in self.diagnostics_blocks:
            content = normalized(block)
            for phrase in (
                "mode-`0555` snapshot",
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
```

Set `self.startup_diagnostics`, `self.custom_diagnostics`, and `self.diagnostics_blocks` using `versioned_block` and the existing diagnostics markers.

- [ ] **Step 3: Run the focused tests and verify RED**

Run:

```powershell
python codex/tests/test_shogun_ops_docs.py
python codex/tests/test_shogun_task_intake_docs.py
```

Expected: the new assertions fail because intake still mandates legacy diagnostics and the documents still contain the registry URL and active-deployment/source-hash requirements. Existing assertions should remain green.

- [ ] **Step 4: Commit the failing contract tests**

```powershell
git add codex/tests/test_shogun_ops_docs.py codex/tests/test_shogun_task_intake_docs.py
git commit -m "test(codex): require relaxed Shogun diagnostics routing"
```

---

### Task 2: Implement the Ops-first and registry-free policy text

**Files:**
- Modify: `codex/CODEX_DESKTOP_STARTUP.md`
- Modify: `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`

**Interfaces:**
- Consumes: Task 1 contract assertions.
- Produces: online startup policy and matching host-policy source with unambiguous Ops-first precedence.

- [ ] **Step 1: Replace the delivery preflight paragraph in Startup**

Within `CODEX_SHOGUN_TASK_INTAKE_V1`, replace the legacy diagnostics prerequisite with:

```markdown
配備済みで有効な `CODEX_SHOGUN_OPS_V1` がある場合、Shogunの操作とtask配送前の状態確認には同contractの固定 `status` だけを使用します。legacy `shogun-codex-diagnostics summary` を先行または並行実行しません。sanitized statusが `healthy` の場合だけ1回配送し、`stopped` の場合の1回起動、配送、限定restartの条件は `CODEX_SHOGUN_OPS_V1` に従います。Opsが未配備・無効・失敗・不明の場合は、承認済み入力経路を確認できないものとして配送せず、raw fallbackを行わず報告します。
```

- [ ] **Step 2: Relax the legacy diagnostics block in Startup**

Delete the per-call registry fetch, active-deployment cardinality, and registry/tool hash comparison paragraphs. Begin the block with:

```markdown
The installed, user-owned regular mode-`0555` snapshot at the fixed path is the trust checkpoint for direct legacy diagnostic requests. No per-call GitHub registry, active-deployment, or source-hash lookup is required.
```

Keep the exact command vector, allowlisted metadata description, ASCII/schema/key-order/cardinality/enums/cross-field/recomputed-overall checks, short-prefix prohibition, 10-second limit, nonzero/empty/non-JSON/partial/stderr failure handling, and raw/direct-read fallback prohibition. Remove `diagnostic_provenance_untrusted`; retain `diagnostic_process_failed` for process and output-contract failures.

- [ ] **Step 3: Apply the same semantic changes to Custom Instructions**

Update the pasteable block in `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` with the same task-intake precedence and relaxed legacy diagnostics wording. Do not add nested Markdown fences inside the outer `## Paste This Text` fence. In the Verification section, replace the per-invocation registry/SHA success condition with:

```markdown
- Deployed Shogun operation and delivery requests use fixed Ops `status` without a legacy diagnostics prerequisite or per-call GitHub registry/source-hash lookup.
- Direct legacy diagnostics use the installed mode-`0555` snapshot as the trust checkpoint while retaining exact argv, schema/invariant validation, empty stderr, and the 10-second limit.
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
python codex/tests/test_shogun_ops_docs.py
python codex/tests/test_shogun_task_intake_docs.py
git diff --check
```

Expected: all Shogun Ops tests and all task-intake tests pass; `git diff --check` produces no output.

- [ ] **Step 5: Commit the policy implementation**

```powershell
git add codex/CODEX_DESKTOP_STARTUP.md codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md
git commit -m "docs(codex): relax Shogun diagnostic provenance"
```

---

### Task 3: Record verification, review, and publish the policy change

**Files:**
- Modify: `codex/work_log.md`
- Verify: `codex/docs/superpowers/specs/2026-07-24-codex-shogun-diagnostics-relaxation-design.md`
- Verify: `codex/docs/superpowers/plans/2026-07-24-codex-shogun-diagnostics-relaxation.md`

**Interfaces:**
- Consumes: passing Task 2 policy and tests.
- Produces: auditable work log, reviewed branch, and draft PR ready for merge approval.

- [ ] **Step 1: Append the work-log entry**

Append a `2026-07-24 — Shogun diagnostics per-call provenance relaxation` entry recording:

```markdown
- Root cause: task intake required legacy diagnostics before delivery even after the fixed Ops wrapper was deployed, creating a circular pre-execution source-hash approval failure.
- Decision: fixed Ops `status` is the sole deployed operation/delivery preflight; direct legacy diagnostics no longer perform per-call GitHub registry, active-deployment, or source-hash lookup.
- Retained: exact argv, mode `0555`, sanitized ASCII JSON/schema/invariant validation, empty stderr, 10-second legacy timeout, privacy boundary, and raw-fallback prohibition.
- Verification: focused Ops and task-intake document tests passed; `git diff --check` was clean. The full suite was intentionally not run.
- Non-changes: Shogun executable snapshots/runtime/tmux/task records and Finance/LIFF/Supabase/Cloud Run/IAM/LINE/Sheets/production services.
```

- [ ] **Step 2: Run final focused verification**

Run:

```powershell
python codex/tests/test_shogun_ops_docs.py
python codex/tests/test_shogun_task_intake_docs.py
git diff --check 62b45fb2a2a5ec922d86e4ade9e63e8955613812..HEAD
git status --short
```

Expected: both test files pass, diff check is silent, and only the intended work-log change is uncommitted before the next step.

- [ ] **Step 3: Commit the work log**

```powershell
git add codex/work_log.md
git commit -m "docs(codex): record Shogun diagnostics relaxation"
```

- [ ] **Step 4: Perform spec and diff self-review**

Check all changed files for placeholders, contradictory diagnostic prerequisites, altered command vectors, broken paste fences, or broader runtime authority. Confirm the changed-file set is limited to the two policy documents, two focused tests, design, plan, and work log.

- [ ] **Step 5: Push and open a draft PR**

Push `agent/codex-shogun-diagnostics-relaxation` and open a draft PR targeting `main`. Include the focused test counts, explicit full-suite omission, retained safety boundaries, and the separate host-policy checkpoint.

- [ ] **Step 6: Obtain review and merge approval**

Require Critical 0 and Important 0 from focused review. If GitHub has no required checks, report that fact and obtain explicit user approval before merging.

- [ ] **Step 7: Atomically deploy the merged host policy**

After merge approval, derive the pasteable Custom Instructions text from the exact merged `workspace/main` commit, validate its diagnostics/Ops/intake markers and command vectors, back up the existing `C:\Users\jinnouchi\.codex\AGENTS.md`, and atomically replace it. Do not start Shogun or deliver a task in this checkpoint.

- [ ] **Step 8: Verify deployment and hand off the canary**

Verify only the installed host-policy hash and required marker/vector contract. In a fresh Codex task, run fixed Ops `status`; if allowed by the merged policy, start once when stopped, require healthy, and deliver the Finance planning task exactly once. The canary task remains a separate runtime action from this Workspace policy implementation.
