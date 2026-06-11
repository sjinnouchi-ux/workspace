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

---

## 2026-05-28｜Kアラート疎通テスト修正

### 背景

- ユーザーが公式LINEから全角スペース区切りでテスト送信した
- スプレッドシートには過去行が見えたが、会話ログと固定返信記録が残っておらず、Cloudflareから参照していたGAS URLも404になっていた

### 対応内容

- `clasp login` を再実施し、Apps Scriptへのpush権限を復旧
- `gas/Code.gs` の最新版をApps Scriptへpush
- `appsscript.json` にWebアプリ設定を追加
  - `executeAs`: `USER_DEPLOYING`
  - `access`: `ANYONE_ANONYMOUS`
- 新しいWebアプリデプロイを作成し、HTTP 200で `KアラートGAS is running.` が返ることを確認
- Cloudflare Worker `yumekango` の `K_ALERT_GAS_URL` Secretを正しいWebアプリURLへ更新
- Cloudflare WorkerへLINE形式のテストPOSTを実施
- `アラート` シートに `Codex疎通テスト` が記録され、会話ログと固定返信文、AI未実行メモが入ることを確認
- `アラート` シートA1が `h` になっていたため `No` に修正

### 残課題

- [ ] ユーザーの公式LINEから再テストし、実際のLINE返信を確認する
- [ ] 既存の家計簿LIFF入力が従来どおり動くか確認する
- [ ] OpenAI APIの課金・利用枠を有効化してAI解析を確認する

---

## 2026-05-28｜公式LINE実機疎通成功

### 背景

- Cloudflare WorkerのKアラート接続先を正しいGAS WebアプリURLへ更新したため、実際の公式LINEから再テストする必要があった

### 対応内容

- ユーザーが公式LINEから `Kアラート　テストです` を送信
- LINE上で固定返信が届いたことをユーザーが確認
- `Kアラート・テスト開発` スプレッドシートの `アラート` シートに新規行が追加されたことを確認
- 新規行の初回コメント内容に `テストです` が記録されたことを確認
- `やり取り全文記録` にユーザー発言と固定返信が記録されたことを確認
- `備考` にAI解析未実行メモが入ることを確認

### 残課題

- [ ] 既存の家計簿LIFF入力が従来どおり動くか確認する
- [ ] OpenAI APIの課金・利用枠を有効化してAI解析を確認する
- [ ] 不足項目の自動質問とスプレッドシート分解記録を次フェーズで実装する

---

## 2026-05-28｜匿名報告AI聞き取りフロー実装

### 背景

- リッチメニューから固定テキストを送信し、匿名報告の案内文を返す運用に変更する
- その後のユーザー返信をAI解析し、必要項目がそろうまで短い聞き返しを行いたい

### 対応内容

- 開始トリガーとして `Kアラート`, `匿名報告`, `匿名報告開始`, `報告する` を許可
- 開始トリガーのみの受信時は、匿名報告の案内文を返信し、次のユーザー返信を待つ状態に変更
- ユーザーが事象内容を返信した時点で `初回コメント内容` として記録するよう変更
- AI解析で不足項目を判定し、短い聞き返し文を返す処理に変更
- 全項目がそろった場合は `報告ありがとうございます。` と短く返信する処理を追加
- OpenAI API利用枠不足時は、`記録しました。確認後に対応します。` と短く返信し、備考へ `OpenAI APIの利用枠不足` と記録するよう変更
- Apps Script version 5を作成し、既存WebアプリURLをversion 5へ更新
- `設定` シートに開始トリガー、案内文、完了文、AIエラー時返信を追記

### 残課題

- [ ] OpenAI APIの課金・利用枠を有効化して、AI解析の実機確認を行う
- [ ] 追加回答で既存行が更新されることを実機確認する
- [ ] 既存の家計簿LIFF入力が従来どおり動くか確認する

---

## 2026-05-28｜Anthropic API切り替え準備

### 背景

- OpenAI APIの利用枠不足によりAI解析が止まっている
- Anthropic APIにはクレジットがあるため、テスト用の安価モデルへ切り替える

### 対応内容

- Anthropic公式ドキュメントでMessages APIとStructured Outputsの仕様を確認
- `AI_PROVIDER` によるAIプロバイダ切り替えを実装
- `AI_PROVIDER=anthropic` の場合はAnthropic Messages APIを使用するよう変更
- Anthropic用Script Propertiesとして `ANTHROPIC_API_KEY` と `ANTHROPIC_MODEL` を追加想定
- テスト用モデルは `claude-haiku-4-5` とした
- Anthropic Structured Outputsの `output_config.format` を使い、既存のKアラートJSONスキーマを流用
- Apps Script version 6を作成し、既存WebアプリURLをversion 6へ更新
- `setupAnthropicProperties()` を追加したが、`clasp run` はAPI executable未設定のため実行不可。プロパティはApps Script画面で手動設定する

