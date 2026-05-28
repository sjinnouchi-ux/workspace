# Cloudflare Worker 接続手順

## 現状

- 公式LINEのWebhook URLは既存のCloudflare Workerに向いている
- `wrangler` はローカルで未ログイン
- 既存WorkerのGitHub上ファイルはmultipart境界文字が混ざっているため、そのまま再デプロイしない

## 推奨手順

1. Cloudflare Dashboardで既存Worker `yumekango` を開く
2. 現在のWorkerコードをバックアップする
3. `k-alert-test/worker/yumekango_worker_integration.js` の内容を反映する
4. Workerの環境変数またはSecretに以下を設定する

| 変数名 | 内容 |
|---|---|
| `LEGACY_GAS_URL` | 既存家計簿GAS WebアプリURL |
| `K_ALERT_GAS_URL` | KアラートGAS WebアプリURL |

5. 保存/デプロイする
6. 公式LINEで `Kアラート テストです` を送信する
7. `Kアラート・テスト開発` スプレッドシートに記録されるか確認する

## 注意

- `LEGACY_GAS_URL` を間違えると家計簿LIFFと既存公式LINE応答に影響する
- `K_ALERT_GAS_URL` を間違えるとKアラートだけ動かない
- まずはユーザー本人と奥様のみの公式LINEでテストする
- WebアプリURLやトークン類はGitHubに記録しない

