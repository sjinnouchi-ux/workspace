# Codex Turn-Ended LINE Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an OIDC-protected kakeibo-api endpoint that sends a fixed Codex turn-ended message to existing enabled management-notification subscribers without changing LIFF, webhook, Worker, or Cloud Run public IAM behavior.

**Architecture:** A dedicated FastAPI router validates a strict versioned payload and a Google-signed ID token for one impersonated notifier service account. A focused service reuses the existing subscriber sheet and LINE client, records event IDs in a separate dispatch sheet, and generates the LINE text server-side. The existing public `kakeibo-api` service remains public; only the new route performs application-layer OIDC authorization.

**Tech Stack:** Python 3.13, FastAPI 0.115.6, Pydantic Settings 2.7.1, google-auth 2.37.0, httpx 0.28.1, Google Sheets API, LINE Messaging API, pytest 8.3.4, Cloud Run, gcloud.

## Global Constraints

- Use a task-specific `sjinnouchi-ux/kakeibo-liff` clone/worktree based on current GitHub `main`.
- Read all repo startup and Primary Docs before editing. Do not edit Claude/FABLE-owned `DESIGN.md`.
- Keep Cloud Run public IAM, `--allow-unauthenticated`, Worker, LIFF, webhook, GAS, and Phase 3 Stage B unchanged.
- Protect only `POST /internal/codex/turn-ended/notify` with application-layer Google OIDC validation.
- Never store or print LINE tokens, LINE user IDs, OAuth/ID tokens, service-account JSON, raw session/turn IDs, transcripts, prompts, cwd, or models.
- Reuse `_management_notification_subscribers`; store event IDs only in `_codex_turn_notification_dispatches`.
- Production constants: project `kakeibo-liff-prod`, region `asia-northeast1`, service `kakeibo-api`, audience `https://kakeibo-api-570965759130.asia-northeast1.run.app`, notifier `codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com`.
- Google credential owner is `s.jinnouchi@yumekango.com`. Isolated-user failures are `INCONCLUSIVE` until checked at the real Windows-user boundary.
- No IAM write, deploy, live request, or LINE Push before a separate explicit approval checkpoint.
- Use TDD and commit after each independently testable task.

---

## File Map

- Create `api/app/services/codex_notifications.py`: fixed message, subscriber lookup, deduplication, delivery, dispatch recording.
- Create `api/app/routers/codex_notifications.py`: strict request schema, OIDC verification, endpoint.
- Create `api/tests/test_codex_notifications.py`: domain, auth, validation, deduplication, regression tests.
- Modify `api/app/services/notifications.py`: expose shared subscriber lookup without behavior changes.
- Modify `api/app/config.py`: add notifier email and subject settings.
- Modify `api/app/main.py`: include the router.
- Create `docs/codex-turn-line-notifications.md`; modify `docs/secret-management.md` and `IMPLEMENTATION_LOG.md`.

### Task 1: Notification Domain Service

**Files:**
- Create: `api/app/services/codex_notifications.py`
- Modify: `api/app/services/notifications.py`
- Test: `api/tests/test_codex_notifications.py`

**Interfaces:**
- Consumes: `SheetsService.get_values`, `ensure_sheet`, `append_first_empty_row_by_columns`, and `LineClient.push`.
- Produces: `enabled_management_notification_subscribers(sheets)`, `build_codex_turn_message(ended_at, host_label)`, and `CodexTurnNotificationService.dispatch(...)`.

- [ ] **Step 1: Write failing service tests**

Add fake Sheets/LINE objects following `api/tests/test_notifications.py`. Assert the exact message:

```python
def test_build_codex_turn_message_is_fixed_and_minimal():
    text = build_codex_turn_message(
        datetime(2026, 7, 17, 14, 32, tzinfo=ZoneInfo("Asia/Tokyo")),
        "NUCBOX_K8_PLUS",
    )
    assert text == (
        "Codexのターンが終了しました\n"
        "端末: NUCBOX_K8_PLUS\n"
        "時刻: 2026-07-17 14:32"
    )
```

