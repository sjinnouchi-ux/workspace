# Specs

## Canonical Sources

| Source | Status | URL |
|---|---|---|
| `codex_kickoff_prompt.md` | Reviewed 2026-07-04 | https://docs.google.com/document/d/1307NeoqwpP1ANBMXgPAh7MphBp4NyiIllLARX3kW8GA |
| `ai_keiei_shindan_web_impl_spec.md` v0.4 | Reviewed 2026-07-04 | https://docs.google.com/document/d/1i0jF9gtzALP2Eyvsyd-JrXN-87_tq3YwV7Q8J6WF_4k |
| `ANSWERS_FROM_CLAUDE.md` | Reviewed 2026-07-05 | https://docs.google.com/document/d/1G-4NcdUwYCbCcTNbGEeXmwEoOJ9WaT4gI9agMJUzWdY |
| `config.seed.json` | Added 2026-07-05; canonical seed | Drive file ID `1riiZgv694hymqgmqMOJe3IP6vo3PuNWR` |
| `ai_keiei_shindan_app_spec.md` | Added 2026-07-05; human-readable logic spec | Drive file ID `1HVKYX8Z9V0hXXtR8Y-jNVyaf0SxWH87u` |
| Google Sheets master/log spreadsheet | Created 2026-07-04; seeded 2026-07-05 | https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I |

## Implementation Gate

Do not infer canonical question, choice, result, or result-step copy. Claude confirmed `config.seed.json` is the single source for spreadsheet seeding and `FALLBACK_CONFIG`.

The spreadsheet exists and has been seeded from `config.seed.json`.

On 2026-07-05, the seeded row counts were confirmed as `questions=9`, `choices=37`, `results=5`, and `result_steps=20`.
