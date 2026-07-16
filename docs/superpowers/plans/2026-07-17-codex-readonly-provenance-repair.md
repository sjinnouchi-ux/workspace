# Codex Read-Only Diagnostics Provenance Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every Codex Desktop policy resolve the schema-version-1 deployment registry from its single canonical GitHub repository without relying on an ambiguous relative path.

**Architecture:** Keep the deployment registry only in `sjinnouchi-ux/multi-agent-shogun`. Update the two `sjinnouchi-ux/workspace` policy documents to use the complete raw URL, record the repair, and independently verify HTTP availability, registry cardinality, source hash, and the deployment-host snapshot.

**Tech Stack:** GitHub Markdown, PowerShell 5.1 validation, Git, WSL2 Ubuntu fixed diagnostics snapshot.

## Global Constraints

- Do not duplicate the deployment registry into `sjinnouchi-ux/workspace`.
- Do not read or display secrets, tmux panes, raw queues, raw reports, raw logs, or raw diagnostic JSON.
- Do not use shortened WSL, Bash, Python, repository-script, or direct-runtime-read fallbacks.
- The only eligible diagnostic argv remains the complete fixed command documented in the policy.

---

### Task 1: Repair the canonical registry reference

**Files:**
- Modify: `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`
- Modify: `codex/CODEX_DESKTOP_STARTUP.md`
- Modify: `codex/work_log.md`

**Interfaces:**
- Consumes: the active registry on `sjinnouchi-ux/multi-agent-shogun` `main`
- Produces: an unambiguous complete raw URL in both Codex policy sources

- [x] **Step 1: Reproduce the failure**

  Verify that both policy files lack the complete canonical URL and that the inferred `sjinnouchi-ux/workspace` raw URL returns HTTP 404.

- [x] **Step 2: Apply the minimal policy change**

  Replace only the relative registry path with:

  `https://raw.githubusercontent.com/sjinnouchi-ux/multi-agent-shogun/main/docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md`

- [x] **Step 3: Record the root cause and non-changes**

  Append a sanitized work-log entry. State that the registry remains solely in `multi-agent-shogun` and that no Shogun runtime data or secret was read.

- [x] **Step 4: Verify policy regression checks**

  Require the complete URL exactly once in each policy file, validate the marked registry has schema version 1 and exactly one active deployment, and run `git diff --check`.

- [ ] **Step 5: Publish for review**

  Commit on a dedicated `codex/*` branch, push, open a PR to `main`, independently review it, and merge only after approval.

### Task 2: Synchronize and verify the deployment host

**Files:**
- Update after merge: real-user `C:\Users\jinnouchi\.codex\AGENTS.md`
- Verify only: `/home/jinnouchi/.local/libexec/shogun-codex-diagnostics`

**Interfaces:**
- Consumes: merged workspace policy and the active deployment record
- Produces: sanitized mode/hash/availability evidence

- [ ] **Step 1: Synchronize the local global instruction**

  Replace the same relative path in the marked block with the complete canonical URL. Make no unrelated changes.

- [ ] **Step 2: Verify snapshot metadata**

  At the real Windows user boundary, confirm the fixed snapshot exists, is mode `0555`, and hashes to the active registry source SHA-256 without reading its contents into Codex output.

- [ ] **Step 3: Run the fixed diagnostic once**

  Only after provenance is trusted, run the complete fixed argv, validate exit/stderr/duration/schema/invariants, and report sanitized summary fields only.

- [ ] **Step 4: Report the safe SUUMO continuation**

  State whether Codex may resume Shogun orchestration for `shogun/implementation-mvp`.

