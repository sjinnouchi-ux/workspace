# NUCBOX_K8_PLUS Codex Memory MCP Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure the Windows Codex Desktop on `NUCBOX_K8_PLUS` to consult verified failure memories after GitHub startup checks and to record only confirmed, verified, reusable failure patterns.

**Architecture:** Add one host-scoped conditional block to the GitHub-canonical Codex Desktop custom instructions and mirror the exact block into this PC's global `~/.codex/AGENTS.md`. The existing Windows-local `shogun_memory` STDIO MCP remains unchanged; the policy treats it as supplementary context and never as the project source of truth.

**Tech Stack:** Markdown, Codex `AGENTS.md`, Windows PowerShell 7, `shogun_memory` MCP

## Global Constraints

- The rule applies only to `NUCBOX_K8_PLUS` Windows Codex Desktop.
- Do not assume the notebook PC has the same Memory MCP data.
- GitHub `main`, Canonical Entry, repository `AGENTS.md`, and Primary Docs remain authoritative and are checked before memory search.
- Record only failures with confirmed cause, verified fix, reuse value, and sanitized evidence reference.
- Never store secrets, OAuth codes, tokens, credentials, authentication JSON, `.env` content, raw logs, raw panes, raw queue/report data, full exceptions, or personal identifiers.
- Memory MCP unavailability is reported but does not block work when GitHub sources are available.
- Do not modify WSL2, tmux, Shogun runtime, Memory MCP command/configuration, or the notebook PC.
- Add no test code.

---

### Task 1: Install the host-scoped Memory MCP working agreement

**Files:**
- Modify: `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`
- Modify: `codex/work_log.md`
- Modify outside repository: `C:\Users\jinnouchi\.codex\AGENTS.md`

**Interfaces:**
- Consumes: existing `[mcp_servers.shogun_memory]` Windows STDIO configuration and `shogun_memory` tool namespace
- Produces: one exact `NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V1` instruction block in the GitHub canonical template and local global AGENTS file

- [ ] **Step 1: Verify the exact policy marker is initially absent**

Run:

```powershell
$marker = 'BEGIN NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V1'
rg -n --fixed-strings $marker codex\CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md
Select-String -LiteralPath 'C:\Users\jinnouchi\.codex\AGENTS.md' -SimpleMatch $marker
```

Expected: both searches return no match.

- [ ] **Step 2: Add the exact canonical instruction block**

Insert the following block into the `Paste This Text` fenced section of `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`, immediately after the existing secrets prohibition and before the Shogun rules:

```markdown
<!-- BEGIN NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V1 -->
### NUCBOX_K8_PLUS Windows Codex Desktop Memory MCP

この規則は host `NUCBOX_K8_PLUS` の Windows Codex Desktop にだけ適用します。ノートPCや他PCに同じMemory MCP設定・保存内容があると推測しないでください。

各タスクでは、最初にGitHub `main` の共通起動手順と `PROJECTS.md`、Canonical Entry、対象repoの既定ブランチ・`AGENTS.md`・Primary Docsを確認してください。その後に限り、`shogun_memory` をCanonical repo名と対象component名で検索し、関連する `VerifiedFailurePattern` の症状、確定原因、検証済み修正、evidence referenceを確認してから作業してください。メモリとGitHub正本が矛盾する場合はGitHubを優先し、メモリを理由に正本確認を省略しないでください。

タスク完了時、再発可能性と再利用価値があり、原因が確認され、修正後の検証が通った失敗だけを `VerifiedFailurePattern` として記録してください。host scope、Canonical repoまたは共通運用area、component、sanitized symptom、confirmed root cause、verified fix、GitHub commit・PR・test result等のevidence reference、verification dateだけを保持してください。同じpatternがある場合は重複entityを作らず、既存entityへ新しい検証結果を追記してください。異なる結果は上書きせず後続検証として追記してください。

原因未確定、推測段階、一時的または再現不能な失敗、秘密値、OAuth code、token、credential、認証JSON、`.env`内容、生ログ、生pane、生queue、生report、例外全文、個人識別情報、不要なローカル絶対path、環境変数値、タスク本文や会話全文は記録しないでください。

`shogun_memory` が利用不能または該当記録0件でも、GitHub正本を確認できる限りタスクは継続し、利用不能だった事実だけを報告してください。Memory MCPを作業開始の必須gateにしないでください。
<!-- END NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V1 -->
```

- [ ] **Step 3: Mirror the exact block into this PC's global AGENTS file**

Create an updated full-file candidate inside the task worktree by applying the same exact block to a copy of `C:\Users\jinnouchi\.codex\AGENTS.md`. Compare the candidate with the current file and require the diff to contain only the one marked block. After approval for the protected local path, replace `C:\Users\jinnouchi\.codex\AGENTS.md` with the reviewed candidate in one copy operation.

Expected: the existing file content is preserved byte-for-byte outside the new marked block.

- [ ] **Step 4: Append the operational record**

Append a dated entry to `codex/work_log.md` stating:

```markdown
## 2026-08-11 NUCBOX_K8_PLUS Codex Memory MCP working agreement

- Added the host-scoped `NUCBOX_K8_PLUS_CODEX_MEMORY_MCP_V1` block to the GitHub-canonical Codex Desktop custom instructions.
- Mirrored the exact block to this PC's global `~/.codex/AGENTS.md`; the notebook PC was not changed and is not assumed to share this memory.
- The rule preserves GitHub-first startup, searches only related verified failure patterns, records only confirmed and verified reusable failures, and excludes secrets and raw runtime data.
- `shogun_memory` remains a Windows-local STDIO MCP and is not a required task gate. WSL2, tmux, Shogun runtime, and MCP configuration were not changed.
```

- [ ] **Step 5: Verify canonical/local block identity and repository scope**

Run a PowerShell comparison that extracts text from the begin marker through the end marker in both files, normalizes only CRLF/LF, and compares SHA-256. Do not print the block body.

Expected projection:

```json
{"canonical_marker_count":1,"local_marker_count":1,"normalized_block_hash_match":true}
```

Then run:

```powershell
git diff --check
git status --short
git diff -- codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md codex/work_log.md
```

Expected: diff check passes; only the canonical instructions and work log are modified in this implementation commit.

- [ ] **Step 6: Verify the existing MCP connection without reading stored content**

Use `shogun_memory.search_nodes` once with the unique query `__nucbox_memory_policy_connectivity_probe_20260811__`.

Expected: the tool call succeeds, returns zero matches, writes nothing, and emits no stored memory content.

- [ ] **Step 7: Commit and push the implementation**

Run:

```powershell
git add -- codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md codex/work_log.md
git commit -m "docs: enable NUCBOX memory MCP workflow"
git push
```

Expected: the dedicated branch is pushed; no local-only repository changes remain.

- [ ] **Step 8: Perform the next-task acceptance check**

Start a new Codex Desktop task because AGENTS instructions are loaded at task start. Ask:

```text
このPCで有効なMemory MCP運用規則を要約してください。GitHub正本を確認する順序、メモリを検索する時点、記録してよい失敗、記録禁止項目、ノートPCとの分離を含めてください。メモリへの書込みはしないでください。
```

Expected: the response identifies `NUCBOX_K8_PLUS Windows Codex Desktop`, places GitHub checks before memory search, limits recording to verified reusable failures, lists the exclusions, does not claim notebook synchronization, and performs no write.

