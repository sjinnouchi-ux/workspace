# market-pilot 作業ログ

このファイルは market-pilot プロジェクトの作業履歴を時系列で記録する。
最新を上に追記する（逆時系列）。

---

## 2026-05-31 午後 Claude セッション（Supabase 設定）

### 実施内容（すべて完了）
- **Supabase プロジェクト新規作成**: 案A（専用プロジェクト新規）を採用
  - 組織: Yumekango（guyqarwmyjauzqcrxrnd）
  - プロジェクト名: **market-pilot**
  - **ref: qxnmzptdevelopmentid**
  - URL: https://qxnmzptdevelopmentid.supabase.co
  - リージョン: ap-northeast-1（東京） / Postgres 17 / 月額 $0（無料枠）
- **マイグレーション適用**（Supabase MCP の apply_migration で実行）
  - 20260531000001 stage_a_initial_schema … 6テーブル + 初期データ
  - 20260531000002 enable_rls_all_tables … 全テーブル RLS 有効化
- **検証 OK**
  - 6テーブル作成済み: tickers / strategy_rules / market_snapshots / signals / run_logs / notifications
  - tickers 8行（QQQ/XLE/XLV/XLF/GLD/TLT/BTC-USD/ETH-USD）
  - strategy_rules 7行（全 RESEARCH・notify_line=true）
  - **security advisor: 警告ゼロ**（RLS 有効化で rls_disabled エラー解消）

### RLS 方針（記録）
- 全6テーブルで RLS 有効。anon/authenticated 向けポリシーは未作成 = 外部アクセス全拒否。
- Python バッチは **service_role キー**で接続 → RLS をバイパスするため動作影響なし。
- anon キーが漏れてもテーブルは覗かれない安全構成。

### Python から接続する際に必要な情報（午後〜次回）
- SUPABASE_URL = https://qxnmzptdevelopmentid.supabase.co
- SUPABASE_SERVICE_ROLE_KEY = Supabaseダッシュボード → Project Settings → API → service_role secret から取得し **.env に格納**（GitHub 非コミット）
- ※ service_role キーは全権限。GitHub / Supabase DB / チャットに貼らない。.env のみ。

### 次の再開ポイント（Phase 1 Python 側）
1. .env に SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY を配置（陣内さん作業 or 手順提示）
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
  - Stage A 6テーブル: tickers / strategy_rules / market_snapshots / signals / run_logs / notifications
  - 初期データ: 8シンボル（QQQ/XLE/XLV/XLF/GLD/TLT + BTC-USD/ETH-USD）、戦略7種（全RESEARCH）
- **Supabase MCP コネクタを接続**（このチャットから直接 SQL 実行が可能になった）

### 申し送り（恒久ルール）
- LINEトークンの.env化は陣内さんが別途対応。本チャットでは平文のまま進行する
- credentials.json 等は GitHub 非コミット。APIキーは出金権限なし・.envのみ
- Desktop=GitHub WebUIコミット / CLI=git pull・push と実行。CLI手順は単一コピペブロックで提示

---

## 2026-05-29｜Codex→Claude向け再設計ブリーフ作成

### 背景・問題
- ETF・暗号資産を対象にした短期戦略研究、自動/手動売買、相関分析、AI月次レビューについて議論した内容をClaudeにも渡せるMarkdownとしてGitHubに出したいという依頼
- Google Sheetsを使わず、Supabaseを主DBにし、Pythonのブラウザ管理ターミナルを作る方針に変更

### 対応内容
- `docs/codex_to_claude_strategy_brief.md` を追加
- 設計思想、Supabase主DB方針、SBI/Coincheck/Binance API連携方針、相関分析、AI戦略レビュー、初期DB候補、実装フェーズを整理
- ユーザーが最重視する「毎月の結果・反省・次月戦略」タブを中核機能として明記

---

## 2026-05-28｜Supabase活用による大幅強化方針の調査・設計

### 背景・問題
- 株自動売買システムを読み込み、Supabaseも活用して大幅に強化したいという依頼
- 現状はGoogle SheetsをDB代わりに使っており、検索性・監査性・型安全性・エラー追跡に限界
- LINEトークンがスクリプト内に直書きされているため、秘密情報管理の見直しが必要

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
