# AI経営実装度診断WEBアプリ Project Brief

Last updated: 2026-07-05

## Purpose

経営者の前で営業マンが提示し、AI実装度の現在地を会話につなげるための限定URL診断アプリを作る。

## Confirmed Stack

- Frontend: single `index.html` with embedded HTML/CSS/Vanilla JS.
- Backend: Google Apps Script Web App.
- Data: Google Sheets with `app_config`, `questions`, `choices`, `results`, `result_steps`, `submissions`, `submission_answer_labels`.
- Hosting: GitHub Pages with `<meta name="robots" content="noindex">`.
- Account for Google-side work: `s.jinnouchi@yumekango.com`.

## Core Constraints

- No external framework or CDN dependency.
- No login or password protection in the initial scope.
- No pricing, booking, inquiry, email capture, sales plan recommendation, YouTube embed, or inline article body in the initial scope.
- Article steps are external-link cards only.
- Result pages are driven by `result_steps`; code should render configured steps, not hard-code result copy except fallback config.
- Theme values must be centralized in a `:root` design-token block.

## Current Status

Project shell was created in Git on 2026-07-04.

A new Google Sheets master/log spreadsheet was created on 2026-07-04 with the required tabs. A structural frontend/GAS implementation has also been prepared.

Claude's review answer was found on 2026-07-05 and confirms that `config.seed.json` is the single source for question, choice, result, and result-step data. On 2026-07-05, `config.seed.json` and `docs/ai_keiei_shindan_app_spec.md` were fetched from Google Drive, committed to the branch, and the spreadsheet master data was seeded from `config.seed.json`.

GAS Web App v2 was deployed from the Apps Script web editor on 2026-07-05, and `/config` was verified against `config.seed.json` with stable object-key ordering.

## Source Links

- Kickoff prompt: https://docs.google.com/document/d/1307NeoqwpP1ANBMXgPAh7MphBp4NyiIllLARX3kW8GA
- Web implementation spec v0.4: https://docs.google.com/document/d/1i0jF9gtzALP2Eyvsyd-JrXN-87_tq3YwV7Q8J6WF_4k
- Claude answer: https://docs.google.com/document/d/1G-4NcdUwYCbCcTNbGEeXmwEoOJ9WaT4gI9agMJUzWdY
- Config seed: `config.seed.json`
- Logic spec: `docs/ai_keiei_shindan_app_spec.md`
- Google Sheets master/log spreadsheet: https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I
- GAS Web App: https://script.google.com/macros/s/AKfycbxgaX2s8ly7NbotTH3V3Nys23kZKy2j48b6_ACQKPV3phyiXYzsx27RJK3yD6yBjzqfFQ/exec

## Current Implementation Artifacts

- `index.html`: standalone frontend shell and data-driven engine.
- `gas/Code.gs`: GAS config and submission API.
- `gas/appsscript.json`: GAS manifest.
- `tests/logic.test.js`: Node logic tests.
- `docs/SETUP.md`: deployment and operation notes.
- `docs/QUESTIONS_FOR_CLAUDE.md`: confirmation items before data fill/deploy.
- `docs/ANSWERS_FROM_CLAUDE.md`: Claude answer pointer and implementation summary.
- `config.seed.json`: canonical data source.
- `docs/ai_keiei_shindan_app_spec.md`: human-readable logic spec.
- `docs/reports/2026-07-05-implementation-completion-summary.md`: initial implementation completion summary and next-task notes.
