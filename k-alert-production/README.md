# Kアラート 本番開発

Kアラートは、公式LINEでコンプライアンス、パワハラ、職場トラブルなどの相談を受け付け、AIチャット、匿名報告、調査官相談、企業向け報告書作成へつなげる本番システムです。

最終設計は [Kアラート本番開発_最終設計_v1.md](./Kアラート本番開発_最終設計_v1.md) を正本とします。

## 初期構成

```text
app/
  main.py              FastAPIアプリ本体
  core/config.py       環境変数設定
worker/
  src/index.ts         Cloudflare Worker固定Webhook入口
tests/
  test_health.py       ヘルスチェックの最小テスト
```

## セットアップ

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
Copy-Item .env.example .env
```

`.env` には実シークレットを入れます。`.env` はGit管理しません。

## 起動

```powershell
uvicorn app.main:app --reload
```

ヘルスチェック:

```text
GET http://127.0.0.1:8000/health
```

LINE Webhook endpoint:

```text
POST http://127.0.0.1:8000/webhooks/line
```

`APP_ENV=local` かつ `LINE_CHANNEL_SECRET` 未設定の場合のみ、署名なしのローカル検証を許可します。local以外では `X-Line-Signature` の検証が必須です。

## Google Cloud Run

本番FastAPIはGoogle Cloud Runへデプロイします。

```text
Google Cloud project: k-alert-production-500611
Region: asia-northeast1
Service: k-alert-api
Cloud Run URL: https://k-alert-api-jl4i5fzkaq-an.a.run.app
```

Cloud Runの実行時シークレットはGoogle Secret Managerで管理します。
APIキーやトークンはDockerイメージやGitHubに含めません。

```text
SUPABASE_SERVICE_ROLE_KEY
LINE_CHANNEL_SECRET
LINE_CHANNEL_ACCESS_TOKEN
ANTHROPIC_API_KEY
CHATWORK_API_TOKEN
ADMIN_API_KEY
LIFF_REPORT_API_KEY
```

Cloudflare Workerの `FASTAPI_ORIGIN_URL` は上記Cloud Run URLへ設定します。
これにより、LINE側のWebhook URLを変更せずにFastAPIの実行基盤だけを
Cloud Runへ移行できます。

## 管理API

ケース確認用の管理APIは `X-Admin-Api-Key` が必須です。キーは
`ADMIN_API_KEY` に設定します。相談本文を返すため、キーはGitHubやチャットへ
表示しません。

```text
GET /admin/cases
GET /admin/cases/{case_id}
GET /admin/exports/reports
GET /admin/exports/report-companies
GET /admin/ai-response-rules
POST /admin/ai-response-rules
```

初期用途:

- LINE実機テスト後のケース状態確認
- Supabaseからスプレッドシートへ抽出する前段API
- Codex定期レビューで会話ログと応答ルールを確認する入口

## スプレッドシート抽出

通報フォームのスプレッドシート更新はGAS主導で行います。

通常ルート:

```text
Google Sheets / GAS -> FastAPI /admin/exports/reports -> Supabase
```

非常用ルート:

```text
Google Sheets / GAS -> Supabase RPC export_reports_for_sheet -> Supabase
```

GASは通常FastAPIを呼び、失敗時のみSupabase RPCへフォールバックします。
GASにはService Role Keyを置かず、通常用の `K_ALERT_ADMIN_API_KEY` と
非常用の `SUPABASE_ANON_KEY` のみを設定します。

Apps Script雛形:

```text
gas/sheet_export.gs
```

GAS Script Properties:

```text
K_ALERT_API_BASE_URL
K_ALERT_ADMIN_API_KEY
SUPABASE_URL
SUPABASE_ANON_KEY
```

Supabase非常用RPC migration:

```text
supabase/migrations/20260626093000_sheet_export_rpc.sql
```

### Supabase Keepalive

Supabase無料枠の自動停止対策として、抽出処理とは独立した軽量RPCを用意します。
GASから6時間ごとに `system_heartbeats` をupsertし、FastAPIやLINEが止まっていても
Supabaseだけへ定期的に書き込みます。

```text
Google Sheets / GAS -> Supabase RPC touch_system_heartbeat -> system_heartbeats
```

Migration:

```text
supabase/migrations/20260626094500_system_heartbeat_rpc.sql
```

Apps Scriptの `installSupabaseKeepaliveTrigger()` を1回実行すると、即時に疎通確認を行い、
以後6時間ごとのトリガーを作成します。

### 提出状態管理

通報フォームのA列は `提出状態` とし、値は `未提出` / `提出済` に限定します。
抽出条件の提出状態は `すべて` / `未提出` / `提出済` です。

管理者がシート上でA列を変更し、Apps Scriptメニューの
`Kアラート -> 提出状態をDBへ反映` を実行すると、各行の `report_id` をキーに
Supabaseの `reports.submission_status` を更新し、その後シートを再抽出します。

Migration:

```text
supabase/migrations/20260626103000_report_submission_status.sql
```

AI応答ルールは初期状態では `active=false` で作成します。現時点のLINE本番フローは
テスト版の運用に合わせ、相談者への同調チャット後に `匿名報告` または `調査官相談`
を選んでもらいます。匿名報告の詳細入力はLINEチャット内ではなくLIFF報告フォームで
受け付けます。

初期対応する `trigger_type`:

- `exact_text_reply`: 入力文が `trigger_text` と完全一致した場合に `instruction` を返信する。
- `contains_text_reply`: 入力文に `trigger_text` が含まれる場合に `instruction` を返信する。
- `fallback_reply`: 他の有効ルールが一致しない場合に `instruction` を返信する。

## LINE相談フロー

```text
相談する
-> 冒頭あいさつを送信
-> 相談者が状況を送信
-> AIが同調返信、緊急判定、次アクション誘導を生成
-> 2回目以降は匿名報告または調査官依頼へ自然に誘導
-> 緊急性がある文面では110番・119番を優先案内

