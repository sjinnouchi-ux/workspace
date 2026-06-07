# Kアラート・テスト開発 完了サマリー

## 完了日

2026-05-28

## 目的

公式LINEから匿名報告を受け付け、AIが報告内容を `いつ`, `どこで`, `だれが`, `だれに`, `なにを`, `どのように` に分解し、不足項目だけを短く聞き返すテスト環境を作る。

## 構成

| 項目 | 内容 |
|---|---|
| 公式LINE Webhook | 既存Cloudflare Worker `yumekango` |
| Worker URL | `yumekango.s-jinnouchi.workers.dev` |
| GASプロジェクト | `Kアラート・テスト開発 GAS` |
| スプレッドシート | `Kアラート・テスト開発` |
| 記録シート | `アラート` |
| AIプロバイダ | Anthropic |
| テストモデル | `claude-haiku-4-5` |

## 実装済み

- `k-alert-test/` プロジェクトを作成
- `Kアラート・テスト開発` スプレッドシートを新規作成
- `アラート` / `設定` シートを作成・整形
- Apps Script Webアプリを作成
- Cloudflare Worker `yumekango` へKアラートGASのルーティングを追加
- 既存の家計簿LIFF向けGET処理は維持
- 公式LINEのテキストPOSTをKアラートGASへ先に照会し、対象外なら既存GASへフォールバックする構成にした
- リッチメニューの `相談する` を開始トリガーとして、匿名相談の案内文を返信
- リッチメニューの `大人の保健室`, `通報する` はデモ段階では `開発中です。` と返信
- ユーザーの次返信を初回コメントとして記録
- AI解析で不足項目だけを短く聞き返す処理を実装
- 全項目がそろった場合は `報告ありがとうございます。` と返信
- OpenAI API利用枠不足を受け、Anthropic APIへ切り替え
- Anthropic APIで項目分解と不足項目聞き取りが動作することを確認

## 確認済みフロー

1. `相談する` を受信
2. 匿名報告の案内文を返信
3. 事象文を受信
4. スプレッドシートへ初回コメントを記録
5. AIが `いつ`, `どこで`, `だれが`, `だれに`, `なにを` を分解
6. 不足項目 `どのように` だけを短く聞き返し
7. 追加回答を受信
8. 同じ行の `どのように` を更新
9. 全項目充足後に `報告ありがとうございます。` と返信

## Script Properties

本番値やAPIキーはGitHubに記録しない。

| キー | 用途 |
|---|---|
| `SPREADSHEET_ID` | Kアラート記録先スプレッドシート |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE返信用アクセストークン |
| `AI_PROVIDER` | `anthropic` |
| `ANTHROPIC_API_KEY` | Anthropic APIキー |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5` |
| `OPENAI_API_KEY` | OpenAIへ戻す場合のみ使用 |
| `OPENAI_MODEL` | OpenAIへ戻す場合のみ使用 |

## 重要な運用メモ

- GAS初回承認や `clasp login` は、Codex内ブラウザだけでは完了しない場合がある。
- 新規GASや再認証が必要な場合は、通常Chromeでユーザー本人が承認し、その後Codexで作業を続行する。
- `clasp run` はAPI executable未設定のため使えない。Script PropertiesはApps Script画面で手動設定する。
- APIキー、LINEトークン、GAS WebアプリURLなどの秘匿値はGitHubに書かない。
- 既存家計簿LIFFと同じ公式LINE/Workerを使っているため、Worker更新時は家計簿LIFFの回帰確認を行う。

## 残課題

テスト開発としての入口確認は完了。今後の本実装・改善候補は以下。

- ユーザー本人の公式LINE実機で、Anthropic聞き取りフローをもう一度確認する
- 既存の家計簿LIFF入力が従来どおり動くか確認する
- 報告内容のランク付けを追加する
- 緊急度に応じて返信文を最適化する
- ChatWork API通知を追加する
- LINE署名検証を追加または確認する
- 事例を増やし、聞き返し文の短さ・自然さを調整する

## 主要ファイル

| ファイル | 内容 |
|---|---|
| `k-alert-test/gas/Code.gs` | KアラートGAS本体 |
| `k-alert-test/gas/appsscript.json` | GAS manifest |
| `k-alert-test/worker/yumekango_worker_integration.js` | Cloudflare Worker統合コード |
| `k-alert-test/docs/work_log.md` | 作業ログ |
| `k-alert-test/docs/manual_setup.md` | 手動設定手順 |
| `k-alert-test/docs/cloudflare_worker_setup.md` | Worker接続手順 |

## 完了判定

テスト開発は完了。

完了時点で、公式LINE相当のWebhook経路からAnthropic APIによる項目分解、不足項目聞き取り、同一行更新、完了返信まで確認済み。
