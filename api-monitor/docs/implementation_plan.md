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

## 費用単価メモ（2026年5月時点）

| モデル | 入力 (/1Mトークン) | 出力 (/1Mトークン) |
|--------|-----------------|-----------------|
| gpt-4o-mini | $0.15 | $0.60 |
| claude-haiku-4-5 | $0.80 | $4.00 |
| claude-opus-4-7 | $5.00 | $25.00 |
| gemini-1.5-flash | $0.075 | $0.30 |

※ 料金は変動するため、Phase5で最新単価を確認して更新すること
