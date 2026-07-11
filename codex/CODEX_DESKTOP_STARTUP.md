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
- Google業務操作は、ユーザーが別指定しない限り `s.jinnouchi@yumekango.com` を使う。

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

Shogunは、WSL2 Linux環境で起動しWebUIから利用する予定です。Codex Desktopのパーソナライズとオンラインルーティング確立後に、ShogunもこのGitHub正本、commit/push、作業ログ、cleanup gateへ適合させます。

その改修が完了するまでは、Codex Desktop側の交通整理でShogun実装、WSL2設定、WebUI設定を変更しません。