Add tests for `sent`, `deduplicated`, `no_subscribers`, disabled subscribers, header `['event_id', 'sent_at']`, and LINE failure leaving the dispatch sheet unchanged.

- [ ] **Step 2: Verify RED**

Run `Set-Location api; python -m pytest tests/test_codex_notifications.py -q`.
Expected: collection fails because `app.services.codex_notifications` is absent.

- [ ] **Step 3: Extract shared subscriber lookup**

Add to `services/notifications.py`:

```python
def enabled_management_notification_subscribers(sheets: SheetsService) -> list[str]:
    rows = sheets.get_values(f"{SUBSCRIBERS_SHEET_NAME}!A2:C")
    return [
        str(row[0])
        for row in rows
        if row and str(row[0]).strip()
        and _is_true(row[1] if len(row) > 1 else False)
    ]
```

Make the existing `enabled_subscribers()` return this function. Do not alter sheet names or commands.

- [ ] **Step 4: Implement the focused service**

Create constants and class:

```python
DISPATCHES_SHEET_NAME = "_codex_turn_notification_dispatches"

@dataclass
class CodexTurnNotificationService:
    sheets: SheetsService
    line: LineClient
    timezone: str = "Asia/Tokyo"

    def dispatch(self, *, event_id: str, ended_at: datetime, host_label: str) -> dict[str, object]:
        self.sheets.ensure_sheet(DISPATCHES_SHEET_NAME, header=["event_id", "sent_at"])
        rows = self.sheets.get_values(f"{DISPATCHES_SHEET_NAME}!A2:B")
        if any(row and str(row[0]) == event_id for row in rows):
            return {"status": "deduplicated", "sent": False, "subscriber_count": 0}
        subscribers = enabled_management_notification_subscribers(self.sheets)
        if not subscribers:
            return {"status": "no_subscribers", "sent": False, "subscriber_count": 0}
        message = {"type": "text", "text": build_codex_turn_message(ended_at, host_label)}
        for user_id in subscribers:
            self.line.push(user_id, [message])
        self.sheets.append_first_empty_row_by_columns(
            spreadsheet="main", sheet_name=DISPATCHES_SHEET_NAME,
            scan_range="A2:A", start_row=2,
            values=[event_id, datetime.now(ZoneInfo(self.timezone)).strftime("%Y/%m/%d %H:%M")],
        )
        return {"status": "sent", "sent": True, "subscriber_count": len(subscribers)}
```

Implement the message using `ended_at.astimezone(ZoneInfo('Asia/Tokyo'))`. Add a cached dependency factory using existing Sheets and LINE factories.

- [ ] **Step 5: Verify GREEN and regression**

Run `python -m pytest tests/test_codex_notifications.py tests/test_notifications.py tests/test_webhook.py -q` from `api`.
Expected: all selected tests pass.

- [ ] **Step 6: Commit**

```powershell
git add api/app/services/codex_notifications.py api/app/services/notifications.py api/tests/test_codex_notifications.py
git commit -m "feat: add Codex turn notification service"
```

### Task 2: Strict OIDC Router

**Files:**
- Create: `api/app/routers/codex_notifications.py`
- Modify: `api/app/config.py`, `api/app/main.py`, `api/tests/test_codex_notifications.py`

**Interfaces:**
- Consumes: `CodexTurnNotificationService.dispatch`.
- Produces: endpoint and settings `codex_turn_notification_sender_service_account` / `codex_turn_notification_sender_subject`.

- [ ] **Step 1: Add failing auth/validation tests**

Cover missing bearer, invalid token, wrong issuer/email/subject, `email_verified=False`, unknown `task_name`, malformed event ID, naive datetime, and allowed sender. Valid claims are:

```python
{
    "iss": "https://accounts.google.com",
    "aud": "https://kakeibo-api-570965759130.asia-northeast1.run.app",
    "email": "codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com",
    "email_verified": True,
    "sub": "123456789012345678901",
}
```

- [ ] **Step 2: Verify RED**

