# Codex Startup Guide

This repository is the GitHub source of truth for the user's project code, detailed Markdown, and work logs.
Notion is the upper management dashboard for status, stage, priority, next action, and important URLs.

## First Files To Read

At the start of a new Codex chat, read only these lightweight files first:

1. `INDEX.json`
2. `docs/notion/projects.csv`
3. `docs/notion/README.md` only when the Notion management rules are needed

Do not read detailed project Markdown at startup. Wait until the user names a specific project, then read that project's `primary_docs` from `INDEX.json`.

## Notion Integration

Notion MCP is not required for this workspace.

In the current Windows Codex workspace, Notion API settings are stored locally in:

```text
C:\Users\irodo\Documents\Codex\2026-06-06\github-github-claude-codex-md-github\.env
```

The file contains these keys:

```text
NOTION_TOKEN
NOTION_PROJECTS_DATABASE_ID
NOTION_VERSION
```

Do not print the token. Do not commit `.env`. It is intentionally ignored by Git.

When another chat says "Notion integration tool is unavailable", use the Notion API with the local `.env` values instead of assuming Notion cannot be updated.

## Operating Model

- Notion: high-level status, next action, stage, priority, owner, and URLs.
- GitHub: code, detailed Markdown, work logs, and source of truth.
- `docs/notion/projects.csv`: GitHub-side mirror of the Notion project dashboard.
- Keep Notion concise. Do not duplicate long work logs into Notion.

## Current Important Projects

- `api-monitor`: Windows local Streamlit app. Launch URL is `http://127.0.0.1:8501`.
- `kakeibo-liff`: Household account book LIFF/GAS project under `yumekango-worker`.
- `market-pilot`: Standalone Codex-managed repository at `sjinnouchi-ux/market-pilot`.

## Memory Note

The user has enabled memory. Keep this operating model in mind for future chats:

1. Start from `INDEX.json` and `docs/notion/projects.csv`.
2. Use Notion as the management dashboard.
3. Use GitHub as the detailed source of truth.
4. Use local `.env` for Notion API access when available.
