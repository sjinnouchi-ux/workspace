# Kアラート本番開発 作業報告

作成日: 2026-06-27

## 概要

Kアラート本番版について、公式LINEからの相談、AI応答、LIFF通報フォーム、Supabase保存、Googleスプレッドシート抽出、Cloud Run公開までの本番基盤を構築した。

テスト版は変更せず、本番版は `Kアラート・本番開発` として独立運用する。

## 現在の構成

```text
公式LINE
-> Cloudflare Worker 固定Webhook入口
-> Google Cloud Run FastAPI
-> Supabase
-> Google Sheets / GAS 抽出
```

Cloudflare WorkerはWebhook URL固定のために残す。Cloud Runや将来の実行基盤を変更しても、LINE側Webhook URLを変更せず、Worker側の転送先だけを差し替えられる。

## 主要URL

- Cloud Run API: https://k-alert-api-jl4i5fzkaq-an.a.run.app
- Cloudflare Worker: https://k-alert-production-webhook.s-jinnouchi.workers.dev
- LIFF URL: https://liff.line.me/2010517346-PtmxkueF
- LIFFフォーム入口: https://k-alert-production-webhook.s-jinnouchi.workers.dev/report
- Supabase project: https://supabase.com/dashboard/project/ctuqydrapwfxvkdtdzna
- 管理スプレッドシート: https://docs.google.com/spreadsheets/d/1t8XUgEd6lRWcJpgDUoogaUyaBT3v2PZVbecWPHelHvY/edit
- AIチャット集計シート: https://docs.google.com/spreadsheets/d/1t8XUgEd6lRWcJpgDUoogaUyaBT3v2PZVbecWPHelHvY/edit?gid=1071539754#gid=1071539754

## 実装済み

### Google Cloud Run

- Google Cloud project: `k-alert-production-500611`
- Region: `asia-northeast1`
- Service: `k-alert-api`
- 最新確認済み revision: `k-alert-api-00005-p5g`
- Cloud Run URL: `https://k-alert-api-jl4i5fzkaq-an.a.run.app`

有効化済みAPI:

- Cloud Run
- Cloud Build
- Artifact Registry
- Secret Manager

Cloud Runの実行時シークレットはSecret Managerで管理する。APIキーやトークンはDockerイメージやGitHubへ含めない。

### Cloudflare Worker

Worker `k-alert-production-webhook` の `FASTAPI_ORIGIN_URL` をCloud Run URLへ設定済み。

Workerは以下を担当する。

- LINE Webhook固定入口
- LIFFフォームHTML配信
- LIFFフォーム送信内容をFastAPI `/liff/report` へ転送
- `/health` 応答

### LINE / AIチャット

実装済みフロー:

```text
相談する
-> 冒頭あいさつ
-> AI同調応答
-> 緊急判定
-> 2ラリー目以降で匿名報告または調査官相談へ誘導
```

緊急性が高い文面では110番/119番を優先案内する。

AI応答はAnthropic APIキーが設定されている場合に有効。AI APIエラー時は固定文へフォールバックする。

LINEプロフィール取得も追加済み。Webhook受信時に `userId` からLINEプロフィールを取得し、取得できる場合は `line_users.display_name` / `picture_url` を更新する。

### LIFF通報フォーム

LIFFフォームはWorker `/report` で配信し、送信後にFastAPI `/liff/report` へ転送する。

フォーム項目:

- 企業名
- 名前（任意）
- いつの事ですか？
- どこで起きましたか？
- だれが起こした人ですか？
- だれに対してのことですか？
- なにをどのようにしていましたか
- その他（任意）
- 相談受付希望

フォーム送信後、LIFFの `chat_message.write` でユーザー側チャットとして完了メッセージを送る。

### ChatWork

ChatWorkは調査官への通知のみ担当する。

調査官が公式LINE管理画面から送信した本文は、現状のLINE Webhookでは取得できない。そのため、調査官対応ログのDB格納方法は別途検討が必要。

