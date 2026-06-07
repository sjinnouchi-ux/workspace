# 2026-06-07 Kアラート・家計簿LIFF 分離完了報告

## 完了概要

Kアラートのテスト機能を家計簿公式LINEから切り離し、Kアラート専用の公式LINE、法人GAS、Cloudflare Worker構成へ移行した。
あわせて家計簿側も法人GASへ移し、Kアラート由来のデモ機能を削除して本来の家計簿機能だけに戻した。

## Kアラート

- 公式LINE: `Kアラート・テスト開発`
- Basic ID: `@953upiqr`
- Messaging API Channel ID: `2010315694`
- Cloudflare Worker: `https://k-alert-test.s-jinnouchi.workers.dev/`
- 法人GAS Web App: `https://script.google.com/macros/s/AKfycbxm5GWC-3zcEyCNSiO7wLg5Ee4qd4c6SHKPBDLhffijuMDk4H0mRVdEwxDEThYstE2lHA/exec`
- 記録DB: `https://docs.google.com/spreadsheets/d/1c1VK_l7xSsT29WLPZiBBYRc5we-yHfGpJuYr24dMNWA/edit?gid=0#gid=0`

### 実装内容

- AI分類項目に `だれに` を追加。
- シート列を12列構成へ更新。
- リッチメニューをMessaging APIで作成し、デフォルト設定。
- `相談する` は匿名相談フロー開始。
- `大人の保健室` / `通報する` は `開発中です。` と返信。
- GAS直Webhookの302問題を避けるため、Cloudflare Worker経由へ変更。

### 確認

- Worker GET: `200 OK`
- Worker POST: `200 OK`
- LINE Webhook検証: `200 OK`

## 家計簿LIFF

- 公式LINE Basic ID: `@258eozcl`
- Messaging API Channel ID: `2007959459`
- LIFF ID: `2010069897-X9JY7R2h`
- Cloudflare Worker: `https://yumekango.s-jinnouchi.workers.dev/`
- 法人GAS Web App: `https://script.google.com/macros/s/AKfycbx2Dw3tpCTC8PZxRwIH68d00TflY98ekTAkxv2-KY7t7EByJdcN676gUOonCg58rg_4/exec`

### 実装内容

- Kアラート由来のデモ機能を削除。
- 削除対象:
  - `保管と入力`
  - `情報参照`
  - `wait_text`
  - `公式LINE_2`
  - `公式LINE_3`
- 家計簿本体機能は維持:
  - `家計簿入力開始`
  - `家計消化状況`
  - LINE会話型の家計簿入力
  - LIFF登録
  - キャッシュ支払い時の経費報告転記
- Worker GETは法人GASへリダイレクトし、LIFF画面のApps Script依存ファイルが正しいGoogleドメインで読まれるように修正。
- Worker POSTはLINE Webhookを法人GASへ転送し、LINEには即時 `200 OK` を返す。

### 確認

- Worker GET: 法人GASへリダイレクトし、家計簿HTMLを表示。
- Worker POST: `200 OK`
- LINE Webhook検証: `200 OK`
- ユーザー実機確認: 公式LINEでアプリ起動OK。

## 主なGitHub変更

- `k-alert-test/gas/Code.gs`
- `k-alert-test/worker/k_alert_dedicated_worker.js`
- `k-alert-test/docs/*`
- `yumekango-worker/gas/Code.gs`
- `yumekango-worker/worker.js`
- `yumekango-worker/docs/work_log.md`

## 残作業

- 通常運用で実データ記録を確認する。
- 家計簿とKアラートそれぞれのリッチメニュー文言・導線を必要に応じて調整する。
- 秘匿値はGitHub/Notion本文には保存しない。
