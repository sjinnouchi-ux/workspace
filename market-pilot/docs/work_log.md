# market-pilot 作業ログ

このファイルは market-pilot プロジェクトの作業履歴を時系列で記録する。
最新を上に追記する（逆時系列）。

---

## 2026-05-31 午後 Claude セッション（Supabase 設定 — 一部ブロック中）

### 方針決定（確定）
- Supabase は **案A：market-pilot 専用プロジェクトを新規作成**で進める（陣内さん承認済み・月額$0）。
- 組織: Yumekango（guyqarwmyjauzqcrxrnd）/ 想定リージョン: ap-northeast-1 / 想定名: market-pilot
- RLS 方針: 全テーブル RLS 有効・ポリシー未作成（外部全拒否）。Python は service_role で接続しバイパス。

### 発生したブロッカー（重要）
- **Supabase MCP コネクタが read-only モード**で接続されている。
- そのため `create_project` / `apply_migration` / `execute_sql` / `list_tables` 等の書き込み・実行系がすべて
  `MCP error -32600: You do not have permission to perform this action` で失敗。
- 読み取り系（list_organizations / list_projects / get_cost）のみ成功。
- → **プロジェクト作成も 001_initial.sql 適用もまだ未完了**（この時点で DB は空のまま）。

### 解除に必要な対応（陣内さん）
- Supabase コネクタを **書き込み可能（read-write）** で再接続する。
  - Claude デスクトップのコネクタ設定で Supabase を一度切断 → 再接続時に read-only オプションを外す
  - または Supabase 側で MCP 用アクセストークンを full-access で再発行
- 解除後、Claude 側で create_project → apply_migration → 検証 を一括実行する。

### 代替案（コネクタ権限を変えたくない場合）
- 既存の手順（GitHub の 001_initial.sql）を **Supabase Web SQL Editor に貼って Run** すれば手動で適用可能。
  - その場合もプロジェクトは陣内さんが先に手動作成する必要あり。

### 次の再開ポイント
1. Supabase コネクタを read-write で再接続（または手動でプロジェクト作成＋SQL適用）
2. 001_initial.sql 適用 → 6テーブル / tickers 8行 / strategy_rules 7行 を検証
3. RLS 有効化マイグレーション適用
4. Phase 1 Python 側（lib共通化 / ユニバース8銘柄 / 06_daily_report.py に Supabase 記録）

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
- **Supabase MCP コネクタを接続**（ただし read-only。書き込みは午後ブロックされた）

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
