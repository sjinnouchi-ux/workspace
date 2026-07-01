# 2026-06-26 Kアラート本番実装向け 最新ハンドオフ

このMDは、別チャットでKアラート本番実装を続けるための現時点の正本メモです。
古い `k-alert-test` の作業ログや別チェックアウトには古いLIFF/GAS/リッチメニュー情報が残っているため、本番実装前にまずこのファイルを読んでください。

## 正本

- GitHubリポジトリ: `https://github.com/sjinnouchi-ux/workspace`
- 作業ブランチ: `codex/k-alert-5w1h-liff`
- 正本ローカル作業ツリー: `C:\Users\irodo\Documents\Codex\2026-06-08\github-notion\work\repos\workspace-kalert-liff-fix-push`
- Kアラートプロジェクト: `k-alert-test`
- 詳細ログ: `k-alert-test/docs/work_log.md`
- 手順: `k-alert-test/docs/manual_setup.md`
- スプレッドシート設計: `k-alert-test/docs/sheet_schema.md`

## 現在の公開設定

- LIFF URL: `https://liff.line.me/2010343610-N2psO7GW`
- LIFF Worker URL: `https://k-alert-test.s-jinnouchi.workers.dev/report`
- Worker API: `https://k-alert-test.s-jinnouchi.workers.dev/api/report`
- Cloudflare Worker名: `k-alert-test`
- 最新確認Worker Version ID: `f90b2a41-05ef-44b3-824a-bd3f13d15489`
- GAS WebアプリURL: `https://script.google.com/macros/s/AKfycbxm5GWC-3zcEyCNSiO7wLg5Ee4qd4c6SHKPBDLhffijuMDk4H0mRVdEwxDEThYstE2lHA/exec`
- LINEログインチャネル: `KアラートLIFF`
- LINEログインチャネルID: `2010343610`
- LIFF ID: `2010343610-N2psO7GW`
- LINE Developers Console上の状態: `公開済み`

2026-06-24に、友達側で `Bad認証` になる原因としてLINEログインチャネルが `開発中` だったことを確認し、`公開済み` へ変更済みです。

## 最新LIFF画面

正本ファイル:

- `k-alert-test/worker/k_alert_dedicated_worker.js`
- SHA256: `BEE6B9F913E8AEE40FA4A3707C5F07248D8E1776E4CD744760B00116B2BB3912`
- ファイルサイズ: `10555` bytes
- ローカル更新日時: `2026-06-23 14:40:58`

画面タイトルとヘッダー:

- `Kアラート通報`

画面冒頭文:

- `通報の内容については、所属している勤務先に対して報告書を提出します。`
- `匿名希望の場合は名前入力は不要です。`

入力項目:

| 項目 | 必須 | payload key | 備考 |
|---|---:|---|---|
| 企業名 | 必須 | `companyName` | `autocomplete="organization"` |
| 名前 | 任意 | `reporterName` | 匿名希望なら空欄可 |
| いつの事ですか？ | 必須 | `when` | 例: `2026年6月23日` |
| どこで起きましたか？ | 必須 | `where` | 例: `職場の事務所で` |
| だれが起こした人ですか？ | 必須 | `who` | 例: `職場の先輩の田中さん` |
| だれに対してのことですか？ | 必須 | `toWhom` | 例: `後輩の山田君に` |
| なにをどのようにしていましたか | 必須 | `whatHow` | 例: `お金を貸してくれと強く迫っていました` |
| その他（自由記載） | 任意 | `freeText` | 空欄可 |
| 相談受付希望 | 必須 | `consultationRequest` | `希望する` / `希望しない` |

画面下部の注意文:

- `証拠保全のため、写真・スクリーンショット・録音などがあれば削除せず保管しておいてください。`

送信仕様:

- LIFF画面はWorkerの `/report` で表示する。
- 送信は同Workerの `/api/report` へ `POST` する。
- WorkerがGAS Webアプリへサーバー側転送する。
- 成功時の画面表示は `送信しました。ご報告ありがとうございます。`
- 成功後、LINEアプリ内なら約1.4秒後に `liff.closeWindow()` する。
- `報告番号` はユーザー画面に表示しない。

## 最新GASコード

正本ファイル:

- `k-alert-test/gas/Code.gs`
- SHA256: `C8AC3A096CC1069AC9360CFEC68E947C0AE2251E07B82F3466CA3F027040BB17`
- ファイルサイズ: `39584` bytes
- ローカル更新日時: `2026-06-23 15:39:33`

Apps Script反映状況:

- 2026-06-23に、ユーザーから最新版 `gas/Code.gs` をApps Scriptへ差し替え・デプロイ完了の報告あり。
- 2026-06-24に、GAS WebアプリURLへGET確認し、HTTP 200で `{"ok":true,"service":"k-alert-test","message":"KアラートGAS is running."}` が返ることを確認済み。

主な定数:

