# dori-manga v3 Phase 2 ブロック報告

作成日: 2026-07-02
対象: dori-manga 管理システム改修 / Phase 2 Drive連携疎通

## 結論

Phase 2は完了していません。

理由は、GCP組織ポリシー `iam.disableServiceAccountKeyCreation` により、サービスアカウントキーJSONの作成がブロックされたためです。
このため、`GOOGLE_SERVICE_ACCOUNT_JSON` を Supabase secrets に設定できず、Edge Functions deploy とJWT付きcurl疎通テストへ進めませんでした。

## 実施済み

- MiniPCに Deno `2.9.0` を導入。
- MiniPCに Supabase CLI `2.109.0` を導入。
- `dori-manga/supabase/functions` 配下の全 `.ts` に対して `deno check` を実行し、通過を確認。
- GCP新規プロジェクト `dori-manga` を作成。
  - Project ID: `studied-brand-501210-i1`
- サービスアカウントを作成。
  - Email: `dori-manga-drive@studied-brand-501210-i1.iam.gserviceaccount.com`
- Google Drive API を有効化。
- Drive親フォルダをサービスアカウントに編集者共有。
  - Folder ID: `11UK7BKd-pcWW7eQSDghbkJxjxJa34Dbz`
  - Folder name: `どり看護師_漫画格納フォルダ（改定）`
- 共有後、一般アクセスを「制限付き」に戻したことを確認。

## 未実施

- `GOOGLE_SERVICE_ACCOUNT_JSON` の `supabase secrets set`
- `create-episode-folder` / `upload-image` の `supabase functions deploy`
- JWT付きcurlによるフォルダ作成疎通テスト
- Drive上のテストフォルダ作成確認と削除
- Supabase `episodes` / 関連テストデータの作成・削除確認

## ブロック詳細

GCP Consoleで `dori-manga-drive` の秘密鍵JSONを作成しようとしたところ、次の組織ポリシーにより作成不可でした。

- Policy ID: `iam.disableServiceAccountKeyCreation`
- 表示内容: サービスアカウントキーの作成をブロックする組織ポリシーが組織に適用されている

キーJSONの中身は作成されておらず、チャット・ファイル・ログにも保存していません。

## 判断が必要な点

1. 組織ポリシー管理者が、一時的または対象プロジェクト限定でサービスアカウントキー作成を許可する。
2. 既存の利用可能なサービスアカウントキーJSONを使う。ただし、出所・権限・ローテーション責任を確認する必要があります。
3. キーJSONを使わない認証方式へ設計変更する。Supabase Edge Functionsでの実装可否を別途検証する必要があります。

## Phase 2 再開条件

- `GOOGLE_SERVICE_ACCOUNT_JSON` として使えるサービスアカウントJSONを安全に用意できること。
- または、キーJSON不要の代替設計がClaude/Codex双方で承認されること。

## 継続中の人間タスク

旧GASのApps Script側の後片付けはGit外の人間タスクとして継続です。

- 旧トリガー停止
- スクリプトプロパティの `service_role` キー削除
