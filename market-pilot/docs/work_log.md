# 作業ログ

今後の依頼・対応内容をすべてここに記録する。
不明点が出た際は過去ログを参照すること。

---

## 2026-05-28｜Supabase活用による大幅強化方針の調査・設計

### 背景・問題
- 株自動売買システムを読み込み、Supabaseも活用して大幅に強化したいという依頼
- 現状はGoogle SheetsをDB代わりに使っており、銘柄数・履歴・通知・検証が増えると検索性、監査性、型安全性、エラー追跡に限界がある
- LINEトークンがスクリプト内に直書きされているため、秘密情報管理の見直しが必要

### 対応内容
- `README.md`, `CLAUDE.md`, `SPREADSHEET.md`, `scripts/06_daily_report.py`, `scripts/07_scan.py`, `scripts/03_backtest.py` を確認
- Supabase公式ドキュメントでPythonクライアント、Cron、Edge Functions、Secrets、Database Webhooksの利用方針を確認
- `docs/supabase_enhancement_plan.md` を作成し、段階移行方針、DB設計案、実装ステップを整理

### 残課題
- [ ] LINEトークンを再発行し、環境変数またはSupabase Secretsへ移行する
- [ ] `supabase/migrations/001_initial_market_pilot.sql` を作成する
- [ ] `requirements.txt` に `supabase` と `python-dotenv` を追加する
- [ ] `06_daily_report.py` にSupabase実行ログ保存を追加する
- [ ] Google SheetsとSupabaseの役割分担を確定する

## 2026-05-19｜Mac移行・cron設定

### 背景・問題
- LINE通知が当日届いていなかった
- 原因：WindowsタスクスケジューラはPCスリープ中に実行されない
- スクリプトにエラーハンドリングがなく、Google認証エラー等でも無音でクラッシュする構造

### 対応内容

#### 1. Mac常時起動型PCへの移行方針決定
- WindowsタスクスケジューラからMac cronへ移行
- Macをスリープさせない設定（システム設定 → バッテリー → スリープさせない）

#### 2. Google認証ファイル配置
- `credentials.json` をGoogle Driveからダウンロード
- 配置先：`~/Library/Application Support/gspread/credentials.json`
- OAuth認証は昨日済み済みであったため、手動実行でLINE送信を確認

#### 3. リポジトリ整理
- 旧ローカルディレクトリ `/Users/satoshijinnouchi/market-pilot/` を削除
- Phase2スクリプト（`03_backtest.py`, `07_scan.py`）をGitHubリポジトリに移行・プッシュ
- 作業ディレクトリを `/Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/` に統一

#### 4. cron設定
```
# 毎日 07:00
0 7 * * * /Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3 /Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/scripts/06_daily_report.py >> /Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/logs/daily.log 2>&1

# 毎日 22:30
30 22 * * * /Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3 /Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/scripts/06_daily_report.py >> /Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/logs/daily.log 2>&1
```
- ログ出力先：`/Users/satoshijinnouchi/sjinnouchi-ux-market-pilot/logs/daily.log`

### 残課題
- [ ] Macのスリープ無効化（システム設定 → バッテリー → スリープさせない）
- [ ] `06_daily_report.py` にエラーハンドリング追加（エラー時もLINEで通知する）

### 環境情報
- Python: 3.13.3（pyenv）
- 実行パス: `/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`
- gspread: 6.2.1 / yfinance: 1.3.0
