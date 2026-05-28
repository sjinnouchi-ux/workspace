# Supabase強化計画

## 背景
market-pilotは現在、Google Sheetsを設定・売買ログ・バックテスト結果の保存先として使い、Mac cronからPythonスクリプトを実行してLINE通知する構成である。

この構成は小さく始めるには扱いやすい一方で、銘柄数、履歴データ、バックテスト条件、通知履歴、エラー監視、将来の自動売買連携を増やすほど、Google Sheetsだけではデータ整合性・検索性・監査性が弱くなる。

Supabaseはまず「取引・シグナル・実行履歴の中核DB」として導入し、Google Sheetsは閲覧・手入力用の補助UIとして残す段階移行が安全。

## 現状整理

### 既存構成
- 実行基盤: Mac cron
- メイン通知: `scripts/06_daily_report.py`
- 多銘柄スキャン: `scripts/07_scan.py`
- バックテスト: `scripts/03_backtest.py`
- 設定・売買ログ: Google Sheets
- 通知: LINE Messaging API broadcast
- 価格データ: yfinance

### 現状の強み
- cronとLINE通知がすでに動く
- Google Sheetsで設定・売買ログを人間が編集しやすい
- QQQ/GLDから多銘柄スキャンへ拡張する基礎がある
- バックテスト用スクリプトが分離されている

### 優先して直すべきリスク
- LINEトークンがPythonファイル内に直書きされている
- 実行失敗時のLINE通知・永続ログが弱い
- 売買ログの列順にコードが強く依存している
- シグナル履歴が保存されず、後から検証しにくい
- Google SheetsがDBになっており、型・制約・検索・集計に限界がある
- `06_daily_report.py` と `07_scan.py` に重複ロジックが多い

## Supabase導入方針

### Phase 1: 記録基盤の追加
現行cron/Python/Google Sheets/LINEは維持し、Supabaseへ以下を保存する。

- 毎回の実行結果
- 各銘柄の価格・RSI・MA・BB・シグナル判定
- 保有銘柄の評価損益
- LINE通知内容と送信ステータス
- エラー内容

この段階では売買判断の挙動を変えない。後から「なぜその通知が出たか」を追跡できる状態にする。

### Phase 2: Google Sheets依存の縮小
Google SheetsからSupabaseへ主データを移す。

- 銘柄リスト
- 売買ログ
- ルール設定
- バックテスト結果

Google Sheetsは手入力・閲覧・簡易ダッシュボード用途に限定し、必要に応じてSupabaseから同期する。

### Phase 3: ダッシュボードと分析強化
Supabase上の履歴を使い、以下を追加する。

- シグナル発生履歴の勝率検証
- 銘柄別パフォーマンス
- ルール別バックテスト比較
- NISA枠消化状況
- 通知履歴と未対応シグナル管理
- Webダッシュボード

### Phase 4: 実行基盤の強化
Mac cronだけに依存せず、Supabase CronやEdge Functionsも検討する。

ただしyfinance取得やPython分析処理は既存Pythonの方が扱いやすいため、最初はMac cronを残す。Supabase側のCron/Edge Functionsは、軽量な集計、通知再送、ヘルスチェック、Webhook受信から始める。

## 推奨DB設計案

### `tickers`
対象銘柄マスタ。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| symbol | text | QQQ, GLDなど |
| name | text | 銘柄名 |
| market | text | US, JPなど |
| asset_class | text | ETF, stock, commodityなど |
| enabled | boolean | スキャン対象か |
| memo | text | 備考 |
| created_at | timestamptz | 作成日時 |
| updated_at | timestamptz | 更新日時 |

### `strategy_rules`
売買ルール管理。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| name | text | ルール名 |
| is_active | boolean | 現在有効か |
| rsi_buy_threshold | numeric | RSI買い閾値 |
| rsi_sell_threshold | numeric | RSI売り閾値 |
| ma_short | integer | 短期MA |
| ma_middle | integer | 中期MA |
| ma_long | integer | 長期MA |
| profit_take_pct | numeric | 利確ライン |
| stop_loss_pct | numeric | 損切りライン |
| investment_jpy | numeric | 1回投資額 |
| fee_rate_pct | numeric | 手数料率 |
| created_at | timestamptz | 作成日時 |

