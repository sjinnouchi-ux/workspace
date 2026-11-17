# Codex Desktop Startup

## Role

この文書は、Windowsの各Codex Desktopがプロジェクト作業を始める際のオンライン正本です。ローカルclone、Codexの過去タスク、メモリ、フォルダ名より先にGitHub `main` 上のこの文書と `PROJECTS.md` を確認します。

Canonical URLs:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/GIT_HANDOFF_PROTOCOL.md
```

Claude、Codex、Fable間のGit引き継ぎは、共通契約 [`GIT_HANDOFF_PROTOCOL.md`](../GIT_HANDOFF_PROTOCOL.md) に従います。

OpenAI references:

- https://learn.chatgpt.com/docs/personalize
- https://learn.chatgpt.com/docs/agent-configuration/agents-md

## Startup Order

1. GitHub `sjinnouchi-ux/workspace` の `main` を取得し、この文書、`PROJECTS.md`、[GitHub Actions・検証コストの共通方針](GITHUB_ACTIONS_POLICY.md)、[承認・本人操作・継続方針](AGENT_APPROVAL_POLICY.md)を読む。
2. 取得に使った `workspace` のcommit SHAを確認する。
3. ユーザーの表現を `PROJECTS.md` の `Alias` と照合し、Canonical Entryを確定する。
4. 対象Gitの既定ブランチを取得し、repoの `AGENTS.md` があれば最初に読む。
5. `PROJECTS.md` のPrimary Docsを読み、現在状態と作業範囲を確定する。
6. 必要な場合だけ、タスク専用のローカルclone/worktreeを作る。

URL取得、GitHub認証、対象プロジェクト特定のいずれかに失敗した場合は、同名ローカルフォルダや過去cloneを推測で使用しません。作業を停止し、不足している接続または登録を報告します。

## GitHub Access

- GitHub owner/account: `sjinnouchi-ux`
- `s.jinnouchi@yumekango.com` はGoogle業務用アカウントであり、GitHub owner名ではない。
- `workspace` は公開ルーターだが、個別のprivate repoには各PCでGitHub認証が必要。
- GitHub connectorが使える場合はconnectorを優先する。
- CLIが必要な場合は `gh auth status` でactive accountを確認し、`git fetch origin --prune` 後にremoteとlocalを比較する。

## Mobile-origin Browser Recovery

具体的な承認はスマホのチャットでも受けられる。既承認の範囲は引き継ぎ、使用ツールの規則が許す操作をCodexが完了する。OAuth同意を一律に本人PC操作としない。追加承認・本人操作が必要な場合の根拠と手順は[共通方針](AGENT_APPROVAL_POLICY.md)に従う。

スマホからの指示でブラウザを使う場合も、Codexが利用可能な通常のPC画面操作で復旧を進め、利用者にPC操作や再起動を繰り返し要求しない。

- `Local browser use is disabled in Work settings` だけで設定オフと断定しない。設定が有効でも、スマホから開始・再開したチャットのPC側初期化不足で同じ表示になる事例がある。
- まずブラウザ一覧・エラーと、必要に応じて設定画面を確認する。ブラウザ許可を変更せず、ネイティブアプリ操作が利用できる場合は、PCのChatGPT/Codex画面で**作業中の同じチャット**を開く。別チャットへの投稿、新規チャット作成、本人を装ったメッセージ送信はしない。
- 続いて `cua_repl` をリセットし、初回APIの規則に従ってブラウザ一覧を再取得する。対象ブラウザのページ表示・読取りまで確認してから復旧済みと報告する。
- これは既存の許可に従う通常の画面操作であり、ブラウザの安全停止を別経路で迂回してよいという意味ではない。許可、署名確認、環境変数、アプリ本体を改変しない。
- PC側で同じチャットを開けない、または再確認しても失敗する場合は結果を報告する。必要な場合だけ、そのチャットをPC側で開いて短い指示を送る操作を本人に依頼する。モデルの思考強度変更、設定の入切、再インストールを根拠なく勧めない。
- 別のスマホ起点チャットやアプリ再起動後には再発し得る。今回の復旧を全チャットの恒久修正と扱わない。
- GitHub正本確認後、`NUCBOX_K8_PLUS` のMemory MCPでは `development-environment` / `mobile-browser-initialization` を検索する。他PCでも同じ原因・修復結果だとは推測しない。

検証済み手順と限界: [development-environmentの復旧記録](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/reports/2026-10-30-mobile-browser-initialization.md)。関連する外部報告: [openai/codex #57721](https://github.com/openai/codex/issues/57721)（利用者による再現報告であり、修正版の提供を保証するものではない）。

## Connection And Authentication Boundaries

- Apps connector、local CLI/sync、local/host MCP、hosted plugin MCP、browser/profile、Remote/SSHを別の認証・実行境界として確認する。
- sandbox user、別host/profile、tool未露出、network制約で判定できない結果はINCONCLUSIVEとし、credential消失や未接続へ置き換えない。
- 別経路の失敗だけでlogout、disconnect、credential削除、OAuth/token再発行、認証JSONコピーを行わない。既存権限と使用toolの安全停止を維持する。
- 詳細は[接続・認証境界](connection-authentication-boundaries.md)。旧PR16の確認scriptを必須化せず、必要な確認は現在使用する正式経路で行う。

## Local Work Policy

- ローカルは作業場であり正本ではない。
- 既存cloneを使う場合も、remote URL、default branch、upstream、dirty stateを確認してから作業する。
- 読取りや文書更新をGitHub上で完結できる場合は、そのまま作業する。ローカルでの実装・検証が必要な場合にクローンやworktreeを作る。
- 新しく一時作業場を作る場合は、原則として1タスクにつき1フォルダとし、作成したパスを作業中に控える。複数repoのクローン、使い捨ての集計スクリプトや中間出力もその中に置く。既存の常設作業場・指定された成果物保存先は各プロジェクトの運用に従う。
- コード、判断記録、実装ログ、引き継ぎは対応するGitHub repoへcommit/pushする。
- ローカルだけに残るMarkdown、未push commit、未追跡成果物がある状態を完了と報告しない。
- live appを扱う場合は、repo state、設定/editor state、deployed/live stateを分けて報告する。

## Windows And PowerShell

- Codex Desktopのローカル作業はWindows + PowerShellを前提とする。
- 検索は `rg` / `rg --files` を優先する。
- 日本語Markdown、CSV、textは `Get-Content -Encoding UTF8` で読む。
- 文字化けした表示を根拠に編集せず、`Get-Content -Raw -Encoding UTF8` で正常表示を確認してから編集する。
- Windows PowerShell 5.1では、BOMなしUTF-8が必要なMarkdown、YAML、JSON、TOMLを `Set-Content`、`Out-File -Encoding utf8`、`>` で新規保存・全置換しない。`apply_patch` またはBOMなしUTF-8を明示できる方法を使い、既存の文字コードを保つ。
- 日本語を含む編集後はUTF-8指定で再読し、`git diff` で文字化けがないことを確認する。
- destructiveなfilesystem/Git操作は、対象と救出完了を確認してから実行する。

## Cleanup Gate

Codexが今回作成した一時作業場は、同じタスクの終了処理で整理する。整理前に以下のうち該当する保存先・作業内容を確認する。

- 必要な変更がcommit済み
- remoteへpush済み
- PRまたは既定ブランチへの反映状態を確認済み
- 必要な作業ログをGitHubへ反映済み
- 最終成果物をGitHubまたは指定Google Driveへ保存済み
- `git status` で必要な未追跡・未コミット情報がない
- deploymentや外部サービス作業がある場合はlive確認済み

条件を満たさない作業場は削除せず、救出対象として報告します。

Windowsで整理対象のタスク専用cloneをごみ箱へ移すときは、次の3段階をそれぞれ独立した操作として行う。

1. **移動前の読取り**：対象の絶対パスとGit rootを照合し、正規remoteに必要なcommitが保存済みで、ローカルだけの作業や他のworktreeからの利用がないことを確認する。ごみ箱にある同じ元パスの記録も確認しておく。
2. **移動**：通常のPowerShellで対象のroot・HEAD・cleanを再確認し、Windowsの `SendToRecycleBin` でcloneを1件ずつ1回だけ移す。GitHub照合やごみ箱の照会をこのコマンドに含めない。
3. **移動後の読取り**：元パスがなく、同じ元パスの新しい復元記録と復元用フォルダがあることを照合する。記録の反映待ちは読取りだけを再試行する。実行を拒否された場合は理由を記録し、[承認方針](AGENT_APPROVAL_POLICY.md)に従う。

複数クローンや補助ファイルをまとめたTEMP直下のタスク専用フォルダには、[作業場単位の整理手順](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/windows-temp-mixed-workspace-recycle.md)を使う。全項目の用途と必要な成果物の保存先を確認し、今回作成した親フォルダを対象とする。利用中・用途不明の項目があれば親を保持する。リンクされたGit worktreeは、管理元repoの登録を確認し、そのプロジェクトのworktree終了手順を使う。

終了報告の末尾に今回の整理結果を1行で記す。例は「作業場：作成なし」「作業場：1件をごみ箱に移動し確認済み」「作業場：1件保持（未保存の原本あり。保存先の確認待ち）」。複数の結果があれば件数を併記し、未確認の移動はその状態のまま伝える。

## Secrets And Accounts

- 秘密値、OAuthコード、token、認証JSON、`.env` の中身をチャット、Markdown、GitHubへ表示・保存しない。
- project repoのsecret管理文書とruntime設定を先に確認する。
- Secret Managerまたはruntime secret storeが正本と明記されたrepoでは、それを優先する。
- `C:\Users\irodo\.codex\.sandbox-secrets\global.env` は、repoが明示的に要求する場合だけローカル互換入力として使う。新PCへ一律コピーしない。
- Secret Manager移行済みと判定するには、`Secret ID + enabled version`、project/role manifest、service account IAM、helper経由のconsumer疎通の4点を確認する。
- Secret IDだけが存在し、manifest、IAM、consumer疎通のいずれかが欠ける場合は `stored_only` と扱う。`global.env` へ戻らず、作業を停止して不足層を報告する。
- Google業務操作は、ユーザーが別指定しない限り `s.jinnouchi@yumekango.com` を使う。

Cross-project audit:

```text
https://github.com/sjinnouchi-ux/mgmt-terminal/blob/main/docs/reports/2026-07-11-cross-project-secret-consumer-audit.md
```

## Documentation Contract

- 全体ルーティング: `workspace/PROJECTS.md`
- 共通Codex運用: `workspace/codex/`
- 開発環境、Memory MCP、Claude監査: `development-environment`
- コード、詳細設計、実装ログ: 各project repoのMarkdown
- 未登録プロジェクト: 推測で作らず、ユーザー確認
- 古いNotion CSV、日付別clone、Codexメモリは補助資料であり、現行ルーティングの正本にしない。

## Deliverable Storage

Yumekango のマイドライブでは、Codex・Claudeの案件成果物を `AIエージェント/<PROJECTS.md の Project 名>/` に保存する。継続案件に属さない単発の制作物は `AIエージェント/単発タスク/` に保存する。人が個人で管理する資料の置き場は同階層の `手動管理/`。業務アプリがID指定する既存フォルダ、原本の共有範囲、他組織の専用アカウントは案件の運用に従う。

Drive接続の業務アカウント、保存先の親と名前を照合し、保存後にファイルのID・親・リンクを読み戻す。同期ドライブ文字はPCごとに確認する。既存の共有資料は元の所有者・共有範囲を維持して参照する。Gitのコード・作業ログは各Canonical repoで管理する。

旧 `Codex保存` は2026-11-17にYumekangoの新規保存先として廃止した。既存資料は保管・復元用。[案件台帳](../PROJECTS.md)の現行案件と単発タスクには上記の新しい保存先を使う。

## Claude Report Intake

Claude Desktopの作業レポートは `マイドライブ/AIエージェント/開発環境/レポート/受信箱` に集まる。

- 受信箱の確認・統合は、ユーザーの明示指示または明示的なintakeタスクとしてのみ行う。通常タスクの開始時に自動確認しない。
- ローカル `G:` が見えない場合はGoogle Drive connector経由で確認し、単独の `Test-Path` 失敗を理由にintake以外の通常作業を停止しない。
- 処理開始時に対象ファイルを `処理中\<PC名>\` へ移動してclaimし、二重処理を防ぐ。移動できなかったファイルには手を出さない。
- 統合前に対象repoの既定branch、HEAD SHA、`AGENTS.md`、Primary Docsを読み、repo固有のbranch/PR・保存先規則を優先する。
- 統合完了（commit/push確認）までファイルを削除しない。処理後は処理済みへ移動し、`codex/work_log.md` にReport-IDとcommitを記録する。
- プロジェクトを特定できないレポートは保留へ移動し、ユーザーへ確認する。
- レポートに秘密値が含まれていた場合は統合を停止し、値を再掲せずに該当箇所を報告する。
- 詳細手順は `claude/REPORT_INTAKE.md` を正本とする。

## Reporting

- 確認済み事実だけを報告する。
- GitHub URL、branch、commit、PR、変更ファイルを可能な範囲で含める。
- GitHub反映前、PRのみ、`main`反映済み、deployment/live反映済みを区別する。
- 未完了または未同期の項目は、対象と理由を明示する。

## Development Environment

Codex Desktopを唯一のオーケストレーターとします。通常の設計、実装、テスト、GitHub反映、進行管理はCodex Desktop内で行い、外部の常設オーケストレーターへtaskを配送しません。

開発環境の正本はprivate repository `sjinnouchi-ux/development-environment` です。`AGENTS.md`、`docs/HANDOFF.md`、`docs/MIGRATION_MANIFEST.md` を確認してから、Memory MCPまたはClaude監査の設定を変更します。

### Windows-local Memory MCP

- `NUCBOX_K8_PLUS` のWindows Codex Desktopでは `development_memory` を補助知識として使用する。
- 必ずGitHub正本、Canonical Entry、既定ブランチ、repo `AGENTS.md`、Primary Docsを確認した後で、Canonical repo名とcomponent名に絞って検索する。
- 記録できるのは、原因が確認され、修正後の検証が通り、再利用価値がある `VerifiedFailurePattern` だけとする。
- host scope、repo/area、component、sanitized symptom、confirmed root cause、verified fix、GitHub commit/PR/test等のevidence reference、verification dateだけを保持する。
- 秘密値、OAuth code、token、credential、認証JSON、`.env`、生ログ、生pane、生queue、生report、例外全文、個人識別情報、不要な絶対path、環境変数値、会話全文は保存しない。
- 同じpatternは重複entityを作らず、後続の検証結果を追記する。GitHubと矛盾する場合はGitHubを優先する。
- `development_memory` が利用不能または該当0件でも、GitHub正本が利用できる限り通常作業を継続する。
- このメモリはこのWindows PCのローカル保存であり、ノートPCやWSL2と自動同期されると仮定しない。

### WSL2 Claude read-only audit

- Claude CLIはWSL2 Ubuntu内の既存OAuth認証を利用するが、Codex Desktopの常設オーケストレーターにはしない。
- ユーザーが監査を求めたときだけ、`development-environment` の固定runnerを使い、対象commit、spec/evidence path、監査質問を明示して一回実行する。
- Claude childはread-only toolsだけを使用し、変更、Git push、retry、fallback、別CLI起動を行わない。
- 監査結果は補助判断であり、GitHub正本とCodexの検証を置き換えない。
- 固定runnerの直前に、同じWSL2 Ubuntu環境で非推論の `claude auth status` を一回確認する。commandが非zero、responseが解釈不能、または `loggedIn=false` の場合は監査を起動せず、利用者へ一回限りの対話的な認証復旧が必要と報告する。認証復旧の承認は監査実行の承認を兼ねない。
- 呼出し側は結果分類まで固定receipt全体を保持し、`stdout_tail` と `stderr_tail` を先に捨てない。受入判断へ進めるのは `state=completed`、`exit_code=0`、かつnonempty `audit_text` の場合だけとし、その他をpassまたはfindings 0件として扱わない。診断tail全文は転載・保存せず、error categoryだけを要約する。
- runner返却後は、当該invocationのaudit-owned controller/Claude childと、effective temporary directory内の `codex-claude-audit-subject-*` だけをread-only確認する。広範なsweepや自動削除は行わず、WSL2 Ubuntu全体の停止は不要とし、Dockerや無関係なprocessを停止・削除しない。
- 詳細な実行・receipt・cleanup契約は `sjinnouchi-ux/development-environment` の [`docs/claude-audit.md`](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/claude-audit.md) を正本とする。

### Retired Shogun

旧Shogun runtime、WebUI、固定Ops、diagnostics、break-glass、Native Windows parallel Shogun、および旧GitHub repoは削除済みです。新規taskの配送、start、restart、repair、再配備、旧repoのCanonical Entry利用を行いません。移行・削除の記録は `development-environment` を正本とします。