Run `python -m pytest tests/test_codex_notifications.py -q` from `api`.
Expected: missing router/settings failures.

- [ ] **Step 3: Add non-secret settings**

Add two empty-string fields and include them in the existing BOM/whitespace validator:

```python
codex_turn_notification_sender_service_account: str = ""
codex_turn_notification_sender_subject: str = ""
```

- [ ] **Step 4: Implement strict models and authorization**

Use `ConfigDict(extra='forbid')`, `Literal[1]`, event pattern `^[0-9a-f]{64}$`, timezone-aware datetime validation, and host pattern `^[A-Za-z0-9_-]{1,64}$`.

`require_codex_turn_notifier` must call `verify_oauth2_token` with `settings.cloud_run_service_url`, accept issuer only from `accounts.google.com` and `https://accounts.google.com`, require verified email, exact configured email, and exact subject. Return 503 for missing configuration, 401 for token/audience/issuer failure, and 403 for principal mismatch.

- [ ] **Step 5: Add the endpoint and register router**

```python
@router.post("/internal/codex/turn-ended/notify")
def notify_codex_turn_ended(body, service=Depends(...), settings=Depends(...), authorization=Header(None)):
    require_codex_turn_notifier(authorization, settings)
    return service.dispatch(event_id=body.event_id, ended_at=body.ended_at, host_label=body.host_label)
```

Import and include this router in `main.py` without changing current routers.

- [ ] **Step 6: Verify focused and full suites**

Run `python -m pytest tests/test_codex_notifications.py -q` then `python -m pytest -q`.
Expected: both pass with no new failures.

- [ ] **Step 7: Commit**

```powershell
git add api/app/config.py api/app/main.py api/app/routers/codex_notifications.py api/tests/test_codex_notifications.py
git commit -m "feat: protect Codex turn notification endpoint"
```

### Task 3: Documentation and Code PR

**Files:**
- Create: `docs/codex-turn-line-notifications.md`
- Modify: `docs/secret-management.md`, `IMPLEMENTATION_LOG.md`

- [ ] **Step 1: Document endpoint, payload, message, subscriber reuse, dispatch sheet, exact identity/audience, rollback, and the unchanged public Cloud Run boundary.**
- [ ] **Step 2: Document only non-secret env names:** `CLOUD_RUN_SERVICE_URL`, `CODEX_TURN_NOTIFICATION_SENDER_SERVICE_ACCOUNT`, `CODEX_TURN_NOTIFICATION_SENDER_SUBJECT`. State that no key JSON is permitted.
- [ ] **Step 3: Run full verification:** `python -m pytest -q`, `python -m compileall app tests`, `node --check worker/worker.js`, `git diff --check`.
- [ ] **Step 4: Record base SHA, branch, files, exact test counts, and that IAM/deploy/live are unperformed.**
- [ ] **Step 5: Commit docs, push, and open a Draft PR. Review and merge before deployment.**

### Task 4: Identity, Deployment, and Live Verification

**Files:**
- Modify after verification: `IMPLEMENTATION_LOG.md`, `docs/codex-turn-line-notifications.md`

- [ ] **Step 1: Read-only production preflight**

Set exact variables and inspect active account, service, and IAM policy. Hash the policy; do not print credentials.

```powershell
$ProjectId="kakeibo-liff-prod"; $Region="asia-northeast1"; $Service="kakeibo-api"
$ServiceUrl="https://kakeibo-api-570965759130.asia-northeast1.run.app"
$NotifierSa="codex-turn-notifier@$ProjectId.iam.gserviceaccount.com"
$CallerUser="s.jinnouchi@yumekango.com"
gcloud auth list --filter="status:ACTIVE" --format="value(account)"
gcloud run services describe $Service --project $ProjectId --region $Region --format="yaml(metadata.name,status.url,spec.template.spec.serviceAccountName)"
gcloud run services get-iam-policy $Service --project $ProjectId --region $Region --format=json
$PreDeployRevision=gcloud run services describe $Service --project $ProjectId --region $Region --format="value(status.latestReadyRevisionName)"
```

