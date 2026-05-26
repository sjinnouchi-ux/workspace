# 作業ログ

## 2026-05-23（4回目）
- migrate_add_status_column.py 作成：A列（完了ドロップダウン）挿入 + 条件付き書式（完了→薄灰色） + R列（画像格納フォルダ）ヘッダー追加
- write_to_sheets.py の COL dict を18列対応に更新（status=A, folder=R 追加）
- setup_sheets.py の HEADER_ROW を18列対応に更新、ドロップダウン・条件付き書式の初期設定を追加
- docs/cli_instruction.md 作成：今後のPDF追加時のCLI実行手順書
- **次のアクション**: ターミナルで `python src/migrate_add_status_column.py` を実行（一回のみ）

## 2026-05-23（3回目）
- B列「PDF URL」をスプレッドシートに追加（既存列を右シフト）
- write_to_sheets.py を更新：pdf_url（B列）書き込み + 処理済みPDFのDriveリネーム（済）対応
- setup_sheets.py のHEADER_ROW・列幅を16列対応に更新
- src/migrate_add_url_column.py 作成：既存5件へのURL追記 + Driveリネーム一括処理
- output.json に pdf_url・pdf_id フィールドを追加（5件）
- **次のアクション**: ターミナルで `python src/migrate_add_url_column.py` を実行

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
- setup_sheets.py を実行しスプレッドシート作成完了（ID: 1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw）
- .env に GOOGLE_SHEETS_ID を設定済み

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
