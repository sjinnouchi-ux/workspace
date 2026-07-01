# Legacy Notion Project Management Prep

This folder is a legacy record from the previous Notion-centered project management workflow.

Current project routing is managed by root `PROJECTS.md`; Notion is not the normal progress-management source.

## Purpose

GitHub remains the source of truth for code, detailed Markdown docs, AI instructions, and work logs.
Notion should be used as the upper management layer for project status, priority, next action, and review cadence.

## Recommended Notion Database

Create one Notion database named `Projects`.

Recommended properties:

| Property | Type | Purpose |
|---|---|---|
| Project | Title | Project name |
| Status | Select | Current management state |
| Stage | Select | Production or development stage |
| Priority | Select | Relative importance |
| Owner | Select | Main working agent or human owner |
| Repository | Text | GitHub repository name |
| GitHub URL | URL | Main GitHub location |
| Primary Docs | Text | First docs to read |
| Production URL | URL | Public production site or app |
| Preview URL | URL | Preview, staging, or test environment |
| Supabase URL | URL | Supabase dashboard or API URL |
| Google Drive URL | URL | Main Drive folder for assets or deliverables |
| Google Sheets URL | URL | Main operations spreadsheet |
| Apps Script URL | URL | Google Apps Script project |
| Admin URL | URL | External admin console such as LINE, Cloudflare, or Ads |
| Reference URLs | Text | Other important links, separated by semicolons |
| Next Action | Text | Next concrete action |
| Blocker | Text | Current blocker or waiting condition |
| Review Cycle | Select | How often to review the project |
| Last Updated | Date | Latest meaningful GitHub update |
| Notes | Text | Short context |

## Status Values

Use these values consistently:

| Status | Meaning |
|---|---|
| Active | Currently moving |
| Backlog | Planned or waiting for attention |
| Support | Utility or operating infrastructure |
| Reference | Stable reference material |
| Archived | Kept for history, not actively managed |

## Stage Values

Use these values consistently:

| Stage | Meaning |
|---|---|
| Idea | Idea only |
| Planning | Requirements, scope, or content planning |
| Design | Architecture, DB, UI, or workflow design |
| Development | Implementation is active |
| Testing | Verification or test operation |
| Production | Content production is active |
| Operation | Running in practical use |
| Maintenance | Stable but occasionally maintained |
| Reference | Reference material only |

## Priority Values

Use these values consistently:

| Priority | Meaning |
|---|---|
| High | Important this month |
| Medium | Useful, but not the main lane |
| Low | Keep visible, but do not actively push |

## Legacy AI Startup Rule

This rule is deprecated. Current startup should use root `PROJECTS.md`.

Formerly, at the start of a new chat, Codex / Claude read lightweight project indexes:

1. root `PROJECTS.md`
2. the target project Git listed in `PROJECTS.md`
3. project-level `PROJECT_BRIEF.md`, `DESIGN_LOG.md`, and `IMPLEMENTATION_LOG.md`

Do not read detailed project Markdown during the first broad conversation. Read project-specific docs only after the user names the project they want to work on.

## Import Flow

1. Import `projects.csv` into Notion.
2. Convert `Status`, `Stage`, `Priority`, `Owner`, and `Review Cycle` to Select properties.
3. Convert `GitHub URL` to URL.
4. Convert `Production URL`, `Preview URL`, `Supabase URL`, `Google Drive URL`, `Google Sheets URL`, `Apps Script URL`, and `Admin URL` to URL.
5. Convert `Last Updated` to Date.
6. Create filtered views:
   - `Active`
   - `Codex`
   - `Claude`
   - `This Month`
   - `Backlog`

## GitHub Rule

Do not duplicate detailed project logs in Notion.
Keep detailed history in GitHub Markdown, and keep Notion focused on the latest status and next action.
