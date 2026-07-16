# Codex Desktop Startup

## Role

この文書は、Windowsの各Codex Desktopがプロジェクト作業を始める際のオンライン正本です。ローカルclone、Codexの過去タスク、メモリ、フォルダ名より先にGitHub `main` 上のこの文書と `PROJECTS.md` を確認します。

Canonical URLs:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md
```

OpenAI references:

- https://learn.chatgpt.com/docs/personalize
- https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Startup Order

1. GitHub `sjinnouchi-ux/workspace` の `main` を取得し、この文書と `PROJECTS.md` を読む。
2. 取得に使った `workspace` のcommit SHAを確認する。
3. ユーザーの表現を `PROJECTS.md` の `Alias` と照合し、Canonical Entryを確定する。
4. 対象Gitの既定ブランチを取得し、repoの `AGENTS.md` があれば最初に読む。
5. `PROJECTS.md` のPrimary Docsを読み、現在状態と作業範囲を確定する。
6. 必要な場合だけ、タスク専用のローカルclone/worktreeを作る。

URL取得、GitHub認証、対象プロジェクト特定のいずれかに失敗した場合は、同名ローカルフォルダや過去cloneを推測で使用しません。作業を停止し、不足している接続または登録を報告します。

## GitHub Access

- GitHub owner/account: `sjinnouchi-ux`
- `s.jinnouchi@yumekango.com` はGoogle業務用アカウントであり、GitHub owner名ではない。
- `workspace` は公開ルーターだが、個別のprivate repoには各PCでGitHub認証が必要。
- GitHub connectorが使える場合はconnectorを優先する。
- CLIが必要な場合は `gh auth status` でactive accountを確認し、`git fetch origin --prune` 後にremoteとlocalを比較する。

## Local Work Policy

- ローカルは作業場であり正本ではない。
- 既存cloneを使う場合も、remote URL、default branch、upstream、dirty stateを確認してから作業する。
- 新規作業はタスク単位のclone/worktreeで行う。
- コード、判断記録、実装ログ、引き継ぎは対応するGitHub repoへcommit/pushする。
- ローカルだけに残るMarkdown、未push commit、未追跡成果物がある状態を完了と報告しない。
- live appを扱う場合は、repo state、設定/editor state、deployed/live stateを分けて報告する。

## Windows And PowerShell

- Codex Desktopのローカル作業はWindows + PowerShellを前提とする。
- 検索は `rg` / `rg --files` を優先する。
- 日本語Markdown、CSV、textは `Get-Content -Encoding UTF8` で読む。
- destructiveなfilesystem/Git操作は、対象と救出完了を確認してから実行する。

## Cleanup Gate

タスク用ローカル作業場は、次をすべて確認した後に整理できます。

- 必要な変更がcommit済み
- remoteへpush済み
- PRまたは既定ブランチへの反映状態を確認済み
- 必要な作業ログをGitHubへ反映済み
- 最終成果物をGitHubまたは指定Google Driveへ保存済み
- `git status` で必要な未追跡・未コミット情報がない
- deploymentや外部サービス作業がある場合はlive確認済み

条件を満たさない作業場は削除せず、救出対象として報告します。

## Secrets And Accounts

- 秘密値、OAuthコード、token、認証JSON、`.env` の中身をチャット、Markdown、GitHubへ表示・保存しない。
- project repoのsecret管理文書とruntime設定を先に確認する。
- Secret Managerまたはruntime secret storeが正本と明記されたrepoでは、それを優先する。
- `C:\Users\irodo\.codex\.sandbox-secrets\global.env` は、repoが明示的に要求する場合だけローカル互換入力として使う。新PCへ一律コピーしない。
- Secret Manager移行済みと判定するには、`Secret ID + enabled version`、project/role manifest、service account IAM、helper経由のconsumer疎通の4点を確認する。
- Secret IDだけが存在し、manifest、IAM、consumer疎通のいずれかが欠ける場合は `stored_only` と扱う。`global.env` へ戻らず、作業を停止して不足層を報告する。
- Google業務操作は、ユーザーが別指定しない限り `s.jinnouchi@yumekango.com` を使う。

Cross-project audit:

```text
https://github.com/sjinnouchi-ux/mgmt-terminal/blob/main/docs/reports/2026-07-11-cross-project-secret-consumer-audit.md
```

## Documentation Contract

- 全体ルーティング: `workspace/PROJECTS.md`
- 共通Codex運用: `workspace/codex/`
- コード、詳細設計、実装ログ: 各project repoのMarkdown
- 未登録プロジェクト: 推測で作らず、ユーザー確認
- 古いNotion CSV、日付別clone、Codexメモリは補助資料であり、現行ルーティングの正本にしない。

## Deliverable Storage

ユーザーがGit管理外の成果物保存を求めた場合は、次のGoogle Drive同期先を使います。

| Type | Windows path |
|---|---|
| Base | `G:\マイドライブ\Codex保存` |
| Images | `G:\マイドライブ\Codex保存\画像` |
| Documents | `G:\マイドライブ\Codex保存\資料` |
| General outputs | `G:\マイドライブ\Codex保存\出力` |
| Temporary review | `G:\マイドライブ\Codex保存\一時確認` |

Folder URL:

```text
https://drive.google.com/drive/folders/1yrWHPFuE7yHZGhs_MLeVZPiifpfsDVQX
```

対象PCに同期先が存在しない場合は別のローカル場所を推測せず、未保存として報告します。保存後はファイルパスとGoogle DriveフォルダURLを報告します。

## Reporting

- 確認済み事実だけを報告する。
- GitHub URL、branch、commit、PR、変更ファイルを可能な範囲で含める。
- GitHub反映前、PRのみ、`main`反映済み、deployment/live反映済みを区別する。
- 未完了または未同期の項目は、対象と理由を明示する。

## Shogun

Shogunは、WSL2 Linux + WebUI上で「GitHub境界連携方式」としてCodex Desktopから独立運用します。GitHubのcommit、branch、PRと必要なDrive成果物だけを境界として共有します。

Codex Desktopの設定、認証、session、ローカルworktree・cleanup方式、成果物保存領域はShogunと共有せず、この文書のCodex Desktop用規則をShogunへ一律適用しません。Shogunは専用branchを使用してmainへ直接pushせず、対象repoの既存規則を優先します。

Shogun実装、WSL2設定、WebUI設定は、ユーザーが明示的にShogun作業を依頼した場合だけ対象とします。通常のCodex Desktop交通整理では変更しません。

### Runtime discovery

- `NUCBOX_K8_PLUS` はShogunのメインホストです。実Windowsユーザー `jinnouchi` のWSL2ディストリビューション `Ubuntu` に `/home/jinnouchi/multi-agent-shogun` があります。`ShogunUbuntu` は使用しません。
- Codexの隔離ユーザー（例: `codexsandboxoffline`）では、ユーザー単位のWSL登録が見えず `wsl.exe --list` が空になる場合があります。この結果だけで「WSL/Shogunが未インストール」と判定してはいけません。
- `NUCBOX_K8_PLUS` でShogun作業を依頼された場合は、実ユーザー環境でのコマンド実行許可を取得し、`Ubuntu`、repo、必要なtmux sessionの存在だけを確認してから作業します。秘密設定、tmux pane、生queue、生report、生ログは読み取り・出力しません。

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

- 標準確認入口は `wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun` です。tmux sessionは将軍用 `shogun` と各役職用 `multiagent`、WebUIのローカル入口は `http://127.0.0.1:8790/` です。
- 別PCでローカルWSLが見つからない場合は「そのPCにShogun実体がない」と報告し、Shogun全体が未導入・消失したとは判定しません。メインホストへの接続経路が未確認なら、推測で代替環境を作らず停止します。

