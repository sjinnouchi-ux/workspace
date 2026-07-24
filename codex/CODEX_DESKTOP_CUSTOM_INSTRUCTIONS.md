# Codex Desktop Custom Instructions

## Purpose

Codex Desktopの `Settings > Personalization > Custom instructions` に設定する共通文面です。Codexではこの内容が各PCのグローバル `~/.codex/AGENTS.md` として扱われます。

Official reference: https://learn.chatgpt.com/docs/personalize

全文の運用規則を各PCへ複製せず、GitHub `main` のオンライン正本へ案内するbootstrapだけを置きます。

## Paste This Text

```text
各タスク開始時、ローカルフォルダ、過去のclone、Codexメモリをプロジェクトの正本として先に使用しないでください。

最初に、GitHub main上の次の共通起動手順を必ず取得し、最新版に従ってください。
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md

次に、次のオンライン台帳から対象プロジェクトのCanonical Entryを確定してください。
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md

対象GitHub repoの既定ブランチ、AGENTS.md、PROJECTS.md記載のPrimary Docsを確認してから作業してください。

URLを取得できない、GitHubのprivate repoへ認証できない、対象プロジェクトを特定できない場合は、同名ローカルフォルダを推測で使わず、作業を停止して不足事項を報告してください。

実装はタスク専用のローカルclone/worktreeで行って構いません。完了時は必要な変更と作業ログをGitHubへ反映し、未コミット、未push、ローカル専用情報がないことを確認してからローカル作業場を整理してください。

秘密値、OAuthコード、token、認証JSON、.envの中身をチャットやGitHubへ表示・保存しないでください。

ShogunはWSL2 Linux + WebUI上で、Codex Desktopと設定・認証・session・Drive領域を共有しない「GitHub境界連携方式」として別運用します。Shogun実装・設定は明示的なShogun作業でのみ扱い、通常のCodex Desktop交通整理の対象にしないでください。

「Shogunを使って」「Shogun経由で」などCodexからShogunを操作する依頼では、毎回取得した共通起動手順の `CODEX_SHOGUN_TASK_INTAKE_V1` を適用してください。最初に新規か継続か曖昧かを判定し、曖昧な場合はShogunへ送信せず利用者へ確認してください。曖昧でない依頼のうち、明示的な継続だけを再開し、それ以外は新規taskとして前回taskを自動継続しないでください。Shogun taskの配送意図だけではstart、stop、restart、repair、deployment、permission承認を許可しません。deployment済みで有効な `CODEX_SHOGUN_OPS_V1` だけが、その固定operationだけを許可します。

NUCBOX_K8_PLUSでは、Shogunは実Windowsユーザー jinnouchi のWSL2 Ubuntuにあります。Codex隔離ユーザーから `wsl.exe --list` が空に見えても未インストールと判定せず、実ユーザー環境での実行許可を取得して確認してください。入口は `wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun`、tmux sessionは `shogun` と `multiagent`、WebUIは `http://127.0.0.1:8790/` です。`ShogunUbuntu` は使用しません。別PCでローカル実体が見つからない場合も、Shogun全体が未導入・消失したとは判定しないでください。秘密設定、tmux pane、生queue、生report、生ログは読み取り・出力しないでください。

<!-- BEGIN CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->
### Codex read-only diagnostics limited exception

The preceding prohibition remains in force. Immediately before each diagnostic
invocation, Codex must fetch GitHub `main` raw
`https://raw.githubusercontent.com/sjinnouchi-ux/multi-agent-shogun/main/docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md`,
validate its single marked schema-version-1 JSON registry and exactly one active
deployment, then compare that record's source SHA-256 with the returned
`tool.source_sha256`.

Only this complete command is eligible for a persistent argv-prefix permission:

`wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-diagnostics summary`

The installed mode-`0555` snapshot may locally aggregate only its fixed,
allowlisted Git/tmux/process/filesystem metadata and the counts of its four fixed
watcher-log substrings from at most the final 1,048,576 bytes. Codex receives
only schema-version-1 JSON. It does not directly read runtime files, logs, or
panes.

Before using any diagnostic field, Codex must require exit 0 and independently
validate ASCII-only bytes plus the complete nested schema, exact key order,
session/agent cardinality, enums, issue severity, count/state/applicability
cross-field invariants, and a recomputed `overall` value.

