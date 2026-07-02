# dori-manga v3 Phase 2 OAuth疎通確認レビュー依頼

作成日: 2026-07-02
対象: dori-manga 管理システム改修 / Drive連携 Phase 2

## 結論

Phase 2（Drive連携の疎通）は、OAuthユーザー認証（refresh token）方式で完了しました。

`create-episode-folder` / `upload-image` はSupabase Edge Functionsへデプロイ済みです。JWT付きで `create-episode-folder` を呼び出し、Drive上の作品フォルダ・サブフォルダ作成、DB更新、テスト資材削除まで確認しました。

## 変更理由

- GCP組織ポリシー `iam.disableServiceAccountKeyCreation` はGoogleのセキュア既定値であり、解除しない方針になったため。
- サービスアカウント方式では、新規サービスアカウントのDrive保存容量問題により `upload-image` が `storageQuotaExceeded` になるリスクがあるため。

## 変更ファイル

- `dori-manga/supabase/functions/_shared/google_drive.ts`
  - `GOOGLE_SERVICE_ACCOUNT_JSON` 参照を削除。
  - `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` を使う refresh token 交換方式へ変更。
  - `POST https://oauth2.googleapis.com/token` で `grant_type=refresh_token` を送信。
  - `invalid_grant` を refresh token失効として日本語メッセージで区別。
  - Drive API本体の `findChildFolder` / `createFolder` / `uploadFile` / 403・404等の分類は維持。
- `dori-manga/docs/work_log.md`
  - OAuth設計変更、Deno check、Supabase secrets/deploy、疎通テスト、テスト資材削除、サービスアカウント共有解除を記録。
- `docs/reports/2026-07-02-dori-manga-v3-phase2-blocker.md`
  - サービスアカウント方式のブロックとOAuth方式への設計変更を記録済み。
- `docs/reports/2026-07-02-dori-manga-v3-phase2-oauth-review.md`
  - 本レビュー依頼。

## 実施内容

- Deno `2.9.0` で `dori-manga/supabase/functions` 配下の対象Edge Functionsを `deno check` し、成功。
- GCP `studied-brand-501210-i1` でOAuth同意画面を Internal として構成。
- デスクトップアプリ用OAuthクライアントを作成。
- `https://www.googleapis.com/auth/drive` scopeで初回同意フローを実施し、refresh tokenを取得。
- refresh tokenからaccess tokenを取得し、Drive親フォルダ `11UK7BKd-pcWW7eQSDghbkJxjxJa34Dbz` の参照に成功。
- Supabase project ref `vdntqwtywxyjxelycavx` に以下の3 secretsを設定。
  - `GOOGLE_OAUTH_CLIENT_ID`
  - `GOOGLE_OAUTH_CLIENT_SECRET`
  - `GOOGLE_OAUTH_REFRESH_TOKEN`
- `create-episode-folder` / `upload-image` をSupabase Edge Functionsへデプロイ。
- 不使用になったサービスアカウント `dori-manga-drive@studied-brand-501210-i1.iam.gserviceaccount.com` は親Driveフォルダ共有から削除。Drive APIで共有残存なしを確認。

## 疎通テスト結果

テスト方法:

- Supabase REST APIで一時episodeと4 panelsを作成。
- Supabase JWT付きで `POST /functions/v1/create-episode-folder` を呼び出し。
- Drive上のフォルダ構成を確認。
- DriveテストフォルダとSupabaseテストデータを削除。

結果:

- テストepisode title: `__codex_phase2_oauth_test_20260702_194958`
- テストepisode id: `343ad9b7-8dfc-44b8-bdcb-eaa22878c1e6`
- 作成されたDrive folder id: `1WS0ipgrQbZMDR4dQ7Nd5GQDmP8r-4jFK`
- Function response: `status = ok`
- `reused = false`
- 作成サブフォルダ: `OK` / `NG` / `CLOSE` / `完成`
- DB `manga_episodes.drive_folder_id` は作成folder idへ更新済み。

削除確認:

- Supabaseテストepisode/panels: 削除済み。`__codex_phase2_oauth_test_20260702_%` の残数0。
- Driveテストフォルダ: Drive APIで削除済み。削除API status `204`。
- 親Driveフォルダ直下: 空に戻ったことをGoogle Driveコネクタで確認。

## レビュー観点への対応

- JWT検証:
  - `supabase/functions/config.toml` の `verify_jwt = true` は無効化していません。
  - 疎通テストもJWT付きで実施しました。
- 秘密情報:
  - OAuth client secret、refresh token、Supabase access token、service_role keyはチャット・ログ・ファイルに保存していません。
- ルートフォルダID:
  - Edge Function内でハードコードせず、既存どおり `app_settings` から取得します。
- Drive APIエラー:
  - 権限不足、フォルダ不存在、認証失敗、OAuth `invalid_grant` を日本語メッセージで区別しています。

## 迷った点

- サービスアカウント共有削除はDrive UIの権限メニューが空白表示になることがありました。最終的にはOAuth実行ユーザーのDrive APIで該当permissionだけを削除し、共有残存なしを確認しました。
- Supabase CLIの `functions list` は、後続確認時点でCLIログイン状態が残っておらず `Access token not provided` になりました。ただし、`functions deploy` は成功済みで、デプロイ済み関数へのJWT付き疎通テストも成功しています。
- PowerShellで日本語JSONをSupabase RESTへ送る際、`-ContentType 'application/json; charset=utf-8'` を明示しないと日本語statusがDB制約に合わない形で送信されるため、疎通テストではContent-Typeを明示しました。

## 残タスク

- 旧GASのApps Script側の後片付けはGit外の人間タスクとして残っています。
  - トリガー停止
  - スクリプトプロパティの `service_role` キー削除
  - 担当: 陣内さん

## Phase 3予定

- 管理画面側から `create-episode-folder` / `upload-image` を呼ぶUI導線の接続。
- フォルダ作成済みepisodeの再実行時に `reused = true` になる動作確認。
- 画像アップロードの実ファイル疎通確認。
- ユーザー向けエラー表示の文言確認。
