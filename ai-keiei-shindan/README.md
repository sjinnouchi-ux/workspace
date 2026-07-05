# AI経営実装度診断WEBアプリ

経営者の前で営業マンが使う、AI実装度の限定URL診断アプリ。

## Current State

Project Git shell and structural implementation are ready.

Before implementation, read both canonical specs:

1. `ai_keiei_shindan_app_spec.md`
2. `ai_keiei_shindan_web_impl_spec.md`

The web implementation spec v0.4 has been found. Claude's review answer is recorded in `docs/ANSWERS_FROM_CLAUDE.md`.

`config.seed.json` is now present and is the canonical source for questions, choices, results, result steps, spreadsheet seeding, and `index.html` `FALLBACK_CONFIG`. The Google Sheets master data has been seeded from it and verified for the canonical row counts.

Current blocker: GAS has not been pushed or deployed from this local environment because `clasp` is not authenticated or linked to an Apps Script project here. `WEBAPP_URL` remains blank until the deployed `/exec` URL is available.

## Planned Structure

```text
ai-keiei-shindan/
├─ index.html
├─ gas/
│  ├─ Code.gs
│  └─ appsscript.json
├─ docs/
│  ├─ specs/
│  └─ SETUP.md
├─ tests/
│  └─ logic.test.js
└─ README.md
```

## Local Verification

```powershell
node tests/logic.test.js
```

## Current Report

- Implementation completion summary: `docs/reports/2026-07-05-implementation-completion-summary.md`
