# workspace

陣内 聡（株式会社ゆめ看護）の全体管理Gitです。

このリポジトリは、各プロジェクトGitへの**ルーター（索引）**として使います。詳細な設計、実装、作業ログ、運用手順は各プロジェクトGitに置き、このリポジトリには「どのプロジェクトを見るべきか」「現役か凍結か」「設計/実装の担当CLIは何か」を記録します。

## 読む順番

1. Codex Desktopは `codex/CODEX_DESKTOP_STARTUP.md` をGitHub `main` から取得する。
2. `PROJECTS.md` で該当プロジェクトを探す。
3. `PROJECTS.md` の `Canonical Entry` に書かれたGitHubへ移動する。
4. 対象repoの `AGENTS.md` と `Primary Docs` を読む。
5. 外部ツール、MCP、認証、バックアップ方針が必要な場合は `MCP.md` を読む。
6. 設計者と実装者の分担を確認する場合は `docs/workflow-design-implementation.md` を読む。

## 新しい運用方針

- 全体管理Gitはルーターに徹する。
- Notionは通常の進捗管理には使わない。
- 旧JSONインデックスは廃止済み。新方式の正本は `PROJECTS.md` と各プロジェクトGitのMarkdownとする。
- Codex Desktopの共通起動手順とパーソナライズ文面は `codex/` に置く。
- Shogunが自動生成するルート `CLAUDE.md` / `AGENTS.md` は、この全体管理Gitでは手書き正本にしない。
- 各プロジェクトGit側の `CLAUDE.md` / `AGENTS.md` は、プロジェクト固有ルールとして手書きしてよい。
- 秘密情報はGitHub、Markdown、チャットに保存しない。

## エージェント構成

- 基盤: multi-agent-shogun（WSL2 Linuxで起動しWebUIから利用予定。Codex Desktop整備後に同じGitHub運用へ改修）
- 要件定義・設計: Claude割当エージェント
- 実装・検証・デプロイ: Codex割当エージェント
- 家計簿LIFF FastAPI化を最初のパイロットとして扱う。

詳細は `docs/workflow-design-implementation.md` を参照してください。

## 未登録プロジェクトが出たとき

ユーザー発言のプロジェクトが `PROJECTS.md` にない場合、勝手に新規作成も凍結扱いもしません。

次のように確認します。

```text
このプロジェクトはPROJECTS.mdに見つかりませんでした。
凍結/保管扱いですか、それとも新規プロジェクトとして追加しますか？
```

## 主要ファイル

```text
README.md
PROJECTS.md
MCP.md
codex/CODEX_DESKTOP_STARTUP.md
codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md
docs/workflow-design-implementation.md
```

## GitHub

Repository:

```text
https://github.com/sjinnouchi-ux/workspace
```
