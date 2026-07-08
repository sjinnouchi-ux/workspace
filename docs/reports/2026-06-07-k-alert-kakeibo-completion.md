# 2026-06-07 家計簿LIFF 分離完了報告

## 完了概要

家計簿側を法人GASへ移し、過去のKアラート・テスト版に由来するデモ機能を削除して本来の家計簿機能だけに戻した。

## Kアラート・テスト版

過去にテスト版が存在したが、詳細なコード、GAS、Sheets、Worker、LIFF、LINE設定、作業ログは2026-07-09に破棄方針へ変更した。
現行のKアラート開発・運用はKアラート本番開発リポジトリを参照する。

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

- `yumekango-worker/gas/Code.gs`
- `yumekango-worker/worker.js`
- `yumekango-worker/docs/work_log.md`

## 残作業

- 通常運用で実データ記録を確認する。
- 秘匿値はGitHub/Notion本文には保存しない。

## 2026-06-08 追加整理

### LINE Developers / Official Account

- LINE Developers上の重複Providerを整理。
  - 空Provider `2004471073` はチャネルなしを確認して削除。
  - 本番Provider `2004471113` は `ゆめ看護` から `家計簿` へ名称変更。
- 家計簿公式LINEアカウント名を `ゆめ看護` から `家計簿` へ変更し、公開済み状態を確認。
- 家計簿Messaging APIチャネル:
  - Channel ID: `2007959459`
  - Channel access tokenはMessaging API設定画面下部で確認する。
- Kアラート・テスト版の詳細は破棄対象とし、現行のKアラート運用は本番開発リポジトリを参照する。

### Environment Values

- Notion:
  - Projects DB ID: `eabfb1bf75aa419986c6fe2d1cb0eb2b`
  - Notion API version: `2022-06-28`
- API Monitor:
  - Windows local DB path: `C:\Users\irodo\Documents\Codex\2026-06-03\mac-github\workspace\api-monitor\data\api_log.db`
- Cloudflare Workers:
  - 家計簿: `yumekango`
  - kango-mamori用Workerは現時点で未作成または未使用。
- Supabase:
  - dori-manga URL: `https://vdntqwtywxyjxelycavx.supabase.co`
  - market-pilot URL: `https://coeepfbfvtkwgtnmzwtz.supabase.co`
  - anon/publishable keyとservice_role keyはSupabase API Keys画面から取得する。service_role keyはGitHub/Notion/チャットに保存しない。

## 2026-06-08 家計簿アプリ最終復旧

### 背景

- Kアラート機能を家計簿GASから削除した際、家計簿公式LINEで使っていた補助機能まで削除されていた。
- 公式LINE上でリッチメニュー2/3が反応しない、リッチメニュー4の合計行が0%になる、LIFF画面にGoogle Apps Scriptの警告が出る状態になっていた。

### 対応内容

- `公式LINE_2` を使う情報参照と、`公式LINE_3` へ記録する保管入力を家計簿公式LINEの補助機能として復旧。
- `家計消化状況` は `集計` シートの当月列を優先して読み、`計（プライベート）` / `計（プライベート・一部経費）` / `総計` などの合計行も正しく表示できるよう修正。
- Cloudflare Worker `yumekango` を更新し、GASのApps Scriptラッパーから本体HTMLだけを抽出して返す方式へ変更。
- `global.env` から `CLOUDFLARE_API_TOKEN` を読み込み、Cloudflare API経由でWorker本番デプロイを実施。

### 確認

- GAS `?action=getCategories`: `200 OK`
- GAS通常GET: `200 OK`
- Worker通常GET: `200 OK`
- WorkerカテゴリJSON: `200 OK`
- Worker通常GETでGASへの302リダイレクトなし。
- Worker通常GETでApps Scriptラッパーなし。
- Worker通常GETで `script.google.com` 文字列なし。
- Worker内のLIFF送信先 `GAS_URL` は `https://yumekango.s-jinnouchi.workers.dev/` に置換済み。
- Cloudflare Worker Version ID: `ed9fd1dd-7370-4db6-ba20-0ce10e9519a1`

### 最終状態

- 家計簿アプリは完了。
- 今後の通常運用では、月次レビュー時に家計簿入力・リッチメニュー2/3/4・LIFF表示を軽く確認する。
