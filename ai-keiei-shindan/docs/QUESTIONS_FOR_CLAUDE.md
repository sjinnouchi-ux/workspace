# Questions For Claude

Last updated: 2026-07-05

Codex has implemented the generic frontend engine, GAS API, setup document, and logic tests as far as possible without inventing canonical content.

## Claude Answer Received

Claude answered in this Drive document:

- https://docs.google.com/document/d/1G-4NcdUwYCbCcTNbGEeXmwEoOJ9WaT4gI9agMJUzWdY

Resolved answers:

- `config.seed.json` is the canonical source for spreadsheet seeding and `FALLBACK_CONFIG`.
- Fill the existing spreadsheet from `config.seed.json`.
- Deploy GAS only after canonical spreadsheet data is filled.
- Enable GitHub Pages only after data seeding, GAS verification, and frontend `WEBAPP_URL` setup.

## Remaining Blocker

`config.seed.json` and `docs/ai_keiei_shindan_app_spec.md` are still not available in the GitHub branch, local checkout, or Google Drive search results as of this update.

Needed file:

- `config.seed.json` with questions 9, choices 37, results 5, and result_steps 20.

Do not infer canonical question, choice, result, or result-step copy without that JSON body.

## Implemented Without Further Design Input

- Standalone `index.html`.
- Theme-token block in `:root`.
- Top, employee size, question, result intro, and result step views.
- Config fetch with fallback.
- Frontend flow state.
- Branch evaluation from `display_condition_json`.
- `convertEmployeeSize()`.
- `isECandidate()`.
- `computeResult()`.
- `buildResultSteps()`.
- `text` and external-link `article` result steps.
- Unknown result step types are skipped.
- URL-less article steps are skipped.
- `/submit` sends `text/plain`.
- Pending submissions are stored for retry.
- GAS `doGet` config API.
- GAS `doPost` submit API.
- `submission_id` idempotence.
- GAS `seedSheetsFromJson(jsonText, preserveSubmissions)`.
- GAS `seedSheetsFromScriptProperty()`.
- Node logic tests.
