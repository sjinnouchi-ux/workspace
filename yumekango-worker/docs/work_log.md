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

## 2026-06-07｜Kアラートデモ機能を家計簿GASから削除

### 背景
- Kアラートを別公式LINEと法人GASへ移したため、家計簿GASを本来の家計簿機能だけに戻す。

### 対応内容
- `保管と入力` / `情報参照` / `wait_text` の入口を削除。
- `公式LINE_2` / `公式LINE_3` 依存処理を削除。
- `startDemoTextStorage_()`, `finishDemoTextStorage_()`, `sendDemoInfoOptions_()`, `replyDemoInfoIfMatched_()`, `saveTextToSheet()` を削除。
- 家計簿本体の `家計簿入力開始`, `家計消化状況`, LINE会話型入力、LIFF登録、経費転写処理は維持。

### 残課題
- [ ] 法人GASエディタへ `yumekango-worker/gas/Code.gs` を反映し、デプロイを更新する。
- [ ] 家計簿公式LINEで `家計簿入力開始` と `家計消化状況` を実機確認する。

## 2026-06-07｜法人GAS URL向けに家計簿Workerを整理

### 背景
- 家計簿GASを法人GASとしてデプロイしたため、Cloudflare Worker `yumekango` も新しいGAS URLへ向ける。

### 対応内容
- `yumekango-worker/worker.js` に混ざっていたmultipart境界文字を除去。
- WorkerをシンプルなGAS中継構成に整理。
- GETは新GASのHTML/JSONを取得して返す。
- POSTはLINE Webhook本文を新GASへ転送し、LINEには即時 `200 OK` を返す。
- 新GAS WebアプリURL:
  - `https://script.google.com/macros/s/AKfycbx2Dw3tpCTC8PZxRwIH68d00TflY98ekTAkxv2-KY7t7EByJdcN676gUOonCg58rg_4/exec`

### 残課題
- [ ] Cloudflare Worker `yumekango` のコードをGitHub版に差し替えてデプロイする。
- [ ] `https://yumekango.s-jinnouchi.workers.dev/` のGET/POSTを確認する。
- [ ] 家計簿公式LINEのWebhook検証と実機確認を行う。

## 2026-06-08｜LINE Developers表示名と環境値の整理

### 背景
- 家計簿LIFFとKアラートの分離後、LINE Developers上に `ゆめ看護` Providerが重複して表示され、家計簿のMessaging APIチャネルとLIFFチャネルの識別が分かりづらくなっていた。
- 汎用 `.env` に入れるため、Cloudflare / Notion / API Monitor / Supabase の参照値も整理する必要があった。

### 対応内容
- 空Provider `2004471073` はチャネルなしを確認して削除。
- 本番Provider `2004471113` を `ゆめ看護` から `家計簿` へ名称変更。
- LINE Official Account Managerで公式LINEアカウント名を `ゆめ看護` から `家計簿` へ変更し、公開済み状態を確認。
- 家計簿Messaging APIチャネルは `2007959459`、LIFF IDは `2010069897-X9JY7R2h` と整理。
- Cloudflare Worker名は `yumekango` と確認。
- Notion Projects DB ID、API Monitor SQLite DBパス、SupabaseプロジェクトURLを確認。

### 注意
- LINE channel access token、Supabase service_role key、Notion tokenなどの秘匿値はGitHub/Notion本文には保存しない。

## 2026-06-08｜家計簿GASのリッチメニュー補助機能復旧

### 背景
- Kアラート機能を家計簿GASから削除した際、家計簿公式LINEで利用していたリッチメニュー補助機能も一緒に削除されていた。
- 具体的には、リッチメニュー2/3の `情報参照` / `保管と入力` が反応しない、リッチメニュー4の家計消化状況の集計がズレる、LIFF画面でApps Script由来の表示が再発する、という相談があった。

### 対応内容
- `公式LINE_2` を使う情報参照と、`公式LINE_3` へ記録する保管入力を、Kアラートではなく家計簿公式LINEの補助機能として復旧。
- `家計消化状況` の当月判定を、`6月` の完全一致だけでなく、日付・数値月・全角数字・年月文字列にも対応するよう修正。
- Cloudflare WorkerのGET処理をGASへの302リダイレクトから、GASのHTML/JSONをWorker側で取得して返す方式へ変更。

### 残課題
- [ ] GASエディタへ `yumekango-worker/gas/Code.gs` を反映し、デプロイを更新する。
- [ ] Cloudflare Worker `yumekango` をデプロイする。
- [ ] 公式LINEでリッチメニュー2/3/4とLIFF表示を実機確認する。

## 2026-06-08｜家計消化状況の合計行0%表示を修正

### 背景
- 公式LINEの家計消化状況で、個別項目は表示される一方、`計（プライベート）` / `計（プライベート・一部経費）` / `総計` が0%になっていた。
- ユーザー共有のスプレッドシートURLで、家計簿プロジェクトの対象スプレッドシートIDと一致し、`集計` タブに月別列があることを確認した。

### 対応内容
- `集計` シートの読み取り範囲を `A1:D35` から `A1:P35` に広げ、ヘッダー行から当月列を検出するよう修正。
- `集計` シートの当月列に実績がある場合は、その値を優先してLINE表示に使うよう修正。
- これにより、家計簿シート上のカテゴリ名と一致しない合計行も、`集計` シートの月別実績から正しく表示できる。

### 残課題
- [ ] GASエディタへ最新版 `yumekango-worker/gas/Code.gs` を反映し、デプロイを更新する。
- [ ] Cloudflare Worker `yumekango` をデプロイする。
- [ ] LINE実機で `家計消化状況` の合計行が0%ではなくなることを確認する。

## 2026-06-08｜家計簿アプリ完了報告

### 背景
- ユーザーから家計簿アプリのプロジェクト完了報告があった。
- 直前の復旧作業で、リッチメニュー補助機能、家計消化状況の合計行、LIFFのApps Script警告対策まで完了した。

### 対応内容
- ユーザーが最新版GASを法人GASへ反映し、デプロイ更新したことを確認。
- `global.env` から `CLOUDFLARE_API_TOKEN` を読み込み、Cloudflare Worker `yumekango` を本番デプロイ。
- Worker側でApps Scriptラッパーを除去し、LIFFフォーム本体HTMLだけを返す方式へ更新。
- 作業内容を `docs/reports/2026-06-07-k-alert-kakeibo-completion.md` に追記。

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
- 今後は通常運用・月次レビュー時に、家計簿入力、リッチメニュー2/3/4、LIFF表示を確認する。
