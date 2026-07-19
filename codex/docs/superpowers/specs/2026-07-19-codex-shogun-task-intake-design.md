# Codex経由Shogun task intake設計

- 日付: 2026-07-19
- 状態: ユーザー承認済み
- 設計正本: `sjinnouchi-ux/workspace`
- 対象surface: Codex DesktopからShogunへ依頼を配送する操作
- 対象外: Shogunコア、WebUI、WSL2設定、runtimeデータ、sessionの変更

## 1. 目的

当面のShogun操作をCodex経由に統一し、新しい依頼が前回の未完了taskや古いcommandを意図せず継続・再実行することを防ぐ。CodexはShogunへ依頼を送る前に操作可能性を確認し、依頼の意図を `new`、`resume`、`ambiguous` のいずれかへ分類する。

## 2. 採用方式

毎タスク取得される `codex/CODEX_DESKTOP_STARTUP.md` を詳細規則のオンライン正本とし、`codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` の貼付文面には、この規則をShogun操作時に必ず適用するbootstrapを置く。

この二層方式により、別PCでもGitHub `main` の最新版を取得すれば同じ規則を使用できる。Shogun repoだけへ規則を置く方式は、Codexが最初の依頼を配送する前の安全確認に間に合わないため採用しない。

## 3. 適用トリガー

ユーザーが「Shogunを使って」「Shogun経由で」「将軍へ依頼して」など、CodexからShogunを操作する意図を明示した場合に適用する。

この明示表現は、指定されたtask本文を既存の承認済みShogun task入力経路へ1回配送する権限だけを含む。Shogunのstart、stop、restart、repair、deployment、permission承認、未承認の新しい配送経路の作成は含まない。利用可能な承認済みtask入力経路を確定できない場合は送信せず、必要な入口または承認を報告する。

Shogunの設計相談や一般的な質問だけの場合は、runtimeへの指示配送を行わない。操作依頼か質問か判別できない場合は推測せず、ユーザーへ確認する。

## 4. 配送前ゲート

CodexはShogunへ指示を送る前に次を行う。

1. GitHub `main` のShogun read-only diagnostics deployment registryを検証する。
2. 許可された固定診断だけを実行し、provenanceとschemaを検証する。
3. 信頼済み診断の再計算結果が `overall=healthy` でない場合は送信せず、sanitizedな理由を報告する。
4. 生queue、pane、report、ログ本文を直接読まない。
5. 診断だけでは未完了taskの意味を確定できないため、task状態の確認はShogunへ送る標準intake指示の責務とする。

このゲートは既存の診断境界を拡張せず、start、stop、restart、repair、permission自動承認を許可しない。

本設計はtask本文の組み立てと配送判断だけを定め、新しいtransport、queue writer、WebUI機能を実装しない。配送には、その時点でGitHub正本に記載され、ユーザーの依頼範囲で使用を承認された既存入口だけを使用する。

## 5. 意図分類

### 5.1 新規依頼 `new`

継続を示す明示的な表現がないShogun操作依頼は新規と扱う。Codexは次の意味を持つ標準ガードを依頼本文の先頭へ付加する。

```text
この依頼は新規taskです。前回の未完了task、未配送command、未処理receiptの状態を先に確認し、sanitized summaryで報告してください。前回taskを自動継続・再実行せず、今回の依頼は新しいtaskと新しいcommand epochとして開始してください。前回作業と今回の依頼が衝突する場合は実行せず、衝突理由と選択肢を報告してください。
```

状態確認そのものを理由に前回taskを再開したり、古いcommandを再送したりしてはならない。

### 5.2 明示的な継続 `resume`

「前回の続きをして」「前回taskを再開して」など、継続が明示された場合だけ使用する。Codexは次の意味を持つ標準ガードを付加する。

```text
この依頼は前回taskの明示的な継続です。前回taskの現在状態と残作業を確認し、完了済み部分と終了済みcommandを再実行せず、残作業だけを継続してください。対象taskを一意に特定できない場合や状態が矛盾する場合は実行せず、sanitized summaryで確認を求めてください。
```

### 5.3 曖昧 `ambiguous`

「前と同じ」「さっきの件」など、新規か継続かを一意に決められない場合はShogunへ送信せず、Codexがユーザーへ確認する。既定値で継続扱いにしてはならない。

## 6. Shogun側の応答契約

標準intake指示は、Shogunへ次を要求する。

- 前回状態の報告はtask ID、状態、残作業、衝突有無を中心とするsanitized summaryに限定する。
- 秘密値、Inbox本文、pane内容、生queue、生report、生ログを返さない。
- 新規依頼は新しいtaskとcommand epochを使用する。
- terminalまたはdrop済みcommandを再実行しない。
- 前回taskと新規taskが同じファイルや外部資源で衝突する場合はfail-closedで停止する。
- 明示的な継続でも完了済み副作用を自動で繰り返さない。

## 7. 変更対象

- `codex/CODEX_DESKTOP_STARTUP.md`: 詳細なintake規則と標準ガード文を追加する。
- `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md`: 貼付文面へShogun操作時のオンライン規則適用を追加し、検証条件を更新する。
- `codex/work_log.md`: 変更目的、branch、検証、PR、deployment非対象を記録する。
- `codex/docs/superpowers/plans/2026-07-19-codex-shogun-task-intake.md`: 実装・検証・rollback計画を記録する。

Shogun repo、生成instruction、WebUI、runtime設定は変更しない。

## 8. 検証

文書検証で少なくとも次を確認する。

- startupとCustom Instructionsの両方にShogun intake規則への入口がある。
- `new`、`resume`、`ambiguous` の三経路が区別される。
- 新規依頼が前回taskを自動継続しない。
- 継続は明示的な場合だけ許可される。
- 曖昧な依頼は送信前に確認する。
- 診断失敗時にraw fallbackを許可しない。
- start、stop、restart、repair、permission自動承認を追加で許可しない。
- 生runtimeデータ、秘密値、実運用内容が差分にない。
- 既存Codex hookのunit testとinstaller testが回帰しない。

## 9. Rolloutとrollback

### Rollout

1. 専用branchで文書と検証を更新する。
2. 独立したdiff review後にdraft PRを作成する。
3. CIとレビュー完了後、ユーザー承認がある場合だけmainへmergeする。
4. 新しいCodexタスクはGitHub mainのstartupを取得して規則を適用する。

Custom Instructions貼付文面の変更はGitHub上の正本更新であり、各PCの設定画面への再貼付は別の明示操作とする。

### Rollback

対象PRをrevertし、startup、Custom Instructions、work logを直前のmainへ戻す。Shogun runtimeへ変更を加えないため、session停止、再起動、snapshot rollbackは行わない。

## 10. 完了条件

- CodexがShogun操作依頼を受けると、配送前診断と意図分類を行う。
- 新規依頼は前回taskを自動継続しない標準ガード付きで配送される。
- 明示的な継続依頼だけが前回taskの残作業を再開できる。
- 曖昧な依頼はShogunへ送信されない。
- GitHub mainに指示正本、作業記録、検証結果が残る。
- Shogunコア、WebUI、WSL2 runtime、本番sessionは変更されない。
