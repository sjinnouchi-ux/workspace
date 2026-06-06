# API Monitor

OpenAI、Anthropic Claude、Google Gemini の API 利用料をローカルブラウザで確認するための Streamlit アプリです。

今後は Windows 管理を前提に、まずこのアプリを `http://localhost:8501` で動かし、必要に応じて Notion には「集計結果・リンク・運用メモ」を同期する構成にします。

## できること

- AI API の月間コスト、トークン数、APIコール数を確認
- 日別コスト推移とサービス別コストをグラフ表示
- APIキーをローカルDBに保存して管理
- プロジェクト名、モデル、用途メモを記録

## Windowsでの起動

PowerShellでこのフォルダを開き、次を実行します。

```powershell
.\run_windows.ps1
```

初回実行時は `.venv` を作成し、`requirements.txt` の依存関係をインストールします。起動後、ブラウザで次のURLを開きます。

```text
http://localhost:8501
```

## 手動起動

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

## APIキー

`.env.example` を `.env` にコピーして、必要なAPIキーを入れます。

```text
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

`.env` はGitHubへ保存しないでください。APIキー本体もNotionには貼らず、Notionには利用料の集計や管理リンクだけを置く運用にします。

## Notion連携方針

Notionホーム画面では、API利用料アプリそのものを完全に動かすよりも、以下を管理する形が現実的です。

- アプリURL: `http://localhost:8501`
- 今月の合計利用料
- サービス別コスト
- 注意が必要なAPIキーやモデル
- 月次確認タスク

実際の集計やグラフ表示は、このStreamlitアプリで行うのが早く、Windowsでも安定します。
