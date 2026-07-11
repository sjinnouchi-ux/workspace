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

ShogunはWSL2 Linux + WebUI環境として後日この運用へ改修します。それまではShogun実装・設定をこのDesktop交通整理の対象にしないでください。
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
