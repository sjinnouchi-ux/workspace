# Codex Shogun Diagnostics Relaxation Design

## Context

The deployed fixed Shogun Ops wrapper already provides sanitized `status`, `start`, `restart-agent`, `restart-all`, and `deliver` operations. However, `CODEX_SHOGUN_TASK_INTAKE_V1` still requires the legacy fixed diagnostics contract before every delivery, while `CODEX_SHOGUN_OPS_V1` says that the deployed Ops wrapper requires no per-call GitHub registry or source-hash lookup. A Codex task therefore returned to the legacy diagnostic path and was rejected by a circular pre-execution check: it was asked to compare the registry hash with `tool.source_sha256` before the tool had returned that field.

The environment is private and the user explicitly approved removing per-invocation GitHub registry and source-hash verification from both the legacy diagnostic flow and the Ops flow.

## Decision

For an explicit Shogun operation or task delivery, the deployed fixed Ops wrapper is the canonical runtime control surface. Codex runs the exact fixed `shogun-codex-ops status` vector first. It does not invoke the legacy `shogun-codex-diagnostics summary` command as an additional prerequisite. A single delivery is permitted only when the sanitized Ops status is `healthy` and the existing new/resume/ambiguous intake guard allows delivery.

Direct requests for the legacy fixed diagnostic command remain supported, but they no longer fetch or validate the GitHub deployment registry and no longer compare a registry source hash with `tool.source_sha256`. The installed mode-`0555` snapshot and host policy are the trust checkpoint.

## Retained Boundaries

The relaxation removes only per-call GitHub provenance work. It does not broaden executable permissions.

- Only the existing complete fixed argv vectors are permitted.
- Shorter `wsl.exe`, shell, Python, repo-script, arbitrary-path, suffix, and environment prefixes remain forbidden.
- Diagnostics and Ops results must exit successfully, return their documented sanitized ASCII JSON contract, and have empty stderr.
- Schema, key order, enums, cardinality, cross-field invariants, and recomputed health remain validated before fields are trusted.
- The 10-second process limit for the legacy diagnostic command remains.
- Raw queue, report, log, pane, task-body, secret, environment, and personal-identifier reads remain forbidden.
- Failure never falls back to raw runtime inspection or automatic repair.
- `restart-all` still requires explicit approval for each invocation.

## Document Precedence

`CODEX_SHOGUN_TASK_INTAKE_V1` will explicitly route deployed operation and delivery requests to `CODEX_SHOGUN_OPS_V1 status`. It will state that legacy diagnostics must not be run first or in parallel when the Ops wrapper is the selected control surface.

`CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1` will remove the registry fetch, active-deployment cardinality check, and source-hash comparison requirements. Its remaining fixed-command, output-validation, timeout, privacy, and fail-closed rules stay intact.

The same semantics must appear in both:

- `codex/CODEX_DESKTOP_STARTUP.md`
- the pasteable block in `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`

## Verification

Focused document contract tests will prove that:

1. task intake selects Ops `status` for deployed operation and delivery workflows;
2. task intake forbids a legacy-diagnostics prerequisite when Ops is selected;
3. neither Startup nor Custom Instructions requires a per-call registry fetch, active-deployment check, or registry-to-tool source-hash comparison;
4. the five exact Ops vectors and the one exact legacy diagnostic vector remain unchanged;
5. sanitized schema/invariant validation, timeout, privacy, raw-fallback prohibition, and `restart-all` approval remain present;
6. the Custom Instructions pasteable fence remains intact; and
7. existing task-intake contract tests continue to pass.

Only the focused Shogun Ops and task-intake document tests plus `git diff --check` are required. The full workspace suite is out of scope because no runtime, queue schema, launcher, watcher, or recovery code changes.

## Deployment and Rollback

After review and merge to `workspace/main`, the real Windows user host policy is atomically updated from the merged Custom Instructions pasteable text. A fresh Codex task must load the new policy before using it.

Rollback reverts the Workspace policy commit and atomically restores the previous host policy. The installed Shogun Ops snapshot and runtime task records are not changed by this policy-only rollback.

## Non-goals

- No Shogun runtime start, restart, repair, or task delivery in this policy change.
- No modification to the Shogun Ops or legacy diagnostics executable snapshots.
- No raw runtime inspection.
- No change to Finance, LIFF, Supabase, Cloud Run, IAM, LINE, Google Sheets, or production services.
