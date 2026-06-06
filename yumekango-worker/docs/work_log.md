# yumekango-worker 作業ログ

## 2026-06-01｜公式LINE 家計消化状況の月初不具合調査

### 背景
- 2026年6月1日になってから、公式LINEで家計簿の入力リンクは届く一方、家計消化状況の報告が出せないという相談があった
- 未入力のため表示できないのか、月替わり処理が設計されていないのかを切り分ける必要があった

### 対応内容
- GitHub上の `yumekango-worker/worker.js` と関連ドキュメントを確認
- 本番Worker URLへGETし、LIFFフォームが6月表示で返ることを確認
- GASのカテゴリ取得エンドポイントがカテゴリJSONを返すことを確認
- ユーザー提供のGASコードを確認し、`sendBudgetReport()` の集計参照ロジックを調査

### 結果
- 入力リンクとLIFFフォーム表示は動作しており、Worker全体やカテゴリ取得は停止していない
- `sendBudgetReport()` は現在月をタイトル表示に使うだけで、月別データを検索・生成していない
- 利用状況の中身は常に `集計` シートの `A1:D35` に依存しているため、6月の集計表・数式・参照範囲が未作成または未更新だと報告できない
- ユーザーが6月分として1円入力したところ報告自体は表示されたが、表示データは5月のままだったため、`集計` シートの数式または表示範囲が5月参照のままになっている可能性が高い

### 残課題
- [ ] `集計` シートの6月用数式・参照範囲を確認する
- [ ] 必要ならGAS側に当月行/当月列を検出する処理、または未入力時も0円表示する処理を追加する
- [ ] LINEチャネルアクセストークンがチャット上に露出したため、再発行とScript Properties移行を検討する

## 2026-06-01｜家計消化状況GAS差し替え版作成

### 背景
- 6月分を1円入力すると報告自体は表示されたが、表示データが5月のままだった
- `sendBudgetReport()` が `集計!A1:D35` のC/D列にある月固定数式へ依存しており、月替わり時に古い月の値を返す構造だった
- ユーザーがApps Scriptへフルコードを貼り替え、デプロイ更新後のURLを共有する方針になった

### 対応内容
- `yumekango-worker/gas/Code.gs` を追加
- `sendBudgetReport()` を修正し、`集計` シートからは項目名と予算のみ読み、当月実績は `家計簿` シートの当月行からGAS側で直接集計する方式に変更
- `LINE_CHANNEL_ACCESS_TOKEN`, `SPREADSHEET_ID`, `EXPENSE_SS_ID` はコード直書きせず、Script Propertiesから読む方式に変更
- `node --check` 相当の構文確認を実施

### 結果
- `集計` シートの5月固定数式に依存せず、LINE表示時点の当月ラベル（例: `6月`）で実績を集計できる差し替え版を作成

### 残課題
- [ ] Apps ScriptのScript Propertiesに `LINE_CHANNEL_ACCESS_TOKEN`, `SPREADSHEET_ID`, `EXPENSE_SS_ID` を設定する
- [ ] ユーザーがApps Scriptへ `yumekango-worker/gas/Code.gs` を貼り替えてデプロイ更新する
- [ ] 更新後URLをCloudflare Workerの `LEGACY_GAS_URL` Secretへ反映する

## 2026-06-01｜GASデプロイ更新後の疎通確認

### 背景
- ユーザーが `irodori.nurse@gmail.com` 側のGASエディタでコードを修正し、デプロイ更新したURLを共有した
- Cloudflare Workerの `LEGACY_GAS_URL` 更新前に、GAS URL単体とWorker経由の疎通を確認する必要があった

### 対応内容
- 共有されたGAS URLの `?action=getCategories` へ直接アクセス
- 本番Worker URLのLIFF画面表示を確認
- `npx wrangler --version` でWrangler CLIが利用可能なことを確認

### 結果
- 共有GAS URLは `スクリプト関数が見つかりません: doGet` を返した
- 本番WorkerはLIFF HTML自体を返すが、GASカテゴリ取得が失敗している可能性がある
- Cloudflare WorkerのSecret更新は、GAS側が `doGet` を含む完全なコードで再デプロイされるまで保留した

### 残課題
- [ ] GASエディタを元のフルコードへ戻し、`sendBudgetReport()` だけを最小パッチへ差し替える
- [ ] 再デプロイ後、GAS URLの `?action=getCategories` がJSONを返すことを確認する
- [ ] 問題なければCloudflare Workerの `LEGACY_GAS_URL` を更新する

## 2026-06-01｜公式LINE GAS再デプロイ後の復旧確認

### 背景
- ユーザーがGASコードを再構成し、公式LINE用GASを再デプロイした
- 前回は `doGet` が見つからない状態だったため、GAS単体とWorker経由の疎通確認が必要だった

### 対応内容
- 共有されたGAS URLの `?action=getCategories` にアクセス
- 共有されたGAS URLの通常GETにアクセス
- 本番Worker `https://yumekango.s-jinnouchi.workers.dev/` にアクセス

### 結果
- `?action=getCategories` はカテゴリJSONを返した
- GAS通常GETは `doGet` が認識され、家計簿入力HTMLを返した
- Worker経由のLIFF画面も6月表示で返った
- 共有URLは既存Worker内のGAS URLと同じため、Cloudflare Workerの `LEGACY_GAS_URL` Secret更新は不要と判断

### 残課題
- [ ] 公式LINEで `家計消化状況` を送信し、6月実績で表示されることを実機確認する

## 2026-06-06｜交通費（経費計上）の支払方法選択対応

### 背景
- `経費計上` / `経費計上（事業関連）` は支払方法（キャッシュ / カード）を選択し、キャッシュの場合のみ経費報告スプレッドシートへ転写する仕様になっている
- `交通費（経費計上）` も同じ扱いにしたい

### 対応内容
- `categoryNeedsPayment_()` を追加し、スプレッドシートH列が `TRUE` の項目に加えて、`交通費（経費計上）` も支払方法選択対象にした
- LIFF画面のカテゴリJSONと、LINE会話入力フローの両方で同じ判定を使うようにした

### 残課題
- [ ] GASエディタへ `yumekango-worker/gas/Code.gs` を反映し、デプロイを更新する
- [ ] LIFF画面で `交通費（経費計上）` 選択時に支払方法カードが表示されることを確認する
- [ ] キャッシュ選択時だけ `経費報告` シートへ転写されることを確認する

## 2026-06-06｜Kアラートデモ機能を残したまま分離しやすく整理

### 背景
- 現在稼働中のGASには家計簿機能に加えて、`保管と入力` / `情報参照` / `公式LINE_2` / `公式LINE_3` を使うデモ機能が含まれている
- デモ機能は近く削除予定だが、別の公式LINEアカウントへ移植するまでは残す必要がある

### 対応内容
- デモ系処理を `DEMO機能（Kアラート移植予定）` ブロックへ集約
- `startDemoTextStorage_()`, `finishDemoTextStorage_()`, `sendDemoInfoOptions_()`, `replyDemoInfoIfMatched_()` に切り出し
- 家計簿本体の `家計簿入力開始`, `家計消化状況`, LIFF登録、経費転写処理は維持

### 残課題
- [ ] 別公式LINEアカウント作成後、DEMO機能ブロックを移植する
- [ ] 移植後、このGASからデモ機能ブロックと `公式LINE_2` / `公式LINE_3` 依存を削除し、家計簿専用コードへ整理する
