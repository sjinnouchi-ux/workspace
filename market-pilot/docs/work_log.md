# market-pilot 作業ログ

このファイルは market-pilot プロジェクトの作業履歴を時系列で記録する。
最新を上に追記する（逆時系列）。

---

## 2026-05-31 午後 Claude セッション（Supabase 設定 — 完了）

### 完了内容（実データで検証済み）
- Supabase コネクタを **read-write で再接続**し、書き込み権限を確認。
- **market-pilot 専用プロジェクトを新規作成**（案A）。
  - 組織: Yumekango（guyqarwmyjauzqcrxrnd）
  - プロジェクト名: **market-pilot**
  - **ref: bxhfqmeltavkpkratmfr**
  - DB host: db.bxhfqmeltavkpkratmfr.supabase.co
  - URL: https://bxhfqmeltavkpkratmfr.supabase.co
  - リージョン: ap-northeast-1（東京） / Postgres 17 / 月額 $0（無料枠） / ACTIVE_HEALTHY
- **マイグレーション適用（2本・成功）**
  - stage_a_initial_schema … 6テーブル + 初期データ
  - enable_rls_all_tables … 全テーブル RLS 有効化
- **検証 OK（実データ確認）**
  - 6テーブル: tickers / strategy_rules / market_snapshots / signals / run_logs / notifications
  - tickers 8行: QQQ/XLE/XLV/XLF/GLD/TLT/BTC-USD/ETH-USD
  - strategy_rules 7行: 全 RESEARCH・notify_line=true
  - market_snapshots/signals/run_logs/notifications は 0行（想定通り、これから記録）
  - **security advisor: 警告ゼロ（lints: []）**

### RLS 方針（記録）
- 全6テーブル RLS 有効・ポリシー未作成 = anon/authenticated は外部アクセス全拒否。
- Python バッチは **service_role キー**で接続 → RLS バイパス（動作影響なし）。

### Python から接続する際に必要な情報
- SUPABASE_URL = https://bxhfqmeltavkpkratmfr.supabase.co
- SUPABASE_SERVICE_ROLE_KEY = Supabaseダッシュボード（market-pilot） → Project Settings → API → service_role secret から取得し **.env に格納**（GitHub 非コミット・チャットに貼らない）

### 次の再開ポイント（Phase 1 Python 側）
1. .env に SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY を配置
2. requirements.txt に supabase / python-dotenv 追加
3. scripts/lib/ 共通モジュール作成（config / supabase_client / indicators / line_notify / universe）
4. ユニバースを8銘柄に拡張
5. 06_daily_report.py に Supabase 記録を追加（§10 準拠: シグナル理由・異常値INVALID・run_logs厚め）。**LINE通知挙動は維持。トークンは平文のまま=陣内さんが別途.env化**

---

## 2026-05-31 午前 Claude セッション

### 実施内容
- 設計書 v2 を確定し、§10「堅牢性・データ品質要件」を追記（commit 7b5803f1）
  - §10.1 シグナル理由を必ず保存（reason_text + reason_detail JSONB）
  - §10.2 異常値ガード（価格0/前日比±20%/欠損/RSI計算不能 → INVALID）
  - §10.3 run_logs を厚めに保存（run_id で束ね、銘柄/戦略別の部分失敗を可視化）
  - §10.4 初期は全戦略 RESEARCH 扱い（通知は可）
- Phase 1 の DB マイグレーション `supabase/migrations/001_initial.sql` を作成・コミット（commit d7faa567）
  - Stage A 6テーブル / 8シンボル / 戦略7種（全RESEARCH）
- Supabase MCP コネクタを接続（最初 read-only でブロック → 午後 read-write で再接続し解決）

### 申し送り（恒久ルール）
- LINEトークンの.env化は陣内さんが別途対応。本チャットでは平文のまま進行する
- credentials.json 等は GitHub 非コミット。APIキーは出金権限なし・.envのみ
- Desktop=GitHub WebUIコミット / CLI=git pull・push と実行。CLI手順は単一コピペブロックで提示

---

## 2026-05-29｜Codex→Claude向け再設計ブリーフ作成

### 対応内容
- `docs/codex_to_claude_strategy_brief.md` を追加
- 設計思想、Supabase主DB方針、API連携方針、相関分析、AI戦略レビュー、初期DB候補、実装フェーズを整理
- ユーザーが最重視する「毎月の結果・反省・次月戦略」タブを中核機能として明記

---

## 2026-05-28｜Supabase活用による大幅強化方針の調査・設計

### 対応内容
- `README.md`, `CLAUDE.md`, `SPREADSHEET.md`, `scripts/06_daily_report.py`, `scripts/07_scan.py`, `scripts/03_backtest.py` を確認
- `docs/supabase_enhancement_plan.md` を作成し、段階移行方針、DB設計案、実装ステップを整理

---

## 2026-05-19｜Mac移行・cron設定

### 対応内容
- WindowsタスクスケジューラからMac cronへ移行（スリープ中に実行されない問題の解消）
- `credentials.json` を `~/Library/Application Support/gspread/credentials.json` に配置
- 作業ディレクトリを `/Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/` に統一
- cron設定（毎日 07:00 / 22:30 に 06_daily_report.py を実行、logs/daily.log に出力）

### 環境情報
- Python: 3.13.3（pyenv） / 実行パス: `/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- gspread: 6.2.1 / yfinance: 1.3.0
