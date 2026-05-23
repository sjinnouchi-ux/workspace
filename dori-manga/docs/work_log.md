# 作業ログ

## 2026-05-23（2回目）
- setup_sheets.py のバグ修正：`sheetId` をハードコード `0` からAPIレスポンス取得に変更
- 原因：新規作成シートのsheetIdが0以外になる場合があり `No grid with id: 0` エラーが発生
- 修正後に再実行し、スプレッドシート作成・ヘッダー設定・書式設定が正常完了
- 新スプレッドシートID: `1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw`
- **残課題**: `.env` に `GOOGLE_SHEETS_ID=1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw` を追記する

## 2026-05-23
- アーキテクチャをCowork中心に刷新（AnthropicのAPIキー不要）
- QQQプロジェクトのOAuth2認証（credentials.json）をdori-mangaに流用
- credentials.json をGoogleドライブ（GCloud/qqq_trading）から取得・配置
- .gitignore / .env 作成
- src/setup_sheets.py 作成（スプレッドシート自動生成）
- src/write_to_sheets.py 作成（Cowork生成JSONのシート書き込み）
- docs/cowork_pipeline.md 作成（設計書＋コード全文）
- 旧スクリプト（run.py / pdf_reader.py / manga_gen.py / drive.py）はCowork中心フローでは不使用

## 2026-05-22
- 漫画自動化パイプラインの設計・実装
  - docs/manga_pipeline_spec.md 作成（仕様書）
  - src/run.py / pdf_reader.py / manga_gen.py / sheets.py / drive.py 作成
  - .env.example 作成
- 参考漫画（4コマ）をGoogleドライブから確認・スタイル分析完了
- サンプルPDF（酸素マスク）をClaude Visionで読み取り・動作確認

## 2026-05-19
- プロジェクトフォルダ作成（CLAUDE.md / README.md / docs/）
- concept.md・episode_list.md の初版作成
