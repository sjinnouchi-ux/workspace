# Questions For Claude

Last updated: 2026-07-04

Codex has implemented the generic frontend engine, GAS API, setup document, and logic tests as far as possible without inventing canonical content.

## Blocking Questions

1. Where is the canonical `ai_keiei_shindan_app_spec.md`?
   - Needed for question text.
   - Needed for choices and choice metadata.
   - Needed for result phase names and headlines.
   - Needed for the 20 initial `result_steps` text rows.

2. Should the existing Google Sheets file be filled directly after that spec is confirmed?
   - Spreadsheet URL: https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I

3. Should Codex deploy GAS before final master data is filled?
   - Recommendation from implementation side: no. Deploy after the master data is confirmed, to avoid testing against placeholder rows.

4. Should GitHub Pages be enabled from `sjinnouchi-ux/workspace` for `/ai-keiei-shindan/` after data and GAS are ready?
   - The web implementation spec says GitHub Pages noindex limited URL is the initial hosting path.

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
- Node logic tests.

