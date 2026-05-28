# APIモニター

OpenAI・Anthropic (Claude)・Google (Gemini) の3社APIの利用状況・費用・トークン数をブラウザでリアルタイム監視するStreamlitダッシュボード。

## 目的

- 複数AIサービスの費用を一元管理する
- プロジェクト別・モデル別の利用状況を可視化する
- APIキーをアプリから安全にコピーできるようにする
- 将来的な多モデル切り替えに備えた管理基盤を構築する

## 画面構成

### モニタータブ
- サマリー指標（今月費用・総トークン数・APIコール数・最多モデル）
- 日別費用推移グラフ（3社重ね表示）
- サービス別費用比率（ドーナツグラフ）
- 直近のAPIコール履歴テーブル

### 設定タブ
- APIキー管理（マスク表示・コピー・表示切替・登録）
- API用途カスタマイズ（プロジェクト名・使用モデル・用途メモを自由編集）

## 対応サービス（初回から3社同時接続）

| サービス | モデル例 | SDKライブラリ |
|---------|---------|-------------|
| OpenAI | gpt-4o-mini, gpt-4o | openai |
| Anthropic (Claude) | claude-haiku-4-5, claude-opus-4-7 | anthropic |
| Google (Gemini) | gemini-1.5-flash, gemini-1.5-pro | google-generativeai |

## 技術スタック

- **フロントエンド兼バックエンド**：Streamlit（Python）
- **データ保存**：SQLite（ローカル）
- **APIログ取得**：各APIレスポンスの `usage` オブジェクトから取得
- **起動方法**：`streamlit run app.py`（ローカルMac上で常時起動）

## 構成

```text
api-monitor/
├── README.md
├── AGENTS.md
├── docs/
│   ├── implementation_plan.md
│   └── work_log.md
├── app.py              ← Streamlitメインアプリ
├── db.py               ← SQLite操作モジュール
├── monitor.py          ← モニタータブUI
├── settings.py         ← 設定タブUI
├── api_clients/
│   ├── openai_client.py
│   ├── claude_client.py
│   └── gemini_client.py
├── requirements.txt
└── .env.example
```

## セットアップ手順

1. `pip install -r requirements.txt --break-system-packages`
2. `.env.example` をコピーして `.env` を作成し、APIキーを記入
3. `streamlit run app.py` で起動
4. ブラウザで `http://localhost:8501` を開く

## 秘密情報の扱い

以下はGitHubへ保存しない。

- OpenAI APIキー
- Anthropic APIキー
- Google APIキー
- `.env` ファイル本体