### `market_snapshots`
スキャンごとの銘柄状態。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| run_id | uuid | 実行単位 |
| symbol | text | 銘柄 |
| observed_at | timestamptz | 観測日時 |
| close_usd | numeric | 終値 |
| volume | numeric | 出来高 |
| rsi | numeric | RSI |
| ma_short | numeric | 短期MA |
| ma_middle | numeric | 中期MA |
| ma_long | numeric | 長期MA |
| bb_upper | numeric | ボリンジャー上限 |
| usd_jpy | numeric | 為替 |
| raw | jsonb | 元データ補足 |

### `signals`
売買シグナル履歴。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| run_id | uuid | 実行単位 |
| symbol | text | 銘柄 |
| signal_type | text | buy, sell, hold |
| strength | text | weak, normal, strong |
| reasons | jsonb | 判定理由 |
| action_hint | text | 購入検討、売却検討など |
| price_usd | numeric | 判定時価格 |
| created_at | timestamptz | 作成日時 |

### `positions`
保有ポジション。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| symbol | text | 銘柄 |
| account_type | text | NISA, 特定口座など |
| shares | numeric | 株数 |
| buy_date | date | 買付日 |
| buy_price_usd | numeric | 買付単価 |
| buy_fx_rate | numeric | 買付時為替 |
| sell_date | date | 売却日 |
| sell_price_usd | numeric | 売却単価 |
| status | text | open, closed |
| memo | text | 備考 |

### `run_logs`
スクリプト実行履歴。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| script_name | text | 実行スクリプト |
| started_at | timestamptz | 開始 |
| finished_at | timestamptz | 終了 |
| status | text | success, failed, partial |
| scanned_count | integer | スキャン数 |
| signal_count | integer | シグナル数 |
| error_message | text | エラー |
| metadata | jsonb | 補足 |

### `notifications`
通知履歴。

| カラム | 型 | 内容 |
|---|---|---|
| id | uuid | 主キー |
| run_id | uuid | 実行単位 |
| channel | text | lineなど |
| title | text | 通知タイトル |
| body | text | 通知本文 |
| status | text | sent, failed |
| response_code | integer | APIレスポンス |
| sent_at | timestamptz | 送信日時 |

## 実装ステップ

### Step 1: 秘密情報の外出し
- `.env.example` を追加
- `LINE_TOKEN`, `SPREADSHEET_ID`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` を環境変数化
- 既存のLINEトークンは漏えい済みとして再発行する

### Step 2: Supabase接続モジュール追加
- `scripts/lib/config.py`
- `scripts/lib/supabase_client.py`
- `scripts/lib/indicators.py`
- `scripts/lib/line_notify.py`

既存スクリプトの重複ロジックを段階的に共通化する。

### Step 3: マイグレーションSQL追加
- `supabase/migrations/001_initial_market_pilot.sql`
- 主要テーブル、インデックス、RLS、service role向け権限を定義する

### Step 4: 実行ログとシグナル保存
- `06_daily_report.py` に `run_logs`, `market_snapshots`, `signals`, `notifications` への保存を追加
- エラー時も `run_logs.status = failed` として残し、可能ならLINE通知する

### Step 5: 多銘柄スキャンのDB化
- `07_scan.py` の結果をSupabaseに保存
- シグナルのみ通知し、詳細はDBで確認できるようにする

### Step 6: バックテスト結果のDB化
- `03_backtest.py` の結果をSupabaseに保存
- ルール別・銘柄別に比較できる形にする

### Step 7: ダッシュボード
- 最初はSupabase Studioで確認
- 次にStreamlitまたは軽量Webアプリで可視化

## 次回実装で最初に行うこと
1. SupabaseプロジェクトのURLとキーの配置方法を決める
2. LINEトークンを再発行して環境変数化する
3. `supabase/migrations/001_initial_market_pilot.sql` を作る
4. `requirements.txt` に `supabase` と `python-dotenv` を追加する
5. `06_daily_report.py` に実行ログ保存だけを追加して、通知挙動は変えずに検証する

## 参考にしたSupabase公式情報
- Pythonクライアント: `supabase-py`
- Edge Functions: TypeScript/Denoのサーバーサイド関数
- Supabase Cron: Postgresの `pg_cron` を利用した定期実行
- Edge Function Secrets: 秘密情報を環境変数として扱う仕組み
- Database Webhooks: テーブル変更をHTTP通知できる仕組み
