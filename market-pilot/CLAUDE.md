# market-pilot — プロジェクトコンテキスト

## プロジェクト概要
株式市場の多銘柄分析・売買シグナル検知・LINE自動通知システム。
QQQ/GLD を中心に数十銘柄を対象に拡張予定。

## ファイル構成
```
market-pilot/
├── CLAUDE.md                    # このファイル
├── README.md
├── requirements.txt
├── scripts/
│   ├── 06_daily_report.py       # メイン：日次レポート（07:00 / 22:30）
│   ├── 03_backtest.py           # バックテスト（Phase2）
│   └── 07_scan.py               # 多銘柄スキャン（Phase2）
├── logs/
│   └── daily.log                # cron実行ログ
└── docs/
    └── work_log.md              # 作業ログ
```

## 稼働環境
- 実行：Mac cron（07:00 / 22:30）
- ログ：`logs/daily.log`
- Python：`/Users/satoshijinnouchi/.pyenv/versions/3.13.3/bin/python3`

## 認証・接続情報
- **Google Sheets認証**：gspread.oauth()（OAuth2 Desktop Client）
  - credentials.json：`~/Library/Application Support/gspread/credentials.json`
  - 認証済み（authorized_user.jsonが存在）
- **スプレッドシートID**：1Jt-vKUHDmLo8Qf6aSZlBnvG5uBtpcr6gtk9ZgLjycQ4
  - シート構成：設定 / 売買ログ
- **LINE Messaging API**：Broadcast送信
  - トークン：`scripts/06_daily_report.py` 内 `LINE_TOKEN` 定数

## 売買ルール
### 買いシグナル（どちらか一方で発動）
- RSI < 40（設定シートで変更可）
- MA5日 > MA20日（ゴールデンクロス）
- アクション：22:30通知でシグナルあれば → SBIで成行注文を即実行

### 売却シグナル（どれか一つで発動）
- 損益 +12.0% 以上（PROFIT_TH定数）
- RSI ≥ 70（RSI_SELL_TH定数）
- RSI ≥ 70 かつ BB上限タッチ（強い売りシグナル）

## Phase計画
- **Phase1（完了）**：QQQ/GLD 日次通知
- **Phase2（次）**：多銘柄スキャン + バックテスト + ニュース収集
- **Phase3（将来）**：Claude CLI 連携で週次考察レポート自動生成

## トラブルシューティング
- LINEが届かない → `logs/daily.log` を確認 / Macスリープ確認
- Google認証エラー → `~/Library/Application Support/gspread/authorized_user.json` を削除して再認証
- スクリプトエラー → crontabの設定とPythonパスを確認
