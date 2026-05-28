# 実装計画

## Phase 1: 土台作成

- [x] GitHubに専用プロジェクトを作成
- [x] スプレッドシート構成を定義
- [x] GAS雛形を作成
- [x] Worker雛形を作成
- [x] `yumekango.com` 側でテスト用スプレッドシートを作成
- [x] `yumekango.com` 側でテスト用GASを作成

## Phase 2: GAS単体テスト

- [x] `アラート` シートのヘッダー作成
- [x] `アラート` / `設定` シートの初期整形
- [x] Script Properties設定
- [x] テストJSONで行追加できることを確認
- [ ] OpenAI APIで初回コメントを構造化できることを確認
- [x] 不足項目の質問文を生成できることを確認

補足:

- `SPREADSHEET_ID`, `OPENAI_MODEL`, `LINE_CHANNEL_ACCESS_TOKEN`, `OPENAI_API_KEY` は設定済み
- OpenAI APIは利用枠不足により、AI解析の実行確認が未完了
- `CHATWORK_API_TOKEN` と `CHATWORK_ROOM_ID` は第2段階で設定
- Apps Scriptの初回承認画面がブラウザ内で進まなかったため、初期整形は既存のGoogle Sheets API認証で実施

## Phase 3: LINE連携

- [x] WorkerからKアラートGASへルーティング
- [x] `Kアラート ...` の初回投稿を保存
- [x] リッチメニュー開始文への匿名報告案内返信
- [ ] OpenAI API利用枠復旧後、不足項目のLINE返信
- [ ] 追加回答で既存行を更新
- [ ] 完了メッセージ返信を実機確認

補足:

- 公式LINEはユーザー本人と奥様のみで利用しているため、現在運用中の公式LINEでテストする
- `wrangler` はログイン済み
- `yumekango_worker_integration.js` は既存LIFF機能を残し、POSTだけKアラートGASへ先に照会する統合案

## Phase 4: ChatWork通知

- [ ] ChatWork APIトークンを設定
- [ ] 通知先ルームIDを設定
- [ ] 完了時にChatWorkへ通知
- [ ] 通知文面を調整

## Phase 5: 安定化

- [ ] LINE署名検証を追加または確認
- [ ] エラー時の備考記録
- [ ] GAS実行ログ確認手順の確立
- [ ] トークン直書き箇所の整理と再発行判断
