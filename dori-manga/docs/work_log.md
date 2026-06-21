# 作業ログ

## 2026-06-21
- Notion API fallbackでプロジェクトDBの `dori-manga` 行を取得し、Git側ミラー `docs/notion/projects.csv` の同プロジェクト行をNotion最新値に同期。
- Supabase休眠防止用に `gas/supabase-import/dori-manga-import.gs` を更新。
  - スプレッドシートメニューに「Supabase更新を今すぐ実行」「3日ごとのSupabase更新を設定」「Supabase定期更新を停止」を追加。
  - `installSupabaseKeepaliveTrigger()` で3日に1回の時間主導トリガーを作成。
  - `runSupabaseKeepalive()` で `prompt_templates`、なければ `characters` の既存1行に `is_active` の軽いUPDATEを送る設計にした。
  - 既存の画像評価インポート処理には手を入れず、keepalive用の独立関数として追加。
- ローカル検証: `projects.csv` を `Import-Csv` で読み込み、`dori-manga` 行の列ずれがないことを確認。GASファイルはNodeの構文チェックを通過。
- Notionの `dori-manga` 行も更新し、Next Actionを「Supabase復元後、GASへkeepalive関数を反映し、installSupabaseKeepaliveTriggerを1回実行する。」へ変更。更新後のNotion値を `docs/notion/projects.csv` に再同期。
- Apps Script本体へのpushとトリガー有効化は、Windows環境に `clasp` と `.clasprc.json` が無いため未実行。GASエディタへ反映後、メニューまたは関数一覧から `installSupabaseKeepaliveTrigger()` を1回実行する必要がある。

## 2026-06-11
- Windows-Codex から `DORI_MANGA_SUPABASE_URL` / `DORI_MANGA_SUPABASE_SERVICE_ROLE_KEY` を `C:\Users\irodo\.codex\.sandbox-secrets\global.env` から一時読み込みし、Supabase REST API への接続を確認。
- 接続先ホストは `vdntqwtywxyjxelycavx.supabase.co` で、設計書の REST API URL と一致。
- 初回REST確認で404に見えた原因は、PowerShellの文字列 `"${table}?select=..."` 相当の書き方ではなく `"$table?select=..."` としていたため、`?select` 部分で変数展開が崩れ、テーブル名なしURLを叩いていたこと。
- Supabase SQL Editor で `information_schema.tables` を確認し、`characters` / `prompt_templates` / `manga_episodes` / `manga_panels` / `generation_attempts` / `prompt_lessons` はすべて `public` schema に存在することを確認。
- `curl.exe` でREST APIを再確認し、6テーブルすべて読み取り成功。件数は `characters` 2件、`prompt_templates` 2件、`manga_episodes` 1件、`manga_panels` 4件、`generation_attempts` 13件、`prompt_lessons` 39件。
- `generation_attempts.final_generation_prompt` の格納状況を確認。OK 11件・NG 2件はいずれもプロンプトあり。CLOSEは現時点で該当レコードなし。
- 環境変数上の anon key は publishable key 形式、service_role key は JWT 形式で存在することを確認。秘密値は表示・記録していない。
- OK画像確認で、直近4件はどり看護師に聴診器がなく、DBプロンプトにも `stethoscope` / `聴診器` 指定がないことを確認。4件を `generation_attempts` 上で OK から NG に再分類し、`evaluation_summary` に「聴診器なし」を記録。
- 再分類後の `generation_attempts` は OK 7件・NG 6件。OK 7件はすべてプロンプト内に `stethoscope` / `聴診器` 指定あり。
- `prompt_lessons` に「どり看護師には必ず紫の聴診器を見える位置に描く。プロンプトには purple stethoscope, clearly visible を必ず入れる。聴診器がない画像はNG。」を追加。

## 2026-05-28（動作確認エントリ）
- INDEX.json 自動更新ワークフロー（`.github/workflows/update-index.yml`）の発火確認のため、本ファイルを更新
- 期待される自動挙動：
  - push後、Actions が「Update INDEX.json」を実行
  - `.github/scripts/update_index.py` が `dori-manga` の変更を検出
  - INDEX.json の `projects.dori-manga.last_updated` を `2026-05-28` へ書き換え
  - github-actions[bot] が `chore(INDEX): auto-update last_updated [skip ci]` でcommit
- 確認後、本エントリは将来的に削除してよい（または残してINDEX運用の歴史として保持）

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
