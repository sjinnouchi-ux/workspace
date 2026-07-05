# AI経営実装度診断WEBアプリ

経営者の前で営業マンが使う、AI実装度の限定URL診断アプリ。

## Current State

Initial implementation is published.

Before implementation, read both canonical specs:

1. `ai_keiei_shindan_app_spec.md`
2. `ai_keiei_shindan_web_impl_spec.md`

The web implementation spec v0.4 has been found. Claude's review answer is recorded in `docs/ANSWERS_FROM_CLAUDE.md`.

`config.seed.json` is now present and is the canonical source for questions, choices, results, result steps, spreadsheet seeding, and `index.html` `FALLBACK_CONFIG`. The Google Sheets master data has been seeded from it and verified for the canonical v1.2.0 row counts.

Current public app:

```text
https://sjinnouchi-ux.github.io/workspace/ai-keiei-shindan/
```

Current GAS Web App:

```text
https://script.google.com/macros/s/AKfycbxgaX2s8ly7NbotTH3V3Nys23kZKy2j48b6_ACQKPV3phyiXYzsx27RJK3yD6yBjzqfFQ/exec
```

Local `clasp` is not authenticated in this environment, so the confirmed GAS deployment route for the latest run was the Apps Script web editor.

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
