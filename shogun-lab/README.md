# Shogun（仮）

Shogun（仮）は、multi-agent-shogun で作成した設計Markdownを、Codexが実行できる形で受け渡すための中継プロジェクトです。

このフォルダは既存プロジェクトの実装コード置き場ではありません。Shogunで設計・分解した内容をMarkdownとして保存し、Codexが対象リポジトリや対象サービスへ実行・検証・報告するための引継ぎ場所として使います。

## 役割分担

- GitHub/Markdown: Shogun設計MD、Codex実行ログ、検証結果、引継ぎ記録の正本
- 全体管理Git: `PROJECTS.md` から対象プロジェクトGitへ案内するルーター
- Shogun: 要件整理、設計、タスク分解、実行用Markdownの作成
- Codex: Shogun設計MDを読み、対象リポジトリ・外部サービス・ローカル環境で実行、検証、報告

## フォルダ構成

```text
shogun-lab/
  README.md
  AGENTS.md
  docs/
    work_log.md
    setup_status.md
  handoffs/
    README.md
  codex-execution/
    README.md
  templates/
    shogun-to-codex-handoff.md
```

## 運用ルール

1. Shogunで作成した設計MDは `handoffs/YYYY-MM-DD-<topic>.md` に保存する。
2. Codexは実行前に対象プロジェクトの `AGENTS.md` と、このフォルダの `AGENTS.md` を読む。
3. Codex実行後は `codex-execution/YYYY-MM-DD-<topic>-result.md` に、実行内容・変更ファイル・検証結果・未完了事項を書く。
4. 実装対象が既存プロジェクトの場合、詳細ログは対象プロジェクト側の `docs/work_log.md` にも追記する。
5. このフォルダには秘密情報、`.env`、APIキー、OAuthトークンを保存しない。

## 現在の状態

- ステータス: 仮運用準備
- 最初の用途: multi-agent-shogun の設計MDをCodex実行へ引き継ぐ
- Shogunローカル実体: `C:\tools\multi-agent-shogun`
- Shogun WSLパス: `/mnt/c/tools/multi-agent-shogun`
- 次アクション: Shogunで作成する設計MDを `templates/shogun-to-codex-handoff.md` に沿って保存し、Codex実行ログと対応づける