Do not persist a shorter `wsl.exe`, `bash -lc`, `python3`, or repo-script prefix.
`cat`, `grep`, YAML bodies, log lines, pane capture, arbitrary paths, sessions,
agents, regexes, shell commands, other scripts, suffix arguments, environment
overrides, starts, stops, restarts, repairs, and writes remain forbidden.

GitHub provenance retrieval or validation failure, no active deployment,
multiple active deployments, and source-hash mismatch are
`diagnostic_provenance_untrusted`. A nonzero exit, empty/non-JSON/partial output,
nonempty stderr, or execution of 10 seconds or more is `diagnostic_process_failed`. In both cases, do
not trust diagnostic fields and do not use any raw or direct-read fallback.
Snapshot placement or update is a separate, explicitly approved Shogun
deployment task and is not part of this exception.
<!-- END CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->

<!-- BEGIN CODEX_SHOGUN_OPS_V1 -->
### Codex-mediated Shogun Ops exception

This fixed Ops exception is inactive until a one-time deployment checkpoint has
verified the reviewed GitHub `main` source, a clean runtime repo at the reviewed
commit, the fixed repo venv/PyYAML dependency, a user-owned regular mode-`0555`
snapshot at the fixed path, and installation of the matching host policy. After
that checkpoint, no per-call GitHub registry or source-hash lookup is required
for the Ops wrapper.

Only these complete executable/subcommand vectors are eligible for persistent
permission. Never permit a shorter `wsl.exe`, `bash -lc`, Python, repo script,
arbitrary path, suffix, or environment prefix:

wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops status
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops start
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops restart-agent <allowlisted-agent>
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops restart-all
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops deliver

- `status` is routine read-only monitoring.
- For an explicit, unambiguous Shogun task, `start` may run once without a new
  approval only when sanitized status is `stopped` and no active task exists.
- `restart-agent` may run once without a new approval only when sanitized status
  identifies exactly one allowlisted stalled agent.
- `deliver` may run exactly once without a new approval only after sanitized
  status is `healthy`; it accepts the exact bounded validated UTF-8 JSON document
  on stdin and relies on the idempotency key.
- `restart-all` always requires explicit user approval for that invocation.

Unknown/degraded state, multiple stalled agents, failed/ambiguous task state, or
wrapper failure stops without raw fallback or automatic repair. The existing
`CODEX_SHOGUN_TASK_INTAKE_V1` new/resume/ambiguous guard still applies to
delivery.

Codex receives only the sanitized fixed JSON contract. It must not read or
display raw queue/report/log/pane content, secrets, environment values, task
bodies from runtime state, or personal identifiers.

Routine Ops changes use focused contract tests plus a real-task canary.
Full-suite work is reserved for core orchestration, queue/report schema,
launcher/tmux topology, watcher, or recovery changes.

Rollback removes the exact host/Workspace exception and restores/removes the
fixed Ops snapshot without deleting existing runtime task records or attempting
automatic session repair.
<!-- END CODEX_SHOGUN_OPS_V1 -->
```

## Verification

設定後に新しいCodexタスクを開始し、次を依頼します。

```text
共通起動手順とPROJECTS.mdをGitHub mainから取得し、取得したworkspace commit SHAと、現在登録されているCanonical Entryの件数を報告してください。ローカルcloneはまだ作らないでください。
```

成功条件:

- raw GitHub URLを取得できる
- `sjinnouchi-ux/workspace` のcommit SHAを報告できる
- `PROJECTS.md` のCanonical Entryを読める
- 同名ローカルフォルダへ先に移動しない
- Shogun操作依頼で `CODEX_SHOGUN_TASK_INTAKE_V1` を取得し、`new`、`resume`、`ambiguous` を区別する。
- 新規taskは前回taskを自動継続せず、曖昧な依頼とunhealthy/untrusted診断では送信しない。
- Before every fixed diagnostic invocation, GitHub main has one valid active deployment and its source SHA-256 matches `tool.source_sha256`.
- The complete command exits 0, returns one fully schema-valid version-1 ASCII JSON object, has empty stderr, and finishes in under 10 seconds; `overall=degraded|unavailable` is not a process failure.
- Free text, pane/YAML/log bodies, paths, PID, command line, remote URL, exact runtime sizes, and runtime hashes are absent.
- Provenance/process failure never triggers a raw fallback, repo-script execution, shorter WSL permission, or direct runtime read.
