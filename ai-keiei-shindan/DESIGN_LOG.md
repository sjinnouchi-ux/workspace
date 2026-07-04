# DESIGN_LOG

## 2026-07-04 Project intake

Source reviewed:

- `codex_kickoff_prompt.md`
  - Google Docs ID: `1307NeoqwpP1ANBMXgPAh7MphBp4NyiIllLARX3kW8GA`
- `ai_keiei_shindan_web_impl_spec.md` v0.4
  - Google Docs ID: `1i0jF9gtzALP2Eyvsyd-JrXN-87_tq3YwV7Q8J6WF_4k`

Confirmed from the kickoff prompt:

- This project should live under `sjinnouchi-ux/workspace` as `ai-keiei-shindan/`.
- The implementation owner is Codex.
- The design owner is Claude / Opus 4.8.
- Required canonical specs before implementation:
  - `ai_keiei_shindan_app_spec.md`
  - `ai_keiei_shindan_web_impl_spec.md`
- Stop at explicit confirmation points in the kickoff prompt.

Confirmed from the web implementation spec v0.4:

- Single-file frontend: `index.html` with HTML/CSS/Vanilla JS.
- Backend/data: Google Apps Script + Google Sheets.
- Hosting: GitHub Pages noindex limited URL.
- Results must be rendered from `result_steps`.
- Theme values must be centralized in `:root` design tokens.
- `result_intro` is required between the final answer and the first result step.
- Article steps are external-link style only in the initial scope.
- Salesperson ID is not implemented in the initial scope.

Open design dependency:

- `ai_keiei_shindan_app_spec.md` was not found by Drive searches for `ai_keiei_shindan_app_spec`, `ai_keiei`, `AI経営実装度診断`, and `ロジック仕様書` in this run. Implementation should not begin until this logic spec is provided or its location is confirmed.