### 残課題

- [x] Apps ScriptのScript Propertiesへ `AI_PROVIDER=anthropic` を設定
- [x] Apps ScriptのScript Propertiesへ `ANTHROPIC_MODEL=claude-haiku-4-5` を設定
- [x] Apps ScriptのScript Propertiesへ `ANTHROPIC_API_KEY` を設定
- [x] 公式LINE相当のWebhook経路でAI聞き取りを確認する

---

## 2026-05-28｜Anthropic API疎通成功

### 背景

- ユーザーがApps ScriptのScript PropertiesにAnthropic用設定を追加した
- Anthropic APIでKアラートの項目分解と不足項目聞き取りが動くか確認する必要があった

### 対応内容

- Cloudflare Worker経由でLINE形式のテストPOSTを実施
- `匿名報告` の開始トリガーに対し、匿名報告案内が返ることを確認
- 事象文から `いつ`, `どこで`, `だれが`, `なにを` がスプレッドシートに分解記録されることを確認
- 不足項目 `どのように` だけを短く聞き返すことを確認
- 追加回答で同じ行の `どのように` が更新されることを確認
- 全項目充足後、`報告ありがとうございます。` が対応コメントと会話ログに記録されることを確認

### 残課題

- [ ] ユーザーの公式LINE実機で同じ流れを確認する
- [ ] 既存の家計簿LIFF入力が従来どおり動くか確認する
- [ ] 事例を増やし、聞き返し文の短さ・自然さを調整する

---

## 2026-05-28｜テスト開発完了

### 背景

- 公式LINE、Cloudflare Worker、GAS、スプレッドシート、Anthropic APIを使ったKアラートのテスト開発が一通り完了した
- 後から再開しやすいよう、完了時点の構成・確認済みフロー・残課題を別MDに整理する

### 対応内容

- `docs/test_development_summary.md` を作成
- テスト開発の目的、構成、実装済み内容、確認済みフローを整理
- Script Propertiesの必要キーを整理
- GAS承認、clasp、秘匿値、既存家計簿LIFFへの注意点を整理
- 今後の本実装・改善候補を整理

### 完了判定

- Kアラートのテスト開発はここで一旦完了
- 公式LINE相当のWebhook経路で、Anthropic APIによる項目分解、不足項目聞き取り、同一行更新、完了返信まで確認済み

### 次回候補

- 公式LINE実機でAnthropic聞き取りフローを再確認
- 家計簿LIFFの回帰確認
- 報告内容のランク付けと返信文最適化
- ChatWork API通知

---

## 2026-06-08｜KアラートLINE設定と環境値の整理

### 背景

- 家計簿LIFFとの分離後、Kアラート専用公式LINEのAPI設定値を汎用 `.env` に整理する必要があった。
- 将来的にKアラートにもLIFF詳細入力を追加する想定があるため、現在のLIFF作成可否を確認した。

### 対応内容

- KアラートProvider `Kアラート・テスト開発` 内にあるMessaging APIチャネルを確認。
- Messaging API Channel IDは `2010315694`。
- Channel secretとChannel access tokenはLINE Developersの対象チャネル画面で確認する。
- Messaging APIチャネルのLIFFタブを確認し、現在の画面上で `Messaging APIチャネルには、LIFFアプリを追加できません。LINEログインチャネルに追加してください。` と表示されることを確認。
- Kアラート用LIFF IDは現時点で未作成。今後必要になった時点で同Provider内にLINEログインチャネルを作成し、LIFFアプリを追加する方針。
- Cloudflare Worker名は `k-alert-test` と確認。

### 注意

- LINE channel access token、channel secret、Supabase service_role keyなどの秘匿値はGitHub/Notion本文には保存しない。

---

## 2026-06-09｜通報するのLIFF導線カード準備

### 背景

- リッチメニュー右下の `通報する` を押したとき、画像例のように `報告画面を開く` ボタン付きのリンク表示を出したい
- ボタン押下後はLIFFの詳細報告画面を開く想定

### 対応内容

- `gas/Code.gs` で `通報する` を `開発中です。` 返信から分離
- `通報する` / `匿名での報告となりますので、安心して報告してください` / `報告画面を開く` のFlex Messageカードを追加
- ボタンURLはScript Propertiesの `K_ALERT_LIFF_URL` から読む設計にした
- `K_ALERT_LIFF_URL` 未設定時は、報告画面URL未設定の案内文を返す
- `docs/manual_setup.md` に `K_ALERT_LIFF_URL` とLINEテスト手順を追記

### 2026-06-09 追記

