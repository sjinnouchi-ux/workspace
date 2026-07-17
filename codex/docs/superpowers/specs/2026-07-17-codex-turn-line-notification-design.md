# Codex Desktop ターン停止LINE通知 設計

- 日付: 2026-07-17
- 状態: ユーザー承認済み
- 設計正本: `sjinnouchi-ux/workspace`
- 関連実装repo: `sjinnouchi-ux/kakeibo-liff`
- 対象端末: `NUCBOX_K8_PLUS`
- 対象surface: Windows実ユーザー `jinnouchi` のCodex Desktop

## 1. 目的

Codex Desktopの主ターンが停止した時点で、既存の家計簿公式LINEへ短いPush通知を送る。タスクの成功・失敗・完了状態は判定せず、「ターンが止まった」ことだけを通知する。

## 2. 確定要件

1. Codexの `Stop` lifecycle hookを使う。
2. 主ターンだけを対象とし、`SubagentStop` は通知しない。
3. 既存のユーザー設定 `notify = ["codex-computer-use.exe", "turn-ended"]` は変更・上書きしない。
4. hookからローカルPythonを起動する。
5. 通知本文は端末名とJST終了時刻だけとし、タスク名は含めない。
6. 現在の `管理通知登録` 済み購読者を共用する。
7. LINE channel access tokenとLINE user IDは家計簿API境界から出さない。
8. 会話、プロンプト、transcript、作業パス、モデル名、秘密値を送信しない。
9. LINE通知の失敗でCodexのターン停止を妨げない。
10. 同じターンの通知は重複送信しない。
11. 初期版では再送キューと常駐processを作らない。

## 3. 非対象

- タスク完了、成功、失敗、blocked、承認待ちの意味判定
- Codexサイドバーのタスク名取得
- サブエージェント停止通知
- LINE APIのローカル直接呼出し
- LINE資格情報、service account JSON、OAuth tokenのローカル保存
- 既存の管理警告通知スケジュールまたは文面の変更
- Shogun、WSL2、tmux、Shogun WebUIの変更

## 4. 検討した方式

### 4.1 採用: Stop hook → Python → 家計簿API → LINE

LINE資格情報を家計簿APIに留めたまま、最短の経路で通知できる。Codex Desktop用の専用OIDC principalと専用受信endpointを追加する。

### 4.2 不採用: Stop hook → Python → 管理ターミナル → 家計簿API → LINE

既存の管理通知経路に近いが、単純なターン停止通知にAPI hopと障害点を追加する。

### 4.3 不採用: Python → LINE Messaging API

実装量は少ないが、LINE tokenをローカルで扱うため既存のsecret境界に反する。

## 5. アーキテクチャ

```text
Codex Desktop main turn
  → user-level Stop hook
  → local Python notifier
  → Google OIDC authenticated request
  → kakeibo-api dedicated internal endpoint
  → existing enabled management-notification subscribers
  → LINE Push API
  → user's official LINE chat
```

Codexの既存external notifierはデスクトップ内部の `turn-ended` 連携に使用中のため、その設定を通知経路として流用しない。新しい `Stop` hookを並存させる。

## 6. Codex hook

### 6.1 配置

- GitHub上のhook script正本は `workspace/codex/hooks/` に置く。
- インストール時にWindows実ユーザーの `~/.codex/hooks/` へ配置する。
- `~/.codex/hooks.json` が存在しない現在状態を前提に新規作成する。
- 将来ほかのhookが追加された場合は、既存定義を保持して `Stop` handlerだけを追加する。

### 6.2 イベント

`Stop` eventのJSONを標準入力から受け取る。使用する入力は次だけとする。

- `hook_event_name`
- `session_id`
- `turn_id`

`transcript_path`、`cwd`、`model`、`permission_mode` は読み取らず、ログや通知へ含めない。

### 6.3 実行

- Windows用の絶対コマンドを `commandWindows` で指定する。
- timeoutは10秒以下とする。
- handlerは標準出力へCodex制御JSONを返さず、正常時はexit 0とする。
- 通知処理の失敗時もCodexを継続させる。失敗情報は秘密を含まない最小限のローカル運用ログだけに記録する。

## 7. ローカルPython notifier

1. 標準入力を上限付きで読み、JSON objectと `hook_event_name == "Stop"` を検証する。
2. `session_id + ":" + turn_id` のSHA-256を `event_id` とし、raw IDを送信・保存しない。
3. `ended_at` をJSTのISO 8601で生成する。
4. host labelは固定の非秘密設定 `NUCBOX_K8_PLUS` を使用する。
5. 専用service accountのOIDC ID tokenを、鍵JSONなしの正しいWindows credential owner境界で取得する。
6. 家計簿APIへ5秒以下のtimeoutで1回だけPOSTする。
7. token、raw hook input、response body、session ID、turn IDはログへ残さない。
8. 初期版ではlocal outboxと自動再送を行わない。

実装前preflightで、surface、host、実行user、credential owner、OIDC token mint方法をread-only確認する。Codex隔離userでの失敗だけでは未接続と判断せず `INCONCLUSIVE` とし、実ユーザー境界で再確認する。service account JSONは作成しない。

