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
| `AI_PROVIDER` | `anthropic` |
| `ANTHROPIC_API_KEY` | Anthropic APIキー |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5` |
| `K_ALERT_LIFF_URL` | `通報する` から開くLIFF報告画面URL |
| `OPENAI_API_KEY` | OpenAI APIへ戻す場合のみ使用 |
| `OPENAI_MODEL` | OpenAI APIへ戻す場合のみ使用 |
| `CHATWORK_API_TOKEN` | 第2段階で設定 |
| `CHATWORK_ROOM_ID` | 第2段階で設定 |

補足:

- `AI_PROVIDER=anthropic` の場合、`ANTHROPIC_API_KEY` と `ANTHROPIC_MODEL` を使う
- `AI_PROVIDER=openai` の場合、`OPENAI_API_KEY` と `OPENAI_MODEL` を使う
- Anthropicのテストモデルは `claude-haiku-4-5` を基本にする
- API利用枠不足時は、ユーザーへ `記録しました。確認後に対応します。` と短く返信する

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

1. 公式LINEへ `相談する` と送る
2. 匿名相談の案内文が届くか確認
3. `通報する` と送る
4. `警報OBへ相談` のカードと `報告画面を開く` ボタンが届くか確認
5. `報告画面を開く` から `K_ALERT_LIFF_URL` のLIFF報告画面が開くか確認
6. `大人の保健室` と送る
7. `開発中です。` と届くか確認
8. 事象内容を返信する
9. スプレッドシートへ初回コメントが保存されるか確認
10. OpenAI API利用枠が有効な場合、不足項目の短い聞き返しが届くか確認
11. 追加回答で同じ行が更新されるか確認
