# code-exchange

Claude Desktop と Claude Code CLI の間でPythonコードをやり取りするためのリポジトリです。

## ワークフロー

```
Claude Desktop → [コード生成] → exchanges/*.md + *.json をpush
Claude Code CLI  → [git pull]  → コード読み取り・実行
ユーザー         → 「完成しました」と報告
Claude Code CLI  → [*.json 削除] → git push
```

## ディレクトリ構成

```
exchanges/
├── YYYYMMDD-NNN.md    # コード本体・説明（完了後も残る）
└── YYYYMMDD-NNN.json  # 実行待ちを示すメタデータ（完了時に削除）
```

## ファイル命名規則

| ファイル | 命名例 | 役割 |
|---------|--------|------|
| `.md`  | `20260519-001.md` | コード・説明・実行メモ |
| `.json` | `20260519-001.json` | ステータス管理（存在＝pending） |

JSONファイルが存在する間は「実行待ち（pending）」です。  
「完成しました」と報告するとJSONが削除され、mdのみ残ります。

## Claude Desktop 側の操作

新しいコードを登録するときは `manage.py new` で生成したテンプレートに記入し push します。

```bash
# 新しいやり取りを作成
python manage.py new "スクレイピングスクリプト"

# 一覧確認
python manage.py list
```

## Claude Code CLI 側の操作

```bash
# 最新化して実行待ちコードを確認
python manage.py list

# 完成報告（JSONを削除してpush）
python manage.py complete 20260519-001
```

## exchanges/template.md

新しいやり取りを作るときのテンプレートは `exchanges/template.md` を参照してください。
