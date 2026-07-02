# dori-manga v3 Phase 1 Claude確認依頼

作成日: 2026-07-02
対象: dori-manga 管理画面 全面改訂 Phase 1
実装担当: Codex
設計担当: Claude

## 実施内容

- Phase 0承認を受け、Phase 1（Edge Functions実装・コードのみ）を実施した。
- `create-episode-folder` Functionを追加した。
  - POST `{ episode_id, title }` を受け取る。
  - `app_settings` の `drive_root_folder_id` を取得し、なければ `drive_root_folder_url` からフォルダIDを抽出する。
  - Drive親フォルダ直下に作品フォルダを作成または再利用する。
  - 作品フォルダ配下に `OK` / `NG` / `CLOSE` / `完成` フォルダを作成または再利用する。
  - `manga_episodes.drive_folder_id` / `drive_folder_url` を更新する。
- `upload-image` Functionを追加した。
  - POST `{ episode_id, result_status, file_name, content_base64 }` を受け取る。
  - `episode.drive_folder_id` 配下の判定フォルダ（`OK` / `NG` / `CLOSE`）を検索する。
  - Base64画像をDriveへアップロードし、`{ status, file_id, web_view_link }` を返す。
  - 10MB超の画像はエラーにする。
- 共通処理を `_shared` に分離した。
  - `cors.ts`: CORS/JSONレスポンス。
  - `errors.ts`: アプリ共通の日本語エラー応答。
  - `supabase.ts`: Supabase RESTアクセス、`app_settings` と `manga_episodes` の取得/更新。
  - `google_drive.ts`: サービスアカウントJWT署名、OAuthトークン取得、Drive API呼び出し、Drive APIエラー分類。
- `dori-manga/supabase/config.toml` を追加し、両Functionで `verify_jwt = true` を明示した。
- デプロイ、Supabase secrets設定、実Drive疎通テストはPhase 2作業として未実施。

## 変更ファイル一覧

- `docs/reports/2026-07-02-dori-manga-v3-phase1-review.md`
- `dori-manga/docs/work_log.md`
- `dori-manga/supabase/config.toml`
- `dori-manga/supabase/functions/_shared/cors.ts`
- `dori-manga/supabase/functions/_shared/errors.ts`
- `dori-manga/supabase/functions/_shared/google_drive.ts`
- `dori-manga/supabase/functions/_shared/supabase.ts`
- `dori-manga/supabase/functions/create-episode-folder/index.ts`
- `dori-manga/supabase/functions/upload-image/index.ts`

## レビュー観点への対応

- (a) JWT検証:
  - `dori-manga/supabase/config.toml` で `create-episode-folder` / `upload-image` ともに `verify_jwt = true` を明示。
  - Function内でも `Authorization: Bearer ...` がない場合は401相当の日本語エラーを返す。
  - `verify_jwt = false` は追加していない。
- (b) サービスアカウントJSON・アクセストークンのログ出力:
  - `console.log` / `console.error` は追加していない。
  - `GOOGLE_SERVICE_ACCOUNT_JSON` とOAuth `access_token` は処理中の変数としてのみ扱い、レスポンスやログへ出していない。
- (c) ルートフォルダID:
  - Drive親フォルダIDはハードコードしていない。
  - `app_settings` の `drive_root_folder_id` を優先し、なければ `drive_root_folder_url` からIDを抽出する。
- (d) Drive APIエラーの日本語分類:
  - 401/invalid_grant: サービスアカウント/キー設定の認証エラー。
  - 403: サービスアカウントへの編集者権限不足。
  - 404: 親フォルダIDまたは作品フォルダIDの不存在。
  - 400: フォルダIDやファイル名などリクエスト形式不正。
  - upload時の判定フォルダ不存在は `status_folder_missing` として日本語メッセージを返す。

## 検証

- `git diff --check`: 成功。
- `rg` による確認:
  - `verify_jwt = false` が存在しないこと。
  - `console.` が存在しないこと。
  - `service_role` 実値、JWTらしき `eyJ...`、GitHub tokenらしき値が追加ファイルに存在しないこと。
  - `app_settings` 参照があり、親フォルダIDのハードコードがないこと。
- 未実行:
  - Deno check。理由: このWindows環境に `deno` / `supabase` / `tsc` CLI が未導入。`npx deno-bin` の一時実行はタイムアウト。
  - Function deploy。理由: Phase 1はコードのみ、デプロイしない指示。
  - 実Drive疎通。理由: Phase 2の人間タスクとsecrets設定後に実施予定。

## 判断に迷った点

- `upload-image` は判定フォルダが存在しない場合に自動作成せず、日本語エラーで返す実装にした。
  - 理由: `create-episode-folder` が `OK` / `NG` / `CLOSE` / `完成` を作成する責務を持つため、upload側で勝手に構成を補正するとフォルダ構成の異常検知が遅れる。
- `create-episode-folder` は同名作品フォルダと各サブフォルダを再利用する実装にした。
  - 理由: v3仕様の「同名フォルダ既存時は再利用（エラーにしない）」に合わせた。

## 次Phaseの予定

- Claude承認後、Phase 2としてDrive連携の疎通へ進む。
- Phase 2では人間タスクとして、GCPサービスアカウント作成、Drive API有効化、キーJSON取得、親フォルダへの編集者権限共有が必要。
- Codex側では、Supabase secrets設定、Functions deploy、JWT付きcurl疎通テスト、テストフォルダ作成/削除確認を行う。
- 旧GASのApps Script側後片付け（トリガー停止・スクリプトプロパティの `service_role` キー削除）はGit外の人間タスクとして残っている。陣内さん作業。

## 確認してほしいこと

- `_shared` 分離の粒度がレビューしやすいか。
- Drive APIエラー分類の粒度が十分か。
- `upload-image` で判定フォルダ不存在時に自動作成せずエラー返却する方針でよいか。
- Phase 2前にDeno/Supabase CLI導入またはMiniPC側での `deno check` を必須にするか。
