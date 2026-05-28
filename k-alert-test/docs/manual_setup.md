# 手動セットアップ手順

CodexのCLI認証ではGAS更新系操作に制約があるため、当面はCodex内ブラウザでGoogle画面を操作する。

## 1. スプレッドシート作成

1. `yumekango.com` のGoogleアカウントでGoogle Driveを開く
2. 新規スプレッドシートを作成
3. タイトルを `Kアラート・テスト開発` にする
4. `アラート` シートを作成
5. `docs/sheet_schema.md` の列定義を1行目に設定
6. 必要に応じて `設定` シートを作成
7. スプレッドシートIDを控える

## 2. GAS作成

1. スプレッドシートからApps Scriptを開く
2. `gas/Code.gs` の内容を貼り付ける
3. `appsscript.json` を表示して `gas/appsscript.json` の内容を反映する
4. Script Propertiesを設定する

### Script Properties

| キー | 値 |
|---|---|
| `SPREADSHEET_ID` | `Kアラート・テスト開発` のスプレッドシートID |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging APIのチャネルアクセストークン |
| `OPENAI_API_KEY` | OpenAI APIキー |
| `OPENAI_MODEL` | 利用モデル名 |
| `CHATWORK_API_TOKEN` | 第2段階で設定 |
| `CHATWORK_ROOM_ID` | 第2段階で設定 |

## 3. GAS Webアプリデプロイ

1. デプロイ > 新しいデプロイ
2. 種類: Webアプリ
3. 実行ユーザー: 自分
4. アクセスできるユーザー: 必要に応じて設定
5. WebアプリURLを控える

## 4. Cloudflare Worker設定

1. 既存Workerを直接置き換える前に、コード差分を確認する
2. `worker/worker.js` のロジックを既存Workerへ統合する
3. Secretを設定する

### Worker Secrets

| キー | 値 |
|---|---|
| `LEGACY_GAS_URL` | 既存家計簿GAS WebアプリURL |
| `K_ALERT_GAS_URL` | KアラートGAS WebアプリURL |

## 5. LINEテスト

1. 公式LINEへ `Kアラート テストです` と送る
2. スプレッドシートへ初回コメントが保存されるか確認
3. 不足項目の聞き返しが届くか確認
4. 追加回答で同じ行が更新されるか確認

