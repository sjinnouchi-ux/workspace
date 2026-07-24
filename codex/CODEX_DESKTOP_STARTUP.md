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

## Claude Report Intake

Claude Desktopの作業レポートは `G:\マイドライブ\Claude保存\レポート\受信箱` に集まる。

- 受信箱の確認・統合は、ユーザーの明示指示または明示的なintakeタスクとしてのみ行う。通常タスクの開始時に自動確認しない。
- ローカル `G:` が見えない場合はGoogle Drive connector経由で確認し、単独の `Test-Path` 失敗を理由にintake以外の通常作業を停止しない。
- 処理開始時に対象ファイルを `処理中\<PC名>\` へ移動してclaimし、二重処理を防ぐ。移動できなかったファイルには手を出さない。
- 統合前に対象repoの既定branch、HEAD SHA、`AGENTS.md`、Primary Docsを読み、repo固有のbranch/PR・保存先規則を優先する。
- 統合完了（commit/push確認）までファイルを削除しない。処理後は処理済みへ移動し、`codex/work_log.md` にReport-IDとcommitを記録する。
- プロジェクトを特定できないレポートは保留へ移動し、ユーザーへ確認する。
- レポートに秘密値が含まれていた場合は統合を停止し、値を再掲せずに該当箇所を報告する。
- 詳細手順は `claude/REPORT_INTAKE.md` を正本とする。

## Reporting

- 確認済み事実だけを報告する。
- GitHub URL、branch、commit、PR、変更ファイルを可能な範囲で含める。
- GitHub反映前、PRのみ、`main`反映済み、deployment/live反映済みを区別する。
- 未完了または未同期の項目は、対象と理由を明示する。

## Shogun

Shogunは、WSL2 Linux + WebUI上で「GitHub境界連携方式」としてCodex Desktopから独立運用します。GitHubのcommit、branch、PRと必要なDrive成果物だけを境界として共有します。

Codex Desktopの設定、認証、session、ローカルworktree・cleanup方式、成果物保存領域はShogunと共有せず、この文書のCodex Desktop用規則をShogunへ一律適用しません。Shogunは専用branchを使用してmainへ直接pushせず、対象repoの既存規則を優先します。

Shogun実装、WSL2設定、WebUI設定は、ユーザーが明示的にShogun作業を依頼した場合だけ対象とします。通常のCodex Desktop交通整理では変更しません。

<!-- BEGIN CODEX_SHOGUN_TASK_INTAKE_V1 -->
### Codex-mediated Shogun task intake

ユーザーが「Shogunを使って」「Shogun経由で」「将軍へ依頼して」など、CodexからShogunを操作する意図を明示した場合に適用します。一般的な質問だけの場合はruntimeへ配送しません。

この明示依頼が許可するのは、指定されたtask本文を既存の承認済みShogun task入力経路へ1回配送することだけです。start、stop、restart、repair、deployment、permission自動承認、新しいtransportの作成は含みません。承認済み入力経路を確定できない場合は送信せず、不足する入口または承認を報告します。

配備済みで有効な `CODEX_SHOGUN_OPS_V1` がある場合、Shogunの操作とtask配送前の状態確認には同contractの固定 `status` だけを使用します。legacy `shogun-codex-diagnostics summary` を先行または並行実行しません。sanitized statusが `healthy` の場合だけ1回配送し、`stopped` の場合の1回起動、配送、限定restartの条件は `CODEX_SHOGUN_OPS_V1` に従います。Opsが未配備・無効・失敗・不明の場合は、承認済み入力経路を確認できないものとして配送せず、raw fallbackを行わず報告します。

この `healthy` は固定Ops statusの再計算済み `overall=healthy` を指し、legacy diagnostics はtask配送の前提ではなく、先にも並行にも実行しません。

依頼意図を次の3種類へ分類します。まず `ambiguous` を除外し、該当しない場合だけ、明示的な継続を `resume`、残りを `new` とします。3分類は相互排他的です。

1. `new`: `ambiguous` に該当せず、明示的な継続表現がない依頼。次のガードをtask本文の先頭へ付けます。

   ```text
   この依頼は新規taskです。前回の未完了task、未配送command、未処理receiptの状態を先に確認し、sanitized summaryで報告してください。前回taskを自動継続・再実行せず、今回の依頼は新しいtaskと新しいcommand epochとして開始してください。前回作業と今回の依頼が衝突する場合は実行せず、衝突理由と選択肢を報告してください。
   ```

2. `resume`: 「前回の続きをして」など継続が明示された依頼だけ。次のガードを付けます。

   ```text
   この依頼は前回taskの明示的な継続です。前回taskの現在状態と残作業を確認し、完了済み部分と終了済みcommandを再実行せず、残作業だけを継続してください。対象taskを一意に特定できない場合や状態が矛盾する場合は実行せず、sanitized summaryで確認を求めてください。
   ```

3. `ambiguous`: 「前と同じ」「さっきの件」など新規か継続か一意に決められない依頼。Shogunへ送信せず、Codexがユーザーへ確認します。既定値で継続扱いにしません。

Shogunから受け取る状態報告にも秘密値、Inbox本文、pane内容、生queue、生report、生ログを含めないよう指示します。
<!-- END CODEX_SHOGUN_TASK_INTAKE_V1 -->

### Runtime discovery

- `NUCBOX_K8_PLUS` はShogunのメインホストです。実Windowsユーザー `jinnouchi` のWSL2ディストリビューション `Ubuntu` に `/home/jinnouchi/multi-agent-shogun` があります。`ShogunUbuntu` は使用しません。
- Codexの隔離ユーザー（例: `codexsandboxoffline`）では、ユーザー単位のWSL登録が見えず `wsl.exe --list` が空になる場合があります。この結果だけで「WSL/Shogunが未インストール」と判定してはいけません。
- `NUCBOX_K8_PLUS` でShogun作業を依頼された場合は、実ユーザー環境でのコマンド実行許可を取得し、`Ubuntu`、repo、必要なtmux sessionの存在だけを確認してから作業します。秘密設定、tmux pane、生queue、生report、生ログは読み取り・出力しません。

<!-- BEGIN CODEX_SHOGUN_READONLY_DIAGNOSTICS_V1 -->
### Codex read-only diagnostics limited exception

The installed, user-owned regular mode-`0555` snapshot at the fixed path is the trust checkpoint for direct legacy diagnostic requests. No per-call GitHub registry, active-deployment, or source-hash lookup is required.

The preceding prohibition remains in force.

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

A nonzero exit, empty/non-JSON/partial output, nonempty stderr, or execution of
10 seconds or more is `diagnostic_process_failed`. Do
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

```text
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops status
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops start
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops restart-agent <allowlisted-agent>
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops restart-all
wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun /home/jinnouchi/.local/libexec/shogun-codex-ops deliver
```

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

- 標準確認入口は `wsl.exe -d Ubuntu --cd /home/jinnouchi/multi-agent-shogun` です。tmux sessionは将軍用 `shogun` と各役職用 `multiagent`、WebUIのローカル入口は `http://127.0.0.1:8790/` です。
- 別PCでローカルWSLが見つからない場合は「そのPCにShogun実体がない」と報告し、Shogun全体が未導入・消失したとは判定しません。メインホストへの接続経路が未確認なら、推測で代替環境を作らず停止します。
