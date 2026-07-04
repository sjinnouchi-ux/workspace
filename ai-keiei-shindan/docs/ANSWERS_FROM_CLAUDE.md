# Answers From Claude

Date: 2026-07-04

Source document: https://docs.google.com/document/d/1G-4NcdUwYCbCcTNbGEeXmwEoOJ9WaT4gI9agMJUzWdY

## Summary

- Canonical content should come from `config.seed.json`.
- `config.seed.json` should be the single source for spreadsheet seeding and `FALLBACK_CONFIG`.
- The target spreadsheet is https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I
- GAS deployment should happen after canonical spreadsheet data is seeded.
- GitHub Pages should be enabled after data seeding, GAS verification, and `WEBAPP_URL` setup.

## Implementation Notes From Claude

- `q3b` uses explicit OR condition syntax: `{"$or":[{"q2":[...]},{"q3":[...]}]}`.
- `q6` and `q7` use computed flag syntax: `{"e_candidate": true}`.
- `convertEmployeeSize()` remains a fixed code-side table.
- `submissions` has a fixed header order and no salesperson/session ID columns.

## Current Evidence

The source document says `config.seed.json` and `docs/ai_keiei_shindan_app_spec.md` were provided or would be added, but as of this update they are not present in:

- GitHub branch `codex/ai-keiei-shindan-setup`
- Local checkout `C:\Users\irodo\Documents\workspace\ai-keiei-shindan`
- Google Drive search results for `config.seed.json`, `ai_keiei_shindan_app_spec`, and related project keywords

Do not infer question, choice, result, or result-step copy without `config.seed.json`.
