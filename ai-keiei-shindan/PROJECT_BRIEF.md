# AI経営実装度診断WEBアプリ Project Brief

Last updated: 2026-07-04

## Purpose

経営者の前で営業マンが提示し、AI実装度の現在地を会話につなげるための限定URL診断アプリを作る。

## Confirmed Stack

- Frontend: single `index.html` with embedded HTML/CSS/Vanilla JS.
- Backend: Google Apps Script Web App.
- Data: Google Sheets with `app_config`, `questions`, `choices`, `results`, `result_steps`, `submissions`.
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

A new Google Sheets master/log spreadsheet was created on 2026-07-04 with the required tabs and placeholder headers. Initial question, choice, result, and result copy data has not been filled because the kickoff document requires the logic spec as canonical source first. The web implementation spec v0.4 was found and reviewed. The logic spec `ai_keiei_shindan_app_spec.md` has not yet been found in Google Drive search results in this run.

## Source Links

- Kickoff prompt: https://docs.google.com/document/d/1307NeoqwpP1ANBMXgPAh7MphBp4NyiIllLARX3kW8GA
- Web implementation spec v0.4: https://docs.google.com/document/d/1i0jF9gtzALP2Eyvsyd-JrXN-87_tq3YwV7Q8J6WF_4k
- Logic spec: pending confirmation of `ai_keiei_shindan_app_spec.md`
- Google Sheets master/log spreadsheet: https://docs.google.com/spreadsheets/d/1wYT01OGL1-lKzzytLDJi8QIVimq61aVFrS88RIiCR0I