### Supabase

主なテーブル:

- `line_users`
- `cases`
- `webhook_events`
- `messages`
- `reports`
- `ai_extractions`
- `chatwork_notifications`
- `investigator_sessions`
- `system_heartbeats`

追加済み:

- 通報フォーム抽出RPC
- Supabase keepalive RPC
- `reports.submission_status`
- `reports.submitted_to_company_at`
- 提出状態更新RPC

### Google Sheets / GAS

管理スプレッドシートに以下を実装済み。

#### 通報フォーム

- DBから通報フォーム一覧を抽出
- `提出状態` をA列へ配置
- `未提出` / `提出済` のプルダウン
- スプシ上で提出状態を変更し、GAS実行でSupabaseへ反映
- FastAPI失敗時はSupabase RPCへフォールバック

#### AIチャット集計

`AI応答抽出` は削除し、`AIチャット集計` のみ残す構成に変更済み。

出力単位:

```text
1行 = 1相談ケース
```

列:

```text
ユーザー名 / LINE userId / case_code / 開始日時 / 最終日時 / 終了区分 / ルート / ユーザー発言数 / AI応答数 / 会話ログ / case_id
```

会話ログは日時を含めず、以下のように表示する。

```text
ユーザー: ...
AI: ...
```

終了区分:

- 相談終了
- 通報完了
- 途中中断

公式LINE管理画面から調査官が直接送信した内容は、現時点では会話ログに含まれない。

#### 定時処理

- 通報フォーム抽出トリガー: 3時間ごと
- Supabase keepaliveトリガー: 6時間ごと

## 追加・変更した主なファイル

- `Dockerfile`
- `.dockerignore`
- `README.md`
- `app/api/routes/admin.py`
- `app/api/routes/liff_report.py`
- `app/services/admin_store.py`
- `app/services/ai_chat.py`
- `app/services/line_event_store.py`
- `app/services/line_messaging.py`
- `app/services/line_webhook_service.py`
- `gas/sheet_export.gs`
- `supabase/migrations/20260626093000_sheet_export_rpc.sql`
- `supabase/migrations/20260626094500_system_heartbeat_rpc.sql`
- `supabase/migrations/20260626103000_report_submission_status.sql`
- `worker/src/index.ts`

## 検証

ローカル検証:

```text
pytest: 34 passed
ruff: All checks passed
```

外部疎通:

- Cloud Run `/health`: OK
- Worker `/health`: OK
- Worker -> Cloud Run Webhook転送: 署名検証まで到達
- Cloud Run管理API: OK
- GAS `AIチャット集計を更新`: 実行完了
- Google Sheets `AIチャット集計`: 再出力済み

## 注意点

- Cloud RunはYumekango組織ポリシーにより `allUsers` IAM付与がブロックされたため、`--no-invoker-iam-check` で公開API化している。
- LINE WebhookはLINE署名検証で保護している。
- 管理APIは `X-Admin-Api-Key` 必須。
- LIFF報告APIは `LIFF_REPORT_API_KEY` 必須。
- `/health` は公開。
- 公式LINE管理画面で調査官が直接送った返信本文は、現状のWebhook/DBには入らない。

## 未決事項

- 調査官対応ログをDB化する方法
  - 推奨案: 調査官専用Web画面/APIを作り、FastAPI経由でLINE Push送信とDB保存を同時に行う。
- Cloud Run費用監視
  - 予算アラートはまだ未設定。必要なタイミングで設定する。
- GitHubへの反映
  - ローカルでは変更済み。リモート反映は別途実行する。

## 次アクション

1. LINE実機で相談開始からAI応答、通報フォーム、スプシ抽出まで通し確認する。
2. 通報フォームの提出状態変更をスプシからSupabaseへ反映する運用テストを行う。
3. 調査官対応ログの取得方式を決める。
4. 必要なタイミングでCloud Run予算アラートを設定する。
5. GitHubへ本番実装差分をコミット・プッシュする。
