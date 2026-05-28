# Kアラート・テスト開発 作業ログ

---

## 2026-05-28｜プロジェクト初期化

### 背景

- 公式LINE AI連携の開発を1からCodexで支援する
- 本番家計簿や株式通知に影響しないよう、Kアラート専用の開発フォルダを作る

### 対応内容

- `k-alert-test/` プロジェクトを作成
- スプレッドシート設計を `docs/sheet_schema.md` に整理
- 実装計画を `docs/implementation_plan.md` に整理
- 手動セットアップ手順を `docs/manual_setup.md` に整理
- GAS雛形を `gas/Code.gs` に作成
- Cloudflare Workerルーティング雛形を `worker/worker.js` に作成

### 残課題

- [x] `yumekango.com` 側で `Kアラート・テスト開発` スプレッドシートを作成
- [x] `yumekango.com` 側でGASを作成
- [ ] Script Propertiesを設定
- [ ] WorkerへKアラートルーティングを統合
- [ ] 公式LINEで初回テスト

---

## 2026-05-28｜Google側テスト環境作成

### 背景

- `Kアラート・テスト開発` 用のスプレッドシートを完全新規で作成する
- 作成したスプレッドシートへGASを接続し、Kアラート処理のテスト土台を整える

### 対応内容

- `yumekango.com` アカウントで新規Googleスプレッドシートを作成
- スプレッドシート名を `Kアラート・テスト開発` に変更
- `アラート` シートを作成し、指定ヘッダーを設定
- `設定` シートを作成し、トリガー文言、緊急度候補、必須項目を設定
- 新規Apps Scriptプロジェクト `Kアラート・テスト開発 GAS` を作成
- `gas/Code.gs` のGAS雛形をApps Scriptへ貼り付けて保存
- Script Propertiesに `SPREADSHEET_ID` と `OPENAI_MODEL` を設定

### 残課題

- [ ] Script Propertiesに `LINE_CHANNEL_ACCESS_TOKEN` を設定
- [ ] Script Propertiesに `OPENAI_API_KEY` を設定
- [ ] Webアプリとしてデプロイ
- [ ] WorkerへKアラートGAS URLを設定
- [ ] LINEから初回テスト

---

## 2026-05-28｜スプレッドシート初期整形

### 背景

- APIキー設定やLINE連携の前に、`Kアラート・テスト開発` スプレッドシートを見やすく整えたい
- 既存のAI連携ロジックには触れず、見た目だけ整える

### 対応内容

- `gas/Code.gs` に `setupSpreadsheetFormatting()` と関連整形関数を追加
- Apps Script側へ更新済みGASコードを貼り付けて保存
- Apps Scriptの初回承認画面がブラウザ内で進まなかったため、既存のGoogle Sheets API認証で直接整形を実施
- `アラート` シートにヘッダー色、罫線、固定行、フィルター、列幅、折り返しを設定
- `設定` シートにヘッダー色、罫線、固定行、列幅、折り返しを設定

### 残課題

- [x] Apps Script上で `setupSpreadsheetFormatting()` を実行できるよう、必要時にGoogle認可を完了する
- [ ] 固定返信・初回コメント保存のみのテスト用フローを検討する

---

## 2026-05-28｜GAS初回承認フロー確認

### 背景

- Codex内ブラウザでApps Scriptの `権限を確認` を押しても、承認画面が開かず警告ログに戻る事象があった
- 今後、新規GAS作成時に同じ問題が起きた場合の標準フローを決めたい

### 対応内容

- ユーザーが通常Chromeで `Kアラート・テスト開発 GAS` の初回承認を実施
- 承認後、Codex内ブラウザから `setupSpreadsheetFormatting` を再実行
- 実行ログで `実行開始` と `実行完了` を確認
- Codex側のGAS運用メモに、通常Chromeで本人承認する標準フローを追記

### 残課題

- [ ] 次回以降の新規GASでも同フローを使う
- [ ] Webアプリデプロイ時の承認・公開範囲は別途確認する

---

## 2026-05-28｜公式LINE実テスト準備

### 背景

- APIキーとLINEチャネルアクセストークンがGAS Script Propertiesへ設定された
- 現在運用中の公式LINEはユーザー本人と奥様のみの利用のため、本番公式LINEでテストしてよい方針になった

### 対応内容

- GAS Webアプリをデプロイ
- デプロイ設定は `自分（s.jinnouchi@yumekango.com）として実行` / `アクセスできるユーザー: 全員`
- `OPENAI_API_KEY`, `OPENAI_MODEL`, `SPREADSHEET_ID`, `LINE_CHANNEL_ACCESS_TOKEN` がScript Propertiesに存在することを確認
- `k-alert-test/gas/Code.gs` に初回保存・固定返信テストモードを追加
- `clasp push --force` を試したが、`invalid_grant / rapt_required` で失敗
- Codex内ブラウザのクリップボード制約により、最新版GASコードの貼り付けは未完了
- `k-alert-test/worker/yumekango_worker_integration.js` にCloudflare Worker統合案を作成
- `k-alert-test/docs/cloudflare_worker_setup.md` にCloudflare Dashboardでの接続手順を追加

### 残課題

- [ ] 最新版GASコードをApps Scriptへ反映し、必要なら再デプロイする
- [x] Cloudflare Workerへ `LEGACY_GAS_URL` と `K_ALERT_GAS_URL` を設定する
- [x] Cloudflare Workerへ統合コードを反映する
- [ ] 公式LINEで `Kアラート テストです` を送信して疎通確認する

---

## 2026-05-28｜Cloudflare Worker本番接続

### 背景

- 公式LINE Webhook URLは既存のCloudflare Worker `yumekango` に向いている
- 既存の家計簿LIFF/家計簿GASを維持しつつ、LINEテキスト投稿だけKアラートGASへ先に振り分けたい

### 対応内容

- Cloudflare Dashboardログイン後、Wrangler CLIのOAuth認証を実施
- Worker `yumekango` に `LEGACY_GAS_URL` と `K_ALERT_GAS_URL` をSecretとして登録
- `k-alert-test/worker/yumekango_worker_integration.js` をWorker `yumekango` へデプロイ
- デプロイ先は `yumekango.s-jinnouchi.workers.dev`
- GET確認でLIFFフォームHTMLがHTTP 200で返ることを確認
- Wranglerデプロイ履歴で新しいVersion IDが作成されたことを確認

### 残課題

- [ ] 最新版GASコードをApps Scriptへ反映し、固定返信テストモードを有効化する
- [ ] 公式LINEでテキスト投稿し、Kアラート用スプレッドシートへの記録を確認する
- [ ] 既存の家計簿LIFF入力が従来どおり動くか確認する