通報する
-> Flexカード「通報する」を表示
-> ボタン押下でLIFF報告フォームを開く
```

チャット中のクイックリプライには `相談を終了する`、`調査を依頼する`、
`通報する` を表示します。`調査を依頼する` はチャット上に選択内容を出したうえで
調査官依頼カードへ進みます。

AI応答は `LLM_PROVIDER` と各プロバイダーのAPIキーが設定されている場合に有効です。
未設定またはAI APIエラー時は固定文へフォールバックします。

## LIFF報告フォーム

匿名報告の詳細入力はWorkerのフォームで受け付けます。

```text
GET  /report?case_code={case_code}
POST /api/report
POST /liff/report
```

LINE Loginチャネル:

```text
Channel ID: 2010517346
LIFF ID: 2010517346-PtmxkueF
LIFF URL: https://liff.line.me/2010517346-PtmxkueF
Endpoint URL: https://k-alert-production-webhook.s-jinnouchi.workers.dev/report
Scope: profile, chat_message.write
```

LIFFチャネルは公開済みです。

WorkerフォームURL:

```text
https://k-alert-production-webhook.s-jinnouchi.workers.dev/report
```

`/api/report` はWorker内で `LIFF_REPORT_API_KEY` を付けてFastAPIの
`/liff/report` へ転送します。フォーム送信後は `reports` と
`ai_extractions` に保存し、caseを更新します。
送信完了時はLIFFの `chat_message.write` で、ユーザー側のチャットとして
相談受付希望の有無に応じた完了メッセージを送信します。FastAPI側はこの完了メッセージには返信せず、
以後ユーザーが通常チャットを続けた場合のみ応答します。

```text
相談受付希望なし:
🛡️ Kアラートからのメッセージ 🛡️

通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。

相談受付希望あり:
🛡️ Kアラートからのメッセージ 🛡️

通報を受付ました。内容は匿名で企業に報告書を提出しますのでご安心ください。

調査官より、改めてチャットでご連絡しますのでご不安な点があればご相談ください。
```

LIFFフォームはテスト版最新仕様に合わせ、以下のA〜J列相当の項目で受け付けます。

- 企業名
- 名前（任意）
- いつの事ですか？
- どこで起きましたか？
- だれが起こした人ですか？
- だれに対してのことですか？
- なにをどのようにしていましたか
- その他（自由記載）
- 相談受付希望

LINE画面からは `case_code` 付きのLIFF URLで開きます。Workerは `what_how_text`
としてFastAPIへ送信し、DBの `reports.body` に `what_how_text` として保存します。

Worker secret `LIFF_ID` とFastAPI側 `K_ALERT_LIFF_URL` は、上記LIFF ID/URLへ
設定済みです。

## リッチメニュー

本番公式LINE `@473vqedz` には、テスト版と同じ3エリアのリッチメニューを
Messaging APIで作成し、デフォルト設定しています。

```text
Rich menu ID: richmenu-541717d478dd28c70f85529f3cb7dcd6
Image: 2500x1686 JPEG
```

エリア:

- 上段左: `相談する` postback `action=consult`, `inputOption=openKeyboard`
- 上段右: `通報する` message
- 下段全幅: LINEシェアURL

## Cloudflare Worker

LINE側のWebhook URLを固定するため、Cloudflare Workerを薄い中継として使います。

```text
公式LINE -> Cloudflare Worker -> FastAPI /webhooks/line
```

FastAPIの公開先をRenderやGoogle Cloud Runへ変更する場合も、LINE側Webhook URLは変更せず、Workerの `FASTAPI_ORIGIN_URL` だけを差し替えます。

初期状態では `FASTAPI_ORIGIN_URL` が未設定でも200を返す準備中モードです。LINEのURL登録や疎通確認を先に進め、FastAPI本番URLが決まった時点で転送先を設定します。

### Temporary FastAPI exposure

Google Cloud Runなどの正式公開先が決まるまでは、Cloudflare TunnelでローカルFastAPIを一時公開し、Worker secret `FASTAPI_ORIGIN_URL` にトンネルURLを設定して検証します。

```powershell
.\tools\cloudflared.exe tunnel --url http://127.0.0.1:8000 --no-autoupdate
```

一時トンネルURLは起動中のみ有効です。恒久公開に移行したら、Worker secret `FASTAPI_ORIGIN_URL` を正式URLへ差し替えます。

2026-06-26時点のWorker deploy:

```text
Worker URL: https://k-alert-production-webhook.s-jinnouchi.workers.dev
Version ID: 4fbef7d9-c383-4162-b7c6-5336ea75ee05
```

## テスト

```powershell
pytest
```

## 実装方針

- Supabaseを記録の正本にする。
- GoogleスプレッドシートはDB抽出ビューとして扱う。
- LINE Webhookでは `webhookEventId` による冪等性を必ず実装する。
- LINE reply token制約を考慮し、遅延時はpush messageへフォールバックする。
- 調査官はLINE userIdを事前登録する。
- ChatWork通知は実送信確認済み。
- 調査官対応は `対応開始 case_code` / `対応終了 case_code` でセッション管理する。
- 相談本文や秘密情報を通常ログへ出さない。