- `通報する` のカード文言を、匿名報告であることが先に伝わる内容へ変更
- LINEログインチャネル `KアラートLIFF` を作成
- LIFFアプリ `Kアラート報告画面` を作成
- LIFF IDは `2010343610-N2psO7GW`
- LIFF URLは `https://liff.line.me/2010343610-N2psO7GW`
- LIFFエンドポイントURLは `https://k-alert-test.s-jinnouchi.workers.dev/report`
- Apps ScriptのScript Propertiesへ `K_ALERT_LIFF_URL` を設定済み
- GAS Webアプリへ最新版 `Code.gs` を反映し、デプロイ更新済み
- GAS POST `通報する` は `{"handled":true,"mode":"report_link"}` を返すことを確認
- Cloudflare Worker POST `通報する` は `200 OK` を返すことを確認

### 残課題

- [x] Kアラート用LINEログインチャネルを作成し、LIFF URLを発行する
- [x] Apps ScriptのScript Propertiesへ `K_ALERT_LIFF_URL` を設定する
- [x] 最新GASコードをApps Scriptへ反映し、必要ならWebアプリを再デプロイする
- [x] 公式LINE実機で `通報する` からカードが返ることを確認する
- [ ] Cloudflare Workerの `/report` にLIFF詳細報告フォームを実装する

---

## 2026-06-09｜Kアラート・（株）LOPE 公式LINE作成とMessaging API有効化

### 背景

- 先行して設定したKアラート公式LINEとは別に、来週以降の別GASプロジェクト用として新しい公式LINEを作成する
- 今回はGAS連携やWebhook実装には進まず、Messaging APIチャネルの有効化までを行う

### 対応内容

- LINE公式アカウント `Kアラート・（株）LOPE` を作成
- Basic IDは `@137dxxtv`
- LINE Official Account Manager URLは `https://manager.line.biz/account/@137dxxtv`
- Messaging API設定で新規プロバイダー `Kアラート・（株）LOPE` を作成し、同アカウントと連携
- Messaging APIのステータスが `利用中` になったことを確認
- Channel IDは `2010344304`

### 注意

- このアカウントは先ほどのKアラートLIFF設定済み公式LINEとは別アカウント
- 対応予定のGASプロジェクトも別プロジェクト
- Channel secretやアクセストークンなどの秘匿値は記録しない

### 残課題

- [ ] 来週、別GASプロジェクト側でWebhook URLと応答処理を設定する
- [ ] 必要に応じてChannel access tokenを発行し、秘匿値として保存する

---

## 2026-06-09｜LIFF報告フォームのGAS記録準備

### 背景

- 先ほど作成したKアラートLIFFで、AI APIを使わずに報告フォームの内容をスプレッドシートへ自動記載したい
- GAS由来の警告画面を出さないため、フォーム画面はCloudflare Workerで表示し、送信処理だけGASへ転送する

### 対象

- Spreadsheet ID: `1c1VK_l7xSsT29WLPZiBBYRc5we-yHfGpJuYr24dMNWA`
- 対象シートGID: `1527545544`
- ヘッダー: `No`, `企業名`, `名前（任意）`, `入力１`, `入力２`, `入力３`, `その他（自由記載）`, `相談受付希望`

### 対応内容

- `gas/Code.gs` に `source: liff_report` のJSON POST処理を追加
- A列 `No` は対象シートの既存最大値+1で自動採番するようにした
- B〜H列へフォーム内容を追記するようにした
- C列 `名前（任意）` は任意入力にした
- H列 `相談受付希望` は `希望する` / `希望しない` のみ許可するようにした
- `worker/k_alert_dedicated_worker.js` に `/report` のLIFFフォーム画面と `/api/report` のGAS転送APIを追加
- フォーム画面ではブラウザalertを使わず、画面内ステータスで送信結果を表示するようにした

### 確認

- スプレッドシートをブラウザで開き、対象ファイルが `Kアラート・テスト開発` であることを確認
- CSVエクスポートで対象シートのヘッダー行を確認
- `worker/k_alert_dedicated_worker.js` の構文チェック成功
- `gas/Code.gs` のJavaScript構文チェック成功
- ローカルプレビューで `/report` フォームの項目表示を確認

### 残課題

- [x] Apps Scriptへ最新版 `gas/Code.gs` を反映し、Webアプリを再デプロイする
- [x] Cloudflare Workerへ最新版 `worker/k_alert_dedicated_worker.js` を反映する
- [ ] LIFFからテスト送信し、A〜H列に自動記載されることを確認する

### 2026-06-09 追記

- ユーザー側でGAS Webアプリのデプロイ更新完了を確認
- WebアプリURL: `https://script.google.com/macros/s/AKfycbxm5GWC-3zcEyCNSiO7wLg5Ee4qd4c6SHKPBDLhffijuMDk4H0mRVdEwxDEThYstE2lHA/exec`
- Cloudflare Worker `k-alert-test` へ `worker/k_alert_dedicated_worker.js` をデプロイ
- Cloudflare Version ID: `02ae9f6c-f7b3-4ec5-807e-421ee2d0f86b`
- `https://k-alert-test.s-jinnouchi.workers.dev/report` がHTTP 200でLIFFフォームHTMLを返すことを確認
- ブラウザで公開フォームの表示項目を確認
- スプレッドシートへの実送信テストは、テスト行が残るため未実施

