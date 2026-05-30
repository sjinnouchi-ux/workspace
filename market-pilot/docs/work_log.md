# market-pilot 作業ログ

このファイルは market-pilot プロジェクトの作業履歴を時系列で記録する。
最新を上に追記する（逆時系列）。

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

### Supabase 接続の記録（重要・申し送り）
- 接続済み MCP: Supabase（公式コネクタ）
- 組織: **Yumekango**（id: guyqarwmyjauzqcrxrnd）
- 既存プロジェクト: **dori-manga のみ**（id/ref: vdntqwtywxyjxelycavx, region: ap-northeast-1, Postgres 17, ACTIVE_HEALTHY, 作成 2026-05-26）
- **未決事項**: market-pilot 専用プロジェクトが無い。無料枠は1プロジェクトのため、午後に下記を要判断。
  - 案A: 既存 `dori-manga` プロジェクトに market-pilot 用テーブルを相乗り（スキーマ分離 or テーブル名prefix）
  - 案B: 別アカウント/別組織で market-pilot 専用プロジェクトを新規作成
- ※ 001_initial.sql はまだ **どのプロジェクtrにも未適用**。プロジェクト方針を決めてから apply_migration / execute_sql で流す。

### 午後の再開ポイント（TODO）
1. Supabase プロジェクト方針を決定（案A or 案B）
2. 決定したプロジェクトに 001_initial.sql を適用（Supabase MCP の apply_migration で実行可能）
3. 適用後の検証: tickers 8行 / strategy_rules 7行 / 6テーブル存在を確認
4. Phase 1 Python 側に着手:
   - scripts/lib/ 共通モジュール（config / supabase_client / indicators / line_notify / universe）
   - ユニバースを8銘柄に拡張
   - 06_daily_report.py に Supabase 記録を追加（**LINE通知挙動は維持。トークンは平文のまま=陣内さんが別途.env化**）

### 申し送り（恒久ルール）
- LINEトークンの.env化は陣内さんが別途対応。本チャットでは平文のまま進行する
- credentials.json 等は GitHub 非コミット。APIキーは出金権限なし・.envのみ
- Desktop=GitHub WebUIコミット / CLI=git pull・push と実行。CLI手順は単一コピペブロックで提示

---

## 2026-05-29 Codex セッション

### 実施内容
- QQQ トレーディングシステムの現状整理
- Supabase 移行構想の検討
- Claude への引き継ぎ資料作成（codex_to_claude_strategy_brief.md）

### 引き継ぎ事項
- 短期戦略研究 + 小口自動執行 + 手動承認トレードの基盤を作る
- 相関分析を中核に据える
- 月次 AI レビューを最重要機能とする

---
