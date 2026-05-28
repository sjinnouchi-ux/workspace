# AGENTS.md — api-monitor

## プロジェクト概要

OpenAI・Anthropic・Google の3社APIをStreamlitで一元監視するダッシュボード。
ローカルMac上で起動し、ブラウザからアクセスする。

## 作業開始時の必読ファイル

1. `README.md` — プロジェクト全体像・構成・起動方法
2. `docs/work_log.md` — 直近の作業履歴・残課題
3. `docs/implementation_plan.md` — フェーズ別実装計画と進捗

## ディレクトリ構成と役割

| パス | 役割 |
|------|------|
| `app.py` | Streamlitエントリーポイント。タブ切り替えのみ担当 |
| `db.py` | SQLite操作（テーブル作成・ログ挿入・取得） |
| `monitor.py` | モニタータブのUI・グラフ描画 |
| `settings.py` | 設定タブのUI（APIキー管理・用途カスタマイズ） |
| `api_clients/` | 各社APIクライアント。usageを返す統一インターフェース |
| `.env` | APIキー（Gitignore済み・手動作成） |

## コーディングルール

- Python 3.13 対応で書く（`/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`）
- パッケージインストールは `pip install --break-system-packages`
- 各APIクライアントは `call(prompt, model)` → `{"content": str, "usage": {...}}` の統一形式で返す
- APIキーは `.env` から `python-dotenv` で読み込む。ハードコード禁止
- SQLiteのDBファイルは `data/api_log.db` に保存
- Streamlitの `st.secrets` は使わず `.env` + `python-dotenv` で統一

## 禁止事項

- APIキー・シークレットをGitHubへpushしない
- `.env` ファイルをコミットしない（`.gitignore` 確認済み）

## 作業完了後

- `docs/work_log.md` に作業内容・残課題を記録してGitHubへpush
