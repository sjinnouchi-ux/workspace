# Specs

## Canonical Sources

| Source | Status | URL |
|---|---|---|
| `codex_kickoff_prompt.md` | Reviewed 2026-07-04 | https://docs.google.com/document/d/1307NeoqwpP1ANBMXgPAh7MphBp4NyiIllLARX3kW8GA |
| `ai_keiei_shindan_web_impl_spec.md` v0.4 | Reviewed 2026-07-04 | https://docs.google.com/document/d/1i0jF9gtzALP2Eyvsyd-JrXN-87_tq3YwV7Q8J6WF_4k |
| `ANSWERS_FROM_CLAUDE.md` | Reviewed 2026-07-05 | https://docs.google.com/document/d/1G-4NcdUwYCbCcTNbGEeXmwEoOJ9WaT4gI9agMJUzWdY |
| `config.seed.json` | Pending file body | Referenced by Claude, not found in branch or Drive search |
| `ai_keiei_shindan_app_spec.md` | Pending file body | Referenced by Claude, not found in branch or Drive search |
| Google Sheets master/log spreadsheet | Created 2026-07-04 | https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I |

## Implementation Gate

Do not fill canonical question, choice, result, or result-step copy until `config.seed.json` is available. Claude confirmed this JSON is the single source for spreadsheet seeding and `FALLBACK_CONFIG`.

The spreadsheet already exists, but it currently contains only headers, implementation placeholders, and source-status flags.

On 2026-07-05, Claude's answer was found in Drive, but the actual `config.seed.json` and `ai_keiei_shindan_app_spec.md` files were still not present in GitHub or Drive search results. Structural code may proceed; canonical content remains blocked until the JSON body is available.