- [ ] **Step 2: Obtain explicit production approval** for exactly: create notifier SA + token-creator binding, deploy two non-secret env values. State that public IAM, Invoker, Worker, LIFF, webhook, GAS, and secrets stay unchanged.

- [ ] **Step 3: Create identity and only impersonation IAM**

```powershell
gcloud iam service-accounts create codex-turn-notifier --project $ProjectId --display-name "Codex Desktop turn notifier"
gcloud iam service-accounts add-iam-policy-binding $NotifierSa --project $ProjectId --member "user:$CallerUser" --role "roles/iam.serviceAccountTokenCreator"
$NotifierSubject = gcloud iam service-accounts describe $NotifierSa --project $ProjectId --format="value(uniqueId)"
```

Do not grant Run Invoker, Secret Manager, Sheets, or project-wide roles.

- [ ] **Step 4: Deploy from merged clean main while preserving public behavior**

Run the established source deployment with the existing runtime identity and secret references:

```powershell
gcloud run deploy $Service `
  --project $ProjectId `
  --source .\api `
  --region $Region `
  --service-account "kakeibo-api-sa@$ProjectId.iam.gserviceaccount.com" `
  --allow-unauthenticated `
  --min-instances 0 `
  --set-secrets "LINE_CHANNEL_ACCESS_TOKEN=LINE_CHANNEL_ACCESS_TOKEN:latest,LINE_CHANNEL_SECRET=LINE_CHANNEL_SECRET:latest,SPREADSHEET_ID=SPREADSHEET_ID:latest,EXPENSE_SS_ID=EXPENSE_SS_ID:latest" `
  --update-env-vars "CLOUD_RUN_SERVICE_URL=$ServiceUrl,CODEX_TURN_NOTIFICATION_SENDER_SERVICE_ACCOUNT=$NotifierSa,CODEX_TURN_NOTIFICATION_SENDER_SUBJECT=$NotifierSubject"
```

Re-hash IAM afterward; it must match pre-deploy.

- [ ] **Step 5: Smoke test safely**

Unauthenticated request must return 401. Mint token into a variable, never output it:

```powershell
$IdToken = & gcloud auth print-identity-token --impersonate-service-account=$NotifierSa --audiences=$ServiceUrl --include-email 2>$null
if ([string]::IsNullOrWhiteSpace($IdToken)) { throw "OIDC token mint failed" }
$EventId=([guid]::NewGuid().ToString("N")+[guid]::NewGuid().ToString("N")).ToLowerInvariant()
$Body=@{schema_version=1;event_id=$EventId;ended_at=[DateTimeOffset]::Now.ToString("o");host_label="NUCBOX_K8_PLUS"}|ConvertTo-Json -Compress
$Headers=@{Authorization="Bearer $IdToken"}
$First=Invoke-RestMethod -Method Post -Uri "$ServiceUrl/internal/codex/turn-ended/notify" -Headers $Headers -ContentType "application/json" -Body $Body
$Second=Invoke-RestMethod -Method Post -Uri "$ServiceUrl/internal/codex/turn-ended/notify" -Headers $Headers -ContentType "application/json" -Body $Body
$IdToken=$null
```

Expected: first `sent`, user confirms one LINE, second `deduplicated`.

- [ ] **Step 6: Verify non-regression:** health, Worker HTML/categories, secret-safe signed webhook, management warning, and unchanged IAM.
- [ ] **Step 7: Prepare and verify rollback without executing it after a successful release.** Record `$PreDeployRevision`; if any acceptance check fails, restore traffic with `gcloud run services update-traffic $Service --project $ProjectId --region $Region --to-revisions "$PreDeployRevision=100"`, remove the user token-creator binding with `gcloud iam service-accounts remove-iam-policy-binding`, and confirm public IAM still matches the original hash.
- [ ] **Step 8: Record revision, timestamps, tests, receipt, dedup, IAM hash equality, rollback target, and unchanged routes; commit/push through review.**