- `START_TRIGGER_TEXTS = ['相談する']`
- `REPORT_LINK_TRIGGER_TEXTS = ['通報する']`
- `DEVELOPMENT_TRIGGER_TEXTS = ['大人の保健室']`
- `CONSULT_START_POSTBACK = 'action=consult'`
- `CONSULT_END_POSTBACK = 'action=end_consult'`
- `INVESTIGATOR_CONSULT_POSTBACK = 'action=investigator_consult'`
- `REQUIRED_FIELDS = ['when', 'where', 'who', 'toWhom', 'what', 'how']`
- `LIFF_REPORT_SHEET_ID = 1527545544`
- `LIFF_REPORT_ALLOWED_CONSULTATION = ['希望する', '希望しない']`

GASの主な修正内容:

- LIFF報告payloadを `companyName`, `reporterName`, `when`, `where`, `who`, `toWhom`, `whatHow`, `freeText`, `consultationRequest` で受ける。
- LIFF報告フォーム用シートはGID `1527545544` を直接探す。
- 旧ヘッダー `入力１` / `入力２` / `入力３` を検知した場合、GAS側で列を追加し、5W1H式の列構成へ寄せる処理あり。
- `freeText` は任意。必須ではない。
- `consultationRequest` は `希望する` / `希望しない` のみ許可。
- `相談する` postbackで相談開始し、LINE入力キーボードを開くリッチメニューと連動する。
- 相談中は `相談を終了する` Quick Replyを表示する。
- AI相談フローは、機械的な不足項目確認ではなく、共感返信を挟んだあとで、匿名報告または調査官依頼を選ぶ流れ。
- 方針確認文はFlex内ではなく通常チャットとして送る。
- ユーザー返答を `匿名で会社に報告する` / `報告せずに調査官に依頼する` / `やはりやめた` に分類する。
- `報告せずに調査官に依頼する` 判定後は `調査官に依頼する` ボタンを出す。
- `調査官に依頼する` 押下後、LINE入力表示は `調査官への依頼\n※調査官が改めてチャットしますので、連絡をお待ちください`。
- 調査官依頼postback受信後は、その後の自動チャット返信を止める。
- 緊急時文言は、生命・身体・財産に対して急を要する場合は110番・119番を促す方針。

GAS Script Propertiesで必要な主なキー:

| キー | 用途 |
|---|---|
| `SPREADSHEET_ID` | Kアラート・テスト開発スプレッドシート |
| `LINE_CHANNEL_ACCESS_TOKEN` | KアラートMessaging APIの返信用 |
| `AI_PROVIDER` | `anthropic` または `openai` |
| `ANTHROPIC_API_KEY` | Anthropic使用時 |
| `ANTHROPIC_MODEL` | Anthropic使用時。テスト基本値は `claude-haiku-4-5` |
| `OPENAI_API_KEY` | OpenAIへ戻す場合 |
| `OPENAI_MODEL` | OpenAIへ戻す場合 |
| `K_ALERT_LIFF_URL` | `https://liff.line.me/2010343610-N2psO7GW` |
| `CHATWORK_API_TOKEN` | 第2段階用 |
| `CHATWORK_ROOM_ID` | 第2段階用 |

秘匿値はGitHub、Notion、チャットへ書かないでください。

## スプレッドシート設定

Spreadsheet:

- 名前: `Kアラート・テスト開発`
- Spreadsheet ID: `1c1VK_l7xSsT29WLPZiBBYRc5we-yHfGpJuYr24dMNWA`
- 管理URL: `https://docs.google.com/spreadsheets/d/1c1VK_l7xSsT29WLPZiBBYRc5we-yHfGpJuYr24dMNWA/edit?gid=0#gid=0`

### `アラート` シート

| 列 | 項目 | 用途 |
|---|---|---|
| A | No | GAS連番 |
| B | 初回コメント内容 | LINE相談の初回コメント原文 |
| C | いつの事ですか？ | AI/追加回答 |
| D | どこで起きましたか？ | AI/追加回答 |
| E | だれが起こした人ですか？ | AI/追加回答 |
| F | だれに対してのことですか？ | AI/追加回答 |
| G | なにをどのようにしていましたか | AI/追加回答 |
| H | 緊急度 | `高` / `中` / `低` |
| I | 対応コメント | 手動またはAI下書き |
| J | やり取り全文記録 | GASが時系列追記 |
| K | 備考 | エラー、判断根拠、状態 |

### LIFF報告フォーム用シート

- 対象シートGID: `1527545544`
- GAS定数: `LIFF_REPORT_SHEET_ID = 1527545544`

| 列 | 項目 | 必須 | 入力元 |
|---|---|---:|---|
| A | No | 自動 | GAS |
| B | 企業名 | 必須 | LIFF |
| C | 名前（任意） | 任意 | LIFF |
| D | いつの事ですか？ | 必須 | LIFF |
| E | どこで起きましたか？ | 必須 | LIFF |
| F | だれが起こした人ですか？ | 必須 | LIFF |
| G | だれに対してのことですか？ | 必須 | LIFF |
| H | なにをどのようにしていましたか | 必須 | LIFF |
| I | その他（自由記載） | 任意 | LIFF |
| J | 相談受付希望 | 必須 | LIFF |

