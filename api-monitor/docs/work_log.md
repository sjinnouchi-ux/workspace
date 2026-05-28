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

---

## 2026-05-28｜Phase 1〜2 実装完了（Claude Desktop / Cowork）

### 対応内容

#### Phase 1（土台）

- `requirements.txt` — streamlit / openai / anthropic / google-generativeai / python-dotenv / pandas / plotly
- `.env.example` — 3社APIキーのテンプレート
- `api-monitor/.gitignore` — `data/` `*.db` `.venv/` 等を追加除外（rootの`.env`除外と併用）
- `db.py` — SQLite層を実装
  - テーブル：`api_call_logs` / `api_keys` / `api_settings`
  - 関数：`init_db`, `insert_call_log`, `fetch_call_logs`, `summary_current_month`,
    `daily_cost_by_service`, `service_cost_share`,
    `upsert_api_key`, `get_api_key`, `list_api_keys`, `delete_api_key`,
    `upsert_setting`, `list_settings`, `delete_setting`
  - DBパスは `API_MONITOR_DB_PATH` で上書き可能。デフォルトは `data/api_log.db`
- `app.py` — Streamlitエントリーポイント。タブ切り替えのみ
- `monitor.py` — モニタータブのMVP（指標カード・日別費用折れ線・サービス別棒・最新50件履歴）
- `settings.py` — 設定タブのMVP（APIキー管理 / 用途カスタマイズフォーム）

#### Phase 2（3社APIクライアント）

- `api_clients/__init__.py` — 共通インターフェース定義
  - `Usage` / `CallResult` (TypedDict)
  - `MODEL_PRICING` 表（USD/1Mトークン、入力・出力別）
  - `calc_cost(service, model, input_tokens, output_tokens) -> float`
- `api_clients/openai_client.py` — `call()` → `chat.completions.create`
  - `usage.prompt_tokens` / `usage.completion_tokens` 取得
- `api_clients/claude_client.py` — `call()` → `messages.create`
  - `usage.input_tokens` / `usage.output_tokens` 取得
- `api_clients/gemini_client.py` — `call()` → `GenerativeModel.generate_content`
  - `usage_metadata.prompt_token_count` / `usage_metadata.candidates_token_count` 取得
- いずれもエラー時も `api_call_logs` に `status='error'` で記録（失敗の見える化）
- APIキー解決順：DB登録キー → `.env` の環境変数

### 設計上の決定

- API呼び出しは **DB側で `service`, `model`, `input/output_tokens`, `cost_usd`, `response_ms` まで自動記録** する設計に統一
- `MODEL_PRICING` に料金単価を集約。Phase 5で公式単価と照合して更新
- 未登録モデルが来ても `cost_usd=0.0` でログは残す（後追いで補正可能にする）
- Streamlitのcaching/secretsは使わず、`db.get_api_key()` と `.env` のみで完結
- pyenv `3.13.3` を前提に `--break-system-packages` でインストール

### 動作確認手順

1. CLI側で `git pull`
2. `pip install -r api-monitor/requirements.txt --break-system-packages`
3. `cp api-monitor/.env.example api-monitor/.env` してAPIキー記入
4. `cd api-monitor && python3 db.py` でDB初期化（`data/api_log.db` 生成）
5. `streamlit run app.py` → `http://localhost:8501` を開く

### 残課題（Phase 3〜5）

- [ ] Phase 3: モニタータブのグラフをplotlyに置換（ドーナツ・重ね折れ線）
- [ ] Phase 4: APIキーのコピー UI（マスク・表示切替は実装済み、ワンクリックコピー追加）
- [ ] Phase 4: 用途カスタマイズの編集・削除UI
- [ ] Phase 5: launchd でMac起動時自動起動
- [ ] Phase 5: 費用単価の最新化＆公式単価との突合
- [ ] テスト：実APIキーで1回ずつ `call()` してログ記録を確認