## 8. 家計簿API contract

### 8.1 Endpoint

```text
POST /internal/codex/turn-ended/notify
Authorization: Bearer <Google OIDC ID token>
Content-Type: application/json
```

### 8.2 Request

```json
{
  "schema_version": 1,
  "event_id": "<64 lowercase hex>",
  "ended_at": "2026-07-17T14:32:00+09:00",
  "host_label": "NUCBOX_K8_PLUS"
}
```

未知fieldを拒否する。文字列長、日時形式、event ID形式を固定する。

### 8.3 Authentication

- 専用Codex Desktop notifier service accountだけを許可する。
- OIDC issuer、audience、email/subを検証する。
- 既存のLIFF・Webhook・公開routeを維持するため、`kakeibo-api` Cloud Run serviceの公開IAMとInvoker設定は変更しない。
- 新しいendpointだけをアプリケーション層のOIDC検証で保護し、匿名・誤audience・誤issuer・誤principalを拒否する。
- Windows実ユーザーには専用notifier service accountのID tokenをmintするための最小impersonation権限だけを付与する。
- 既存の管理ターミナル送信元service accountと認可設定を共有しない。
- LINE tokenをこのendpointのcallerへ返さない。

### 8.4 Delivery

- 既存 `_management_notification_subscribers` の有効購読者を共用する。
- Codex通知専用のdispatch sheetへ `event_id` と送信時刻だけを記録する。
- 同じ `event_id` は `deduplicated` としてPushしない。
- 購読者0件は `no_subscribers` として正常終了する。
- 既存の管理警告dispatch sheetとfingerprintの意味を混在させない。

## 9. LINE本文

本文は家計簿API側で生成し、callerが任意本文を渡せないようにする。

```text
Codexのターンが終了しました
端末: NUCBOX_K8_PLUS
時刻: 2026-07-17 14:32
```

端末名と時刻以外の動的情報は含めない。

## 10. エラー処理

- 不正OIDC: 401
- 許可外principal: 403
- 不正payloadまたは未知field: 422
- 重複event: 200 `deduplicated`
- 購読者なし: 200 `no_subscribers`
- LINE Push失敗: 家計簿APIは失敗を記録し、未送信eventを送信済みにしない
- ローカルnetwork/OIDC/API失敗: Pythonは秘密を除いたstatusだけを記録し、Codexを停止させない
- 初期版では自動再送しない

## 11. テスト

### 11.1 Python

- valid Stop inputから固定schema payloadを作る
- Stop以外を送らない
- raw session/turn IDがpayloadとlogへ出ない
- event IDが決定的である
- timeout、OIDC失敗、HTTP失敗でもCodex向けexitを阻害しない
- response bodyやtokenをlogへ出さない

### 11.2 家計簿API

- OIDCなし、誤audience、誤issuer、誤principalを拒否
- 正しいprincipalとpayloadを受理
- unknown fieldを拒否
- subscriber共用
- LINE messageの固定文面
- 同一eventの重複除外
- no subscribers
- LINE失敗時にdispatch未記録
- 既存管理警告通知とLINE reply pathの回帰テスト

### 11.3 Live

1. production deploy前に専用service account、実ユーザーのimpersonation権限、audienceをread-only確認し、`kakeibo-api` の公開IAMが変更されないことを確認する。
2. hookを無効のままendpointへ認証済みsmoke requestを送り、対象subscriberへの1件受信を確認する。
3. event ID再送で重複除外を確認する。
4. Windows実ユーザーのCodex Desktopへhookを追加する。
5. 専用テストターンを1回停止させ、LINE本文、端末名、JST時刻を確認する。
6. サブエージェント停止が通知されないことを確認する。
7. 既存のCodexデスクトップ通知と管理警告通知の非回帰を確認する。

## 12. Rolloutとrollback

### Rollout

1. kakeibo-liffにendpoint、service、testを実装する。
2. 専用service accountを作成し、Windows実ユーザーへID token mint用の最小impersonation権限だけを設定する。`kakeibo-api` の公開IAMとInvoker設定は変更しない。
3. 家計簿APIをdeployし、hookなしでlive検証する。
4. workspaceにPython hook scriptとWindows installerを実装する。
5. Windows実ユーザー境界でhook定義を追加し、1ターンだけE2E確認する。

### Rollback

1. `~/.codex/hooks.json` から追加した `Stop` handlerだけを除外する。
2. 既存 `notify` 設定と他hookは保持する。
3. 専用sender設定と実ユーザーのimpersonation権限を除外する。`kakeibo-api` の公開IAMとInvoker設定は変更しない。
4. endpoint codeとdispatch sheetは監査証跡として残し、LINE tokenや購読情報を移動しない。

## 13. 完了条件

- main turn停止ごとに1件だけ公式LINEへ届く
- 通知本文は端末名とJST時刻だけ
- subagent停止では届かない
- LINE token、LINE user ID、raw session/turn ID、会話内容がローカル・Git・ログへ出ない
- 同一turnの再実行は重複除外される
- 通知障害がCodex turn終了を妨げない
- 既存 `notify`、LINE reply、管理警告通知が変わらず動く
