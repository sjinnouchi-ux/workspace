# 実装計画

## Phase 1: 土台作成

- [x] GitHubにapi-monitorプロジェクトを作成
- [x] README.md・AGENTS.md・docsを整備
- [ ] `requirements.txt` を作成
- [ ] `.env.example` を作成
- [ ] SQLiteスキーマ設計（`db.py`）
- [ ] Streamlitアプリの骨格作成（`app.py`）

## Phase 2: APIクライアント実装

- [ ] OpenAIクライアント（`api_clients/openai_client.py`）
  - `usage` から `input_tokens` / `output_tokens` を取得
- [ ] Anthropicクライアント（`api_clients/claude_client.py`）
  - `usage` から `input_tokens` / `output_tokens` を取得
- [ ] Geminiクライアント（`api_clients/gemini_client.py`）
  - `usage_metadata` から `prompt_token_count` / `candidates_token_count` を取得
- [ ] 3社共通インターフェース確認・テスト

## Phase 3: モニタータブ実装

- [ ] サマリー指標カード（今月費用・総トークン・コール数・最多モデル）
- [ ] 日別費用推移グラフ（3社重ね折れ線）
- [ ] サービス別費用比率（ドーナツグラフ）
- [ ] APIコール履歴テーブル

## Phase 4: 設定タブ実装

- [ ] APIキー管理UI（マスク表示・コピー・表示切替・新規登録）
- [ ] API用途カスタマイズUI（プロジェクト×モデル×用途メモ）
- [ ] 設定のSQLite保存・読み込み

## Phase 5: 安定化

- [ ] エラーハンドリング（APIキー未設定時の案内表示）
- [ ] 費用計算の精度確認（各社の料金表と照合）
- [ ] Mac起動時の自動起動設定（launchd or 手動）
- [ ] `.gitignore` で `.env` と `data/` を除外確認

## Phase 6: 3社API利用実績の自動取得

### 方針

現在のアプリは、アプリ内の `api_clients/*_client.py` を経由したAPI呼び出しだけをSQLiteへ記録する設計である。
今後はこれを、OpenAI / Anthropic Claude / Google Gemini の各プロバイダー側にあるusage/billing情報を取得し、利用実績としてモニターへ同期する設計へ拡張する。

費用単価テーブルは補助計算用とし、プロバイダー側からcostが取得できる場合は公式usage/cost値を正とする。

### タスク

- [ ] 取得対象の定義
  - 表示単位：日別、サービス別、モデル別、APIキー別、プロジェクト別
  - 同期方式：手動更新、起動時更新、定期更新
- [ ] SQLiteスキーマ追加
  - `provider_usage_snapshots` または `provider_cost_logs` を追加
  - 候補カラム：`provider`, `date`, `model`, `project_id`, `api_key_id`, `input_tokens`, `output_tokens`, `cost_usd`, `currency`, `source`, `synced_at`
  - 重複防止キー：`provider + date + model + project/api_key`
- [ ] OpenAI同期クライアント
  - OpenAI Admin/Usage/Costs APIからusage/costを取得
  - 必要設定：OpenAI Admin API key、必要に応じてOrganization ID
- [ ] Anthropic Claude同期クライアント
  - Anthropic Usage & Cost Admin APIからusage/costを取得
  - 必要設定：Anthropic Admin API key（`sk-ant-admin...`）
  - 個人アカウントで利用できない場合は、画面に権限不足として明示
- [ ] Gemini同期クライアント
  - Google Cloud Billing Export to BigQueryを利用してGemini API費用を取得
  - 必要設定：GCP project ID、billing export dataset、BigQuery read権限、サービスアカウント認証
  - AI Studio / Cloud Billing側の反映遅延を画面に表示
- [ ] 設定タブ改修
  - APIキー登録中心の画面から、接続設定・同期状態・接続確認中心の画面へ変更
  - 各社ごとに最終同期日時、同期エラー、接続確認結果を表示
- [ ] モニタータブ改修
  - ローカル呼び出しログとprovider同期データを区別して集計
  - データ取得元を表示：OpenAI Usage API / Anthropic Usage API / Google Cloud Billing BigQuery
- [ ] 検証
  - OpenAI：公式ダッシュボードと当月costが近いことを確認
  - Claude：Claude ConsoleのUsage and Costと同期結果を照合
  - Gemini：AI StudioまたはCloud Billing表示とBigQuery集計を照合
- [ ] ドキュメント更新
  - READMEを「登録型」ではなく「3社usage同期型」の説明へ更新
  - work_logに実装結果、制約、未解決事項を記録

## 費用単価メモ（2026年5月時点）

| モデル | 入力 (/1Mトークン) | 出力 (/1Mトークン) |
|--------|-----------------|-----------------|
| gpt-4o-mini | $0.15 | $0.60 |
| claude-haiku-4-5 | $0.80 | $4.00 |
| claude-opus-4-7 | $5.00 | $25.00 |
| gemini-1.5-flash | $0.075 | $0.30 |

※ 料金は変動するため、Phase5で最新単価を確認して更新すること
