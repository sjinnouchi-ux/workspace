# APIモニター 作業ログ

---

## 2026-05-28｜プロジェクト初期化

### 背景

- KアラートプロジェクトでOpenAI APIを使い始めたことを契機に、API利用費用の可視化ニーズが発生
- 将来的にOpenAI・Anthropic・Googleの3社を使い分ける想定のため、一元管理ダッシュボードを構築する
- Streamlit（Python）＋SQLiteで構築し、ローカルMacで起動する方針に決定

### 対応内容

- `api-monitor/` プロジェクトをGitHubに作成
- `README.md` にプロジェクト概要・構成・セットアップ手順を記載
- `AGENTS.md` にAIエージェント向けの作業ガイドラインを記載
- `docs/implementation_plan.md` にPhase1〜5の実装計画を記載
- `docs/work_log.md`（本ファイル）を作成

### 設計決定事項

- **データ保存**：SQLite（`data/api_log.db`）。外部サービス不要でシンプルに管理
- **APIキー管理**：`.env` + `python-dotenv`。GAS Script Propertiesとは分離
- **画面構成**：モニタータブ（可視化）＋設定タブ（APIキー・用途管理）の2タブ構成
- **対応3社**：OpenAI・Anthropic・Google を初回から同時接続
- **コーディングモデル**：Claude Opus 4.7 を使用（コーディング性能が最高水準）

### 残課題

- [ ] Phase 1: 土台コード作成（`app.py`, `db.py`, `requirements.txt`, `.env.example`）
- [ ] Phase 2: 3社APIクライアント実装
- [ ] Phase 3: モニタータブUI実装
- [ ] Phase 4: 設定タブUI実装
- [ ] Phase 5: 安定化・費用単価の最新化
