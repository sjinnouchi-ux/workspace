# workspace

陣内 聡（株式会社ゆめ看護）の全体管理Gitです。

このリポジトリは、各プロジェクトGitへの**ルーター（索引）**として使います。詳細な設計、実装、作業ログ、運用手順は各プロジェクトGitに置き、このリポジトリには「どのプロジェクトを見るべきか」「現役か凍結か」「設計/実装の担当CLIは何か」を記録します。

## 読む順番

1. `PROJECTS.md` で該当プロジェクトを探す。
2. `PROJECTS.md` の `Repo / Path` に書かれたプロジェクトGitへ移動する。
3. プロジェクトGitの `PROJECT_BRIEF.md`、`DESIGN_LOG.md`、`IMPLEMENTATION_LOG.md` を読む。
4. 外部ツール、MCP、MiniPC、認証、バックアップ方針が必要な場合は `MCP.md` を読む。
5. 設計者と実装者の分担を確認する場合は `docs/workflow-design-implementation.md` を読む。

## 新しい運用方針

- 全体管理Gitはルーターに徹する。
- Notionは通常の進捗管理には使わない。
- 旧JSONインデックスは廃止済み。新方式の正本は `PROJECTS.md` と各プロジェクトGitのMarkdownとする。
- Shogunが自動生成するルート `CLAUDE.md` / `AGENTS.md` は、この全体管理Gitでは手書き正本にしない。
- 各プロジェクトGit側の `CLAUDE.md` / `AGENTS.md` は、プロジェクト固有ルールとして手書きしてよい。
- 秘密情報はGitHub、Markdown、チャットに保存しない。

## エージェント構成

- 基盤: multi-agent-shogun（常時起動のWindows MiniPC上で稼働予定）
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
docs/workflow-design-implementation.md
```

## GitHub

Repository:

```text
https://github.com/sjinnouchi-ux/workspace
```
