# Codex Desktop Startup

## Role

この文書は、Windowsの各Codex Desktopがプロジェクト作業を始める際のオンライン正本です。ローカルclone、Codexの過去タスク、メモリ、フォルダ名より先にGitHub `main` 上のこの文書と `PROJECTS.md` を確認します。

Canonical URLs:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/GIT_HANDOFF_PROTOCOL.md
```

Claude、Codex、Fable間のGit引き継ぎは、共通契約 [`GIT_HANDOFF_PROTOCOL.md`](../GIT_HANDOFF_PROTOCOL.md) に従います。

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
- 開発環境、Memory MCP、Claude監査: `development-environment`
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

## Development Environment

Codex Desktopを唯一のオーケストレーターとします。通常の設計、実装、テスト、GitHub反映、進行管理はCodex Desktop内で行い、外部の常設オーケストレーターへtaskを配送しません。

開発環境の正本はprivate repository `sjinnouchi-ux/development-environment` です。`AGENTS.md`、`docs/HANDOFF.md`、`docs/MIGRATION_MANIFEST.md` を確認してから、Memory MCPまたはClaude監査の設定を変更します。

### Windows-local Memory MCP

- `NUCBOX_K8_PLUS` のWindows Codex Desktopでは `development_memory` を補助知識として使用する。
- 必ずGitHub正本、Canonical Entry、既定ブランチ、repo `AGENTS.md`、Primary Docsを確認した後で、Canonical repo名とcomponent名に絞って検索する。
- 記録できるのは、原因が確認され、修正後の検証が通り、再利用価値がある `VerifiedFailurePattern` だけとする。
- host scope、repo/area、component、sanitized symptom、confirmed root cause、verified fix、GitHub commit/PR/test等のevidence reference、verification dateだけを保持する。
- 秘密値、OAuth code、token、credential、認証JSON、`.env`、生ログ、生pane、生queue、生report、例外全文、個人識別情報、不要な絶対path、環境変数値、会話全文は保存しない。
- 同じpatternは重複entityを作らず、後続の検証結果を追記する。GitHubと矛盾する場合はGitHubを優先する。
- `development_memory` が利用不能または該当0件でも、GitHub正本が利用できる限り通常作業を継続する。
- このメモリはこのWindows PCのローカル保存であり、ノートPCやWSL2と自動同期されると仮定しない。

### WSL2 Claude read-only audit

- Claude CLIはWSL2 Ubuntu内の既存OAuth認証を利用するが、Codex Desktopの常設オーケストレーターにはしない。
- ユーザーが監査を求めたときだけ、`development-environment` の固定runnerを使い、対象commit、spec/evidence path、監査質問を明示して一回実行する。
- Claude childはread-only toolsだけを使用し、変更、Git push、retry、fallback、別CLI起動を行わない。
- 監査結果は補助判断であり、GitHub正本とCodexの検証を置き換えない。

### Retired Shogun

旧Shogun runtime、WebUI、固定Ops、diagnostics、break-glass、Native Windows parallel Shogunは退役対象です。新規taskを配送せず、start、restart、repair、再配備、旧repoをCanonical Entryとして使用しません。移行・削除の記録は `development-environment` を正本とします。
