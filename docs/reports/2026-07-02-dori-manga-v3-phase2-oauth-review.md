# dori-manga v3 Phase 2 OAuth設計変更レビュー依頼

作成日: 2026-07-02
対象: dori-manga 管理システム改修 / Drive連携認証方式変更

## 結論

Drive連携の認証方式を、サービスアカウントJSONからOAuthユーザー認証（refresh token）へ変更しました。

ただし、Phase 2の疎通完了には至っていません。Supabase access tokenの権限不足により、`supabase secrets set` と `functions deploy` が403で止まっています。

## 変更理由

- GCP組織ポリシー `iam.disableServiceAccountKeyCreation` は解除しない方針になったため。
- サービスアカウント方式では、新規サービスアカウントのDrive保存容量問題により `upload-image` が `storageQuotaExceeded` になるリスクがあるため。

## 変更ファイル

- `dori-manga/supabase/functions/_shared/google_drive.ts`
  - `GOOGLE_SERVICE_ACCOUNT_JSON` 参照を削除。
  - `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` を使う refresh token 交換方式へ変更。
  - `POST https://oauth2.googleapis.com/token` で `grant_type=refresh_token` を送信。
  - `invalid_grant` を refresh token 失効として日本語メッセージで区別。
  - Drive API本体の `findChildFolder` / `createFolder` / `uploadFile` / 403・404等の分類は維持。
- `dori-manga/docs/work_log.md`
  - OAuth設計変更、Deno check、GCP/OAuth作業、Supabase権限ブロックを記録。
- `docs/reports/2026-07-02-dori-manga-v3-phase2-blocker.md`
  - サービスアカウント方式ブロックに加え、OAuth変更後のSupabase権限ブロックを追記。

## 実施済み

- Deno `2.9.0` で `dori-manga/supabase/functions` 配下の全 `.ts` を `deno check` し、成功。
- GCP `studied-brand-501210-i1` でOAuth同意画面を Internal として構成。
- デスクトップアプリ用OAuthクライアントを作成。
- `https://www.googleapis.com/auth/drive` scopeで初回同意フローを実施し、refresh tokenを取得。
- refresh tokenからaccess tokenを取得し、Drive親フォルダ `11UK7BKd-pcWW7eQSDghbkJxjxJa34Dbz` の参照に成功。
- 権限不足だったSupabase access tokenは削除済み。

## 未実施

- `supabase secrets set`
- `supabase functions deploy create-episode-folder upload-image`
- JWT付きcurl疎通テスト
- Drive上のテストフォルダ作成確認と削除
- Supabase側のテストepisode/panels削除確認

## 現在のブロック

Supabase CLIで次のエラーにより停止しました。

```text
Your account does not have the necessary privileges to access this endpoint.
```

ブラウザで確認したところ、現在ログイン中のSupabase組織は `K Alert Production` で、対象project ref `vdntqwtywxyjxelycavx` のプロジェクトが見えていません。

## 再開条件

- 対象Supabaseプロジェクト `vdntqwtywxyjxelycavx` に対してsecrets/deploy権限を持つアカウントでログインする。
- または、その権限を持つSupabaseアカウントでaccess tokenを生成する。

## 迷った点

- Supabase access tokenは現在ログイン中アカウントで生成できましたが、対象プロジェクト権限がないため削除しました。
- サービスアカウント共有削除はDrive UIの権限メニュー描画が不安定で、まだ完了確認できていません。OAuth方式では不要なため、Phase 2完了前の後片付けとして再試行します。
- refresh token等の値はログ・チャット・ファイルに保存していません。

## Claudeレビュー観点

- `getDriveAccessToken()` のrefresh token交換方式が妥当か。
- `invalid_grant` の日本語エラー分類が十分か。
- サービスアカウント前提の文言がユーザー向けエラーに残っていないか。
- Drive API呼び出し部分に不要な変更が入っていないか。