---

## 2026-06-09｜本日の作業終了メモ

### 到達点

- リッチメニュー右下 `通報する` からLIFF報告画面を開く導線を作成
- LINEログインチャネル `KアラートLIFF` とLIFFアプリ `Kアラート報告画面` を作成
- LIFF URL `https://liff.line.me/2010343610-N2psO7GW` をGAS Script Propertiesへ設定済み
- GAS Webアプリを最新版へ更新済み
- Cloudflare Worker `k-alert-test` へLIFF報告フォームを反映済み
- 公開フォーム `https://k-alert-test.s-jinnouchi.workers.dev/report` の表示を確認済み
- 別アカウント `Kアラート・（株）LOPE` の公式LINE作成とMessaging API有効化まで完了

### 次回アクション

- LIFFから報告フォームを実送信し、対象スプレッドシートA〜H列へ自動記載されることを確認する
- テスト行を残す場合は内容をテストデータとして明記する
- 必要に応じてフォーム項目名、説明文、デザインを本番向けに調整する
- `Kアラート・（株）LOPE` は来週以降、別GASプロジェクトでWebhook URLと応答処理を設定する

### 未実施

- LIFFフォームからの実送信テスト
- Notionの月次レビュー、KPI、SNS/PR、意思決定ログへの記載

---

## 2026-06-11｜Kアラート公式LINEリッチメニュー画像差し替え

### 背景

- `Kアラート・テスト開発` 公式LINEのリッチメニュー画像を新デザインへ差し替えたい
- 管理画面には既存リッチメニューが表示されず、過去記録からMessaging APIで作成・デフォルト設定されていることを確認した

### 対応内容

- 対象公式LINE: `@953upiqr`
- Messaging API Channel ID: `2010315694`
- LINE APIで現在のデフォルトリッチメニューIDを取得
- 既存リッチメニューは `2500x1686`、エリア3つであることを確認
- エリア構成は上段 `大人の保健室`、下段左 `相談する`、下段右 `通報する`
- 新画像を既存メニューサイズに合わせて `2500x1686` JPEGへ変換
- 既存リッチメニュー画像をGoogle Driveへバックアップ
- LINE APIでは既存画像の上書きができないため、同じタップ領域で新リッチメニューを作成し、画像をアップロードしてデフォルト設定を切り替え

### 結果

- 旧リッチメニューID: `richmenu-db41028867c5f9a95b15744b80b4711d`
- 新リッチメニューID: `richmenu-3eab5ad0af2747ff7933d15461431bf6`
- 新リッチメニューがデフォルト設定済み
- 新画像取得確認: `796,496 bytes`
- 新画像保存先: `G:\マイドライブ\Codex保存\画像\k-alert-richmenu_2500x1686_api.jpg`
- バックアップ保存先: `G:\マイドライブ\Codex保存\画像\k-alert-richmenu-backup-20260611-124113.jpg`

### 次回確認

- 実機LINEでリッチメニュー表示が新画像に変わっていることを確認する
- `相談する` と `通報する` のタップ位置が意図どおり反応することを確認する

---

## 2026-06-11｜LIFF報告フォームの任意項目と相談受付選択修正

### 背景

- `通報する` から開くLIFF報告フォームで、`相談受付希望` の `希望する` / `希望しない` が選択しづらい状態になっていた
- `その他（自由記載）` は任意項目にしたいが、フォームとGASの両方で必須扱いになっていた

### 対応内容

- `worker/k_alert_dedicated_worker.js` のCSSを修正し、通常のテキスト入力だけに `appearance: none` を適用するよう変更
- ラジオボタンはネイティブ表示と `accent-color` を使い、選択状態が見えるようにした
- `その他（自由記載）` の `required` を外し、画面上も `任意` と表示するよう変更
- `gas/Code.gs` のLIFF報告バリデーションから `freeText` を必須項目として除外
- `docs/manual_setup.md` の入力仕様を、C列・G列は任意に更新

### 確認

- `worker/k_alert_dedicated_worker.js` の構文チェック成功
- `gas/Code.gs` のJavaScript構文チェック成功

### 残課題

- Apps Scriptへ最新版 `gas/Code.gs` を反映し、Webアプリを再デプロイする
- Cloudflare Workerへ最新版 `worker/k_alert_dedicated_worker.js` を反映する
- LIFF実機で `相談受付希望` の選択と、`その他（自由記載）` 空欄送信を確認する
