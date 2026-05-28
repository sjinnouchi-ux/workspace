# Cloudflare Worker 接続手順

## 現状

- 公式LINEのWebhook URLは既存のCloudflare Workerに向いている
- `wrangler` は2026-05-28にOAuth認証済み
- Worker `yumekango` へ `LEGACY_GAS_URL` と `K_ALERT_GAS_URL` をSecretとして設定済み
- `k-alert-test/worker/yumekango_worker_integration.js` をWorker `yumekango` へデプロイ済み
- 既存WorkerのGitHub上ファイルはmultipart境界文字が混ざっているため、そのまま再デプロイしない

## 実施済み手順

1. Cloudflare Dashboardで既存Worker `yumekango` を確認
2. Wrangler CLIをOAuth認証
3. WorkerのSecretに以下を設定

| 変数名 | 内容 |
|---|---|
| `LEGACY_GAS_URL` | 既存家計簿GAS WebアプリURL |
| `K_ALERT_GAS_URL` | KアラートGAS WebアプリURL |

4. `k-alert-test/worker/yumekango_worker_integration.js` を `yumekango` へデプロイ
5. GET確認でLIFFフォームHTMLがHTTP 200で返ることを確認

## 次の確認手順

1. 最新版GASコードをApps Scriptへ反映する
2. 必要ならWebアプリを再デプロイする
3. 公式LINEで `Kアラート テストです` を送信する
4. `Kアラート・テスト開発` スプレッドシートに記録されるか確認する
5. 既存の家計簿LIFF入力が従来どおり動くか確認する

## 注意

- `LEGACY_GAS_URL` を間違えると家計簿LIFFと既存公式LINE応答に影響する
- `K_ALERT_GAS_URL` を間違えるとKアラートだけ動かない
- まずはユーザー本人と奥様のみの公式LINEでテストする
- WebアプリURLやトークン類はGitHubに記録しない