注意:

- 2026-06-23の5W1H化ログでは一時的にA〜K列という表記があるが、2026-06-23後続修正と現行LIFF payloadでは `whatHow` を1項目として扱うため、LIFF報告フォーム用シートはA〜J列運用。
- LINE相談側のAI内部では `what` / `how` を分けるが、LIFFフォーム画面とLIFF報告シートでは `なにをどのようにしていましたか` に統合している。

## 最新リッチメニュー

LINE APIから2026-06-26に現在のデフォルトリッチメニューを読み戻し確認済み。

- 現在のデフォルトリッチメニューID: `richmenu-6357c4f92df07d8801645928a6a53af4`
- 名前: `K Alert Rich Menu 2026-06-23 share layout v2`
- 選択状態: `selected = true`
- サイズ: `2500 x 1686`
- エリア数: `3`
- 現在LINE APIからダウンロードした画像: `G:\マイドライブ\Codex保存\一時確認\k-alert-current-richmenu-richmenu-6357c4f92df07d8801645928a6a53af4.jpg`
- 作成時の保存画像: `G:\マイドライブ\Codex保存\画像\k-alert-richmenu-share-layout-v2_2500x1686.jpg`
- 直前バックアップ画像: `G:\マイドライブ\Codex保存\画像\k-alert-richmenu-backup-before-layout-v2-20260623.jpg`

エリア設定:

| 位置 | 範囲 | アクション |
|---|---|---|
| 上段左 | `x=0, y=220, width=1250, height=760` | `postback`, `data=action=consult`, `displayText=相談する`, `inputOption=openKeyboard` |
| 上段右 | `x=1250, y=220, width=1250, height=760` | `message`, `text=通報する` |
| 下段全幅 | `x=0, y=980, width=2500, height=706` | `uri`, LINEシェアURL |

シェアURL:

```text
https://line.me/R/share?text=K%E3%82%A2%E3%83%A9%E3%83%BC%E3%83%88%E5%85%AC%E5%BC%8FLINE%E3%81%AF%E3%81%93%E3%81%A1%E3%82%89%0Ahttps%3A%2F%2Fline.me%2FR%2Fti%2Fp%2F%40953upiqr
```

## このチャットで実施した修正

### 2026-06-24

- Cloudflare Worker `k-alert-test` を再デプロイ。
- デプロイ時に `--compatibility-date 2024-01-01` を明示。
- Worker Version ID: `f90b2a41-05ef-44b3-824a-bd3f13d15489`
- `https://k-alert-test.s-jinnouchi.workers.dev/report` がHTTP 200で応答することを確認。
- `https://liff.line.me/2010343610-N2psO7GW` が `/report` へリダイレクトすることを確認。
- GAS WebアプリURLがHTTP 200で応答することを確認。
- LINEログインチャネル `KアラートLIFF` を `開発中` から `公開済み` へ変更。
- `Bad認証` の原因候補だった外部ユーザー利用制限を解除。
- `k-alert-test/docs/work_log.md`, `docs/notion/projects.csv`, Notion `k-alert-test` 行を更新。

## 未確認・次に確認すること

- 友達側のLINEアプリからLIFF URLを開き、`Bad認証` が解消されていること。
- LIFFフォームから実送信し、対象シートA〜J列へ記録されること。
- 公式LINE実機で、上段左 `相談する`、上段右 `通報する`、下段 `シェアする` のタップ位置と動作。
- `相談する` の初回文、共感返信、匿名報告/調査官依頼の選択カード。
- `報告せずに調査官に依頼する` 判定後、`調査官に依頼する` ボタンが表示されること。
- `調査官に依頼する` 押下後、自動チャット返信が止まること。

## 本番実装で注意すること

- 古い `C:\Users\irodo\Documents\Kアラート・テスト開発` はロゴや出力物中心で、実装正本ではない。
- 古い `sjinnouchi-ux__workspace` チェックアウトには古いWorker/GASが残っている可能性がある。
- 本番実装で流用する場合は、必ずこの正本作業ツリーの `k-alert-test/gas/Code.gs` と `k-alert-test/worker/k_alert_dedicated_worker.js` を基準にする。
- 秘密情報は `C:\Users\irodo\.codex\.sandbox-secrets\global.env` または各サービスのSecret/Script Propertiesで管理し、MD/GitHub/Notionには書かない。
- LINEログインチャネルは一度 `公開済み` にすると `開発中` に戻せない。今回の `KアラートLIFF` は公開済み変更済み。
- LIFF表示だけならWorkerで確認できるが、最終判定はLINEアプリ内のLIFF実機確認とスプレッドシート記録確認が必要。
