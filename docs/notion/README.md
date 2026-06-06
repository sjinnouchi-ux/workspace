# Notion Project Management Prep

This folder prepares the GitHub workspace for high-level Notion project management.

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
| Priority | Select | Relative importance |
| Owner | Select | Main working agent or human owner |
| Repository | Text | GitHub repository name |
| GitHub URL | URL | Main GitHub location |
| Primary Docs | Text | First docs to read |
| Next Action | Text | Next concrete action |
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

## Priority Values

Use these values consistently:

| Priority | Meaning |
|---|---|
| High | Important this month |
| Medium | Useful, but not the main lane |
| Low | Keep visible, but do not actively push |

## Import Flow

1. Import `projects.csv` into Notion.
2. Convert `Status`, `Priority`, and `Owner` to Select properties.
3. Convert `GitHub URL` to URL.
4. Convert `Last Updated` to Date.
5. Create filtered views:
   - `Active`
   - `Codex`
   - `Claude`
   - `This Month`
   - `Backlog`

## GitHub Rule

Do not duplicate detailed project logs in Notion.
Keep detailed history in GitHub Markdown, and keep Notion focused on the latest status and next action.
