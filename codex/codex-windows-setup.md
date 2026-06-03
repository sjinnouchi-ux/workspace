# Codex Windows Setup

Created: 2026-06-03
Environment: Windows / Codex Desktop
GitHub account: `sjinnouchi-ux`

This document records the Windows-side Codex setup recreated from the Mac/Cowork history.
Secrets, OAuth tokens, API keys, service-role keys, and credential JSON contents are intentionally not recorded here.

## Purpose

- Recreate the Mac-side Codex, MCP, GitHub, and API-monitoring workflow on Windows.
- Keep the setup auditable in GitHub without exposing secrets.
- Make future Windows Codex sessions able to use GitHub, Node/npm/npx, Python, Streamlit, and MCP servers.

## Installed Tools

| Tool | Version / Status | Notes |
|---|---:|---|
| Git for Windows | `2.54.0.windows.1` | Installed with `winget`. |
| GitHub CLI | `2.93.0` | Logged in as `sjinnouchi-ux`. |
| Node.js | `v24.16.0` | Provides `npm` and `npx` for MCP servers. |
| npm / npx | `11.13.0` | PowerShell execution policy set to `RemoteSigned` for `.ps1` shims. |
| Python | `3.13.13` | Installed in the user profile. |
| uv | `0.11.17` | Used for Python REPL MCP startup. |

## PATH

The Windows user PATH was updated so these locations are preferred:

```text
C:\Program Files\nodejs\
C:\Users\irodo\AppData\Local\Programs\Python\Python313\
C:\Users\irodo\AppData\Local\Programs\Python\Python313\Scripts\
C:\Program Files\Git\cmd
C:\Program Files\GitHub CLI\
C:\Users\irodo\AppData\Local\Microsoft\WindowsApps
C:\Users\irodo\AppData\Local\Programs\Python\Launcher\
C:\Users\irodo\AppData\Roaming\npm
C:\Users\irodo\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe
```

PowerShell execution policy:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
```

This allows `npm` and `npx` PowerShell shims to run normally.

## GitHub

GitHub CLI authentication was completed with device login.

Verified state:

```text
github.com
  Logged in to github.com account sjinnouchi-ux (keyring)
  Git operations protocol: https
  Token scopes: gist, read:org, repo
```

Git was connected to GitHub CLI credentials:

```powershell
gh auth setup-git
```

Global Git identity:

```text
user.name  = sjinnouchi-ux
user.email = 285629432+sjinnouchi-ux@users.noreply.github.com
```

## Cloned Repositories

The following repositories were cloned into the Windows Codex workspace:

```text
C:\Users\irodo\Documents\Codex\2026-06-03\mac-github\workspace
C:\Users\irodo\Documents\Codex\2026-06-03\mac-github\market-pilot
```

Both were clean after clone.

## Codex MCP Configuration

Windows Codex config file:

```text
C:\Users\irodo\.codex\config.toml
```

Backup created before editing:

```text
C:\Users\irodo\.codex\config.toml.bak-20260603-095348
```

Existing settings preserved:

- Browser plugin enabled
- `node_repl` MCP server preserved
- Codex bundled marketplaces and runtime plugins preserved

Added MCP servers:

```toml
[mcp_servers.gsc]
command = 'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe'
args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', '$sep=[char]59; $env:Path="C:\Program Files\nodejs\"+$sep+[Environment]::GetEnvironmentVariable("Path","Machine")+$sep+[Environment]::GetEnvironmentVariable("Path","User"); & "C:\Program Files\nodejs\npx.cmd" -y google-searchconsole-mcp']
startup_timeout_sec = 120

[mcp_servers.github]
command = 'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe'
args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', '$sep=[char]59; $env:Path="C:\Program Files\nodejs\"+$sep+[Environment]::GetEnvironmentVariable("Path","Machine")+$sep+[Environment]::GetEnvironmentVariable("Path","User"); $env:GITHUB_PERSONAL_ACCESS_TOKEN=& "C:\Program Files\GitHub CLI\gh.exe" auth token; & "C:\Program Files\nodejs\npx.cmd" -y @modelcontextprotocol/server-github']
startup_timeout_sec = 120

[mcp_servers."ga4-mcp-server"]
command = 'C:\WINDOWS\System32\WindowsPowerShell\v1.0\powershell.exe'
args = ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', '$sep=[char]59; $env:Path="C:\Program Files\nodejs\"+$sep+[Environment]::GetEnvironmentVariable("Path","Machine")+$sep+[Environment]::GetEnvironmentVariable("Path","User"); & "C:\Program Files\nodejs\npx.cmd" -y mcp-remote@0.1.30 https://mcp-ga.stape.ai/mcp']
startup_timeout_sec = 120

[mcp_servers."python-repl"]
command = 'C:\Users\irodo\AppData\Local\Microsoft\WinGet\Packages\astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe\uv.exe'
args = ['tool', 'run', 'mcp-python-repl']
startup_timeout_sec = 120
```

### MCP Notes

- `github` does not store the token in `config.toml`; it reads the token at startup via `gh auth token`.
- `gsc` may require first-run Google OAuth in the browser.
- `ga4-mcp-server` uses the remote GA4 MCP endpoint `https://mcp-ga.stape.ai/mcp` and may require OAuth.
- `python-repl` starts through `uv tool run mcp-python-repl`.
- Codex app restart is required before newly added MCP servers appear as tools.

## API Monitor

The Mac-side `api-monitor` project was cloned from `workspace/api-monitor`.

Python dependencies were installed with Windows Python 3.13:

```powershell
python -m pip install -r .\workspace\api-monitor\requirements.txt
```

Installed key packages:

- `streamlit`
- `openai`
- `anthropic`
- `google-generativeai`
- `python-dotenv`
- `pandas`
- `plotly`

Database initialized:

```text
C:\Users\irodo\Documents\Codex\2026-06-03\mac-github\workspace\api-monitor\data\api_log.db
```

Created local `.env` with empty key placeholders:

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
API_MONITOR_DB_PATH=data/api_log.db
```

API keys must be filled in locally. Do not commit `.env`.

Streamlit was verified on:

```text
http://localhost:8501
```

## Verification

Confirmed commands:

```text
python --version  -> Python 3.13.13
npm --version     -> 11.13.0
npx --version     -> 11.13.0
git --version     -> git version 2.54.0.windows.1
gh auth status    -> logged in as sjinnouchi-ux
```

Confirmed MCP startup commands:

- GitHub MCP: starts on stdio
- Search Console MCP: starts on stdio
- Python REPL MCP: starts on stdio

Confirmed Codex config syntax:

```powershell
python -c "import tomllib, pathlib; tomllib.loads(pathlib.Path(r'C:\Users\irodo\.codex\config.toml').read_text(encoding='utf-8-sig')); print('toml_ok')"
```

Result:

```text
toml_ok
```

## Remaining Follow-Up

- Restart Codex Desktop so the new MCP server entries are loaded.
- Confirm whether `github`, `gsc`, `ga4-mcp-server`, and `python-repl` appear as tools after restart.
- Complete first-run OAuth for Search Console and GA4 if prompted.
- Fill API monitor `.env` locally with actual API keys.
- If GA4 MCP still fails during `tools/list`, consider replacing it with a direct GA4 Data API script or a dedicated local MCP server.
