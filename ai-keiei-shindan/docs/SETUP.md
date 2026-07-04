# SETUP

Last updated: 2026-07-04

## Current Deployment State

- Google Sheets master/log file exists.
- Frontend and GAS code are prepared in Git.
- GAS has not been pushed or deployed.
- GitHub Pages has not been published.
- Question, choice, result, and result-step master data is not final because `ai_keiei_shindan_app_spec.md` is still pending.

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

Do not treat placeholder rows as final content. Fill the master data from `ai_keiei_shindan_app_spec.md` after Claude confirms the canonical source.

## GAS

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

- Claude confirms the logic spec source.
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

