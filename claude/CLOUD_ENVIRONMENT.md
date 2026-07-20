# Claude Code Cloud Environment

Claude Code on the web（claude.ai/code）で使う環境定義の正本です。環境定義はclaude.ai側に保存されるため、この文書は「消えた場合に同一環境を再作成するための仕様書」として機能します。

## 前提

- クラウドセッションはAnthropic管理のVM上で動き、セッションはアカウントに紐づいて永続する。デスクトップPC・ノートPC・スマホのどこからでも同一セッションを開いて継続できる。
- VM自体はセッション単位の使い捨て。成果はGitHubへのpushだけが永続する（`CLAUDE_CODE_STARTUP.md` のCleanup Gate参照）。
- 追加のインフラ費用はない。使用量は既存サブスクリプションの上限を共有する。
- research preview段階の機能であり、仕様変更があり得る。変更を検知した場合はこの文書を更新する。

## 環境定義（正本仕様）

| 項目 | 値 |
|---|---|
| Environment name | `yumekango-standard` |
| Network access | `Trusted`（既定の許可リスト: パッケージレジストリ、GitHub等） |
| Environment variables | なし（秘密値は置かない。`GH_TOKEN` / `GITHUB_TOKEN` も未設定とし、GitHub proxyに認証を任せる） |
| Setup script | 下記のとおり |

Setup script（環境設定ダイアログの Setup script 欄へ貼り付け）:

```bash
#!/bin/bash
apt update && apt install -y gh ripgrep || true
```

- セットアップ結果はスナップショットとしてキャッシュされ、以後のセッションは即座に同じ状態で始まる（約7日で自動再構築）。
- 追加パッケージが恒常的に必要になったら、この文書のSetup scriptを先に更新してから環境定義へ反映する（文書が正本、UI設定が写し）。
- プロジェクト固有の依存はここに足さず、対象repoの `.claude/settings.json` のSessionStart hookに置く。

## 初回セットアップ手順（アカウントに1回だけ）

1. claude.ai/code を開き、GitHubアカウント `sjinnouchi-ux` でClaude GitHub Appを承認する。対象のprivate repoへのアクセスを許可する。
2. 環境セレクタから **Add environment** を選び、上記の正本仕様どおりに `yumekango-standard` を作成する。
3. 既定環境を `yumekango-standard` に設定する。
4. 動作確認セッションを1つ作成し、下記Verificationを実行する。

## セッション運用ルール

- 1タスク = 1セッション。タスクの続きは新規セッションを作らず、同じセッションを開いて継続する（PCをまたいでよい）。
- セッション名から対象プロジェクトが分かるよう、最初の指示にプロジェクト名（`PROJECTS.md` のAlias）を含める。
- 完了したセッションはCleanup Gate確認後にアーカイブする。
- 障害時・特殊作業時は `claude --teleport <session-id>` でローカル端末へ引き込める。恒常運用にはしない。

## Verification

新規セッションで次を依頼する。

```text
共通起動手順とPROJECTS.mdをGitHub mainから取得し、取得したworkspace commit SHAと、
現在登録されているCanonical Entryの件数を報告してください。
あわせて gh --version と rg --version を報告し、GH_TOKEN の状態を
unset / proxy-injected / unexpected のいずれかの分類だけで報告してください。
値そのものは出力しないでください。
```

成功条件:

- raw GitHub URLを取得できる
- `sjinnouchi-ux/workspace` のcommit SHAを報告できる
- `gh` と `rg` が使える
- `GH_TOKEN` の状態が `unset` / `proxy-injected` / `unexpected` の分類だけで報告され、実token値が表示されない（`unexpected` の場合は作業を止めて報告）
- 対象private repoをcloneできる

## Setup Checklist

- [ ] GitHub App承認（private repo含む）
- [ ] 環境 `yumekango-standard` 作成（Trusted / 環境変数なし / Setup script設定）
- [ ] 既定環境に設定
- [ ] Verificationセッション成功
- [ ] デスクトップPC・ノートPC両方から同一セッションを開けることを確認
- [ ] 各プロジェクトrepoへ `CLAUDE.md`（`@AGENTS.md`）追加
