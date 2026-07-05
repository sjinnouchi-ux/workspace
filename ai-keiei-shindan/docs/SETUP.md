# SETUP

Last updated: 2026-07-05

## Current Deployment State

- Google Sheets master/log file exists.
- Frontend and GAS code are prepared in Git.
- `config.seed.json` and `docs/ai_keiei_shindan_app_spec.md` are present in Git.
- Spreadsheet master data has been seeded from `config.seed.json`.
- GAS has not been pushed or deployed.
- GitHub Pages has not been published.
- `index.html` `FALLBACK_CONFIG` is synced with `config.seed.json`.

## Google Sheets

Spreadsheet:

```text
https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I
```

Tabs:

- `app_config`
- `questions`
- `choices`
- `results`
- `result_steps`
- `submissions`
- `_README`

The master data was seeded from `config.seed.json` on 2026-07-05 and verified with these data-row counts:

- `questions`: 9
- `choices`: 37
- `results`: 5
- `result_steps`: 20

`submissions` has the Claude-confirmed header order and no data rows were present before reseeding.

## Seeding From `config.seed.json`

GAS includes two reproducible seed helpers:

- `seedSheetsFromJson(jsonText, preserveSubmissions)`
- `seedSheetsFromScriptProperty()`

Recommended reproducible flow:

1. Paste the JSON body into Apps Script project property `CONFIG_SEED_JSON`.
2. Run `seedSheetsFromScriptProperty()`.
3. Confirm returned counts:
   - `questions: 9`
   - `choices: 37`
   - `results: 5`
   - `result_steps: 20`
4. Confirm the spreadsheet tabs have the same data-row counts.
5. Clear or avoid storing the JSON anywhere secret-bearing. The seed is content data, not credentials, but the GitHub copy should still be the durable source.

## GAS

Current local blocker:

- `clasp` is not authenticated in this Windows environment.
- `ai-keiei-shindan/.clasp.json` is not present, so the local checkout is not linked to an Apps Script project.
- GAS push/deploy and live `/config` verification must be completed after authenticating/linking `clasp` with `s.jinnouchi@yumekango.com`, or by using another authenticated Apps Script deployment route.

Source files:

- `gas/Code.gs`
- `gas/appsscript.json`

Deploy requirements:

1. Use `s.jinnouchi@yumekango.com`.
2. Create or attach a GAS project.
3. Push `gas/Code.gs` and `gas/appsscript.json` with `clasp`.
4. Deploy as Web App.
5. Access: anyone.
6. Copy the `/exec` URL.
7. Put that URL in `index.html` as `WEBAPP_URL`.
8. Redeploy a new Web App version after every GAS code change.

POST from the frontend must use:

```text
Content-Type: text/plain
```

This avoids a GAS CORS preflight failure.

## Frontend

Source file:

```text
index.html
```

The file is intentionally standalone. It has no build step and no external libraries.

Before publishing, confirm:

- `WEBAPP_URL` is set to the deployed GAS `/exec` URL.
- `<meta name="robots" content="noindex">` remains present.
- No secrets or `.env` values are embedded.
- The app still passes `node tests/logic.test.js`.

## GitHub Pages

Initial target:

```text
https://sjinnouchi-ux.github.io/workspace/ai-keiei-shindan/
```

Publish only after:

- `config.seed.json` is present in GitHub and used to seed the spreadsheet.
- Spreadsheet master data is filled.
- GAS Web App is deployed.
- Frontend has the GAS `/exec` URL.
- Logic tests pass.
- A 375px width browser check passes.

## Article Step Rules

`result_steps.type = article` is external-link only in the initial scope.

- Use `headline` as the article title.
- Use `url` for the external article URL.
- Use `link_label`, or leave it blank to show the default article button text.
- Do not use booking pages, price pages, inquiry forms, or email capture pages as article URLs.
