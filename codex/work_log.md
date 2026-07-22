# Codex 作業ログ

Codex専用フォルダ内の作業記録です。ワークスペース全体に関わる内容はルートの `claude_log.md` にも記録します。

---

## 2026-05-28｜Codex専用フォルダ作成

### 背景

- GAS等の操作オペレーションがClaude CoworkとCodexで異なる
- Codex専用の運用メモをGitHub上で管理したい
- GASは当面Codex内ブラウザを使ってコーディング・エラー確認・デプロイする方針になった

### 対応内容

- `codex/` フォルダを作成
- `codex/README.md` を作成
- `codex/gas_browser_operation.md` を作成
- `codex/work_log.md` を作成

### 残課題

- [ ] 最初のGASブラウザ操作タスクで手順を実地検証する
- [ ] `clasp` の `rapt_required` 解消可否を別途確認する

---

## 2026-05-28｜公式LINE AI連携の現状整理

### 背景

- 公式LINE、Cloudflare Worker、GAS、スプレッドシート、LIFF、market-pilotの関係をCodex側で把握したい
- 今後、公式LINEと安価なAI APIを連携し、不足項目確認、スプレッドシート記録、ChatWork通知までのテスト環境を作りたい
- 新規スプレッドシートは本番家計簿と分け、可能なら `yumekango.com` 側で管理したい

### 対応内容

- GitHub上の `yumekango-worker/` と `market-pilot/` の関連ファイルを確認
- ユーザー提供のGASコードから、家計簿LIFF、LINE Webhook、スプレッドシート保存、家計消化状況返信の流れを整理
- `codex/official_line_ai_integration.md` を作成
- 秘密情報、LINEトークン、認証値はMarkdownに記録しない方針を明記

### 残課題

- [x] AI連携の最初の対象業務を決める
- [x] テスト用スプレッドシートの列定義を決める
- [ ] ChatWork通知先ルームIDと通知文面を決める
- [ ] テスト用GASを `yumekango.com` 側で作成できるか確認する
- [ ] 既存Workerを分岐拡張するか、テスト用Workerを別名で作るか決める

---

## 2026-07-09｜Kアラート・テスト版の履歴整理

### 要点

- 過去にKアラートのテスト版が存在した。
- テスト版の詳細なGAS、Google Sheets、Worker、LIFF、LINE設定、作業ログはGit管理から削除する方針に変更した。
- 現行のKアラート開発・運用は本番開発リポジトリを正本とする。

---

## 2026-07-11｜全プロジェクト入口の棚卸し

### 対応内容

- GitHubアカウント `sjinnouchi-ux` の12リポジトリと `PROJECTS.md` を照合した。
- Windowsローカルで22個の成立したGitルート、3個の空 `.git`、31個のCodex trusted pathを確認した。
- 正式clone、タスク用clone、重複・退役候補、空の危険入口、未同期情報あり、Shogun対象外に分類した。
- 未同期Markdown、未統合commit、生成物が残る場所を特定し、削除禁止対象として記録した。
- Codexが各runで読む共通入口は `~/.codex/AGENTS.md` であり、repo側 `AGENTS.md` が追加適用されることを公式仕様で確認した。

### 成果物

- `codex/2026-07-11-project-entrypoint-inventory.md`

### 未実施

- ローカル固有情報のGitHubへの移送
- `PROJECTS.md` のURL・未登録repo修正
- グローバル `AGENTS.md` テンプレートの作成と各PCへの配布
- 空入口、重複clone、古いtrusted pathの削除

Shogun関連はユーザー指定により別デスクトップで扱うため変更していない。

---

## 2026-07-11｜オンライン正本への交通整理

### 対応内容

- `codex/CODEX_DESKTOP_STARTUP.md` を作成し、GitHub優先の起動順、認証停止条件、ローカル作業場、cleanup gateを定義した。
- `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` に、各PCのパーソナライズへ設定する共通bootstrap文面を記録した。
- `PROJECTS.md` を完全なGitHub URLとPrimary Docsを持つルーターへ再構成した。
- `mgmt-terminal`、`kango-mamori-studio-requests`、`supabase-db-templates` を台帳へ追加した。
- Shogunを `multi-agent-shogun` へ正しく接続し、WSL2 Linux + WebUI、後日同一GitHub運用へ改修する方針を記録した。
- stale workspaceにだけ残っていた2026-06-16のdori-manga確認ログを正本へ救出した。

### 非対象

- Shogun実装、WSL2設定、WebUI設定
- ローカルフォルダやcloneの削除
- 未確認の生成物をGitHubへ追加すること

### GitHub反映結果

- `workspace` PR #4をsquash mergeし、`main` の `e976f29352eaf08f996c1182e7509233e11ed99f` へ反映した。
- `taiwan-outreach` PR #1をsquash mergeし、2026-07-05の確認済み作業ログを `main` の `dc02db8cd879f7e4f7dba96dc9ffc42d1e9d489d` へ救出した。
- `kango-mamori-studio-requests` PR #2をsquash mergeし、確認済みSTUDIO構成メモとrepo入口を `main` の `44c676065d37a2e95493ae22275544ef50e309bf` へ救出した。
- `PROJECTS.md` のPrimary Docsと共通起動文書の参照先が解決できること、および3つのraw URLがHTTP 200を返すことを確認した。

### このPCへの反映

- `C:\Users\irodo\.codex\AGENTS.md` をオンライン起点bootstrapへ切り替えた。SHA-256は `857A8E578855333DDF5C27CD27B085BBBFAD16AD4D6379DA25AAB106E2ED4F02`。
- 変更前ファイルは `C:\Users\irodo\.codex\backups\AGENTS-before-online-bootstrap-20260711-1738.md` に保存した。SHA-256は `75E789917863183CE856976FC0C0E08E5193D24FB76E64130686094CAE43234A`。
- 安定clone `C:\Users\irodo\Documents\workspace` を更新後の `origin/main` へfast-forwardした。
- 今回作成した `C:\Users\irodo\Documents\Codex\2026-07-11\traffic-control` は、内容がGitHubへ反映済みで作業ツリーがcleanであることを確認して削除した。

### 明示承認まで保留

- 既存の空Git入口、空 `.git`、重複clone、古いtrusted pathは削除していない。
- `kakeibo-liff` と `k-alert-production-workspace-push` の未統合branchは保存した。
- `Kアラート・テスト開発` と `台湾プロジェクト` の生成物は未確認のまま保持し、GitHubへ追加していない。
- Shogun実装、WSL2、WebUIは変更していない。

---

## 2026-07-11｜Shogun GitHub境界連携方式の確定

### 決定

- Shogunの最終方式を `GitHub境界連携方式`、設計書を `2026-07-11-shogun-cross-pc-operating-plan-v1.1.md`、状態を `1.1 lightweight approved` とした。
- 設計書のSHA-256 `D63EC4684978DBCA11CEC477B2C540F1C1A1E8BE4273ED3644B0CD1F94BA7A82` をGoogle Drive上の実体と照合した。
- ShogunはCodex Desktopと設定、認証、session、worktree/cleanup方式、Drive領域を共有せず、GitHubのcommit、branch、PRと必要な成果物だけを境界として連携する。
- 以前の「ShogunをCodex Desktopと同じcleanup規則へ適合させる」案はv1.1によりsupersededとした。

### Codex側の反映範囲

- 共通起動手順、パーソナライズ用bootstrap、`PROJECTS.md` のShogun説明だけを境界方式へ更新する。
- Codex Desktopのonline-first、task用clone/worktree、cleanup gate、secret、Google Drive保存規則は変更しない。
- 対象projectのAGENTS、Shogun本体、WSL2、WebUIは変更しない。

---

## 2026-07-11｜全project secret consumer監査

### 確認結果

- `PROJECTS.md` の全15プロジェクト行、実Git入口14件をGitHub既定branchから監査した。
- 旧 `global.env` の値あり41項目に対応するSecret IDは41件すべて存在し、全件に有効versionがあることを確認した。
- `codex-agent` が参照できるのは管理ターミナル用2件だけで、残る39件は保管のみ完了、manifest/IAM/consumer切替が未完了だった。
- dori-mangaの新PC障害は、本番停止ではなくCloudflare deploy credentialの供給経路不足と確定した。
- API Monitor、議事録システム、Kakeibo、Market PilotにもPC間移行上の残件がある。

### 反映

- 共通起動手順へSecret Manager移行完了の4条件を追加した。
- `PROJECTS.md` の影響projectへ現在の停止条件を追記した。
- dori-mangaのsecret文書と作業ログへ、保管済み・利用未整備の境界を追記した。
- privateの詳細監査正本は `mgmt-terminal/docs/reports/2026-07-11-cross-project-secret-consumer-audit.md` とした。

### 非変更

- Secret値、Secret version、IAM、`global.env`、runtime、Shogun/WSL2/WebUIは変更していない。

---

## 2026-07-11｜API Monitor Secret Manager consumer移行

- Canonical repo `sjinnouchi-ux/api-monitor` にruntime/sync roleのSecret Manager起動経路を追加した。
- 管理ターミナルに `api-monitor.runtime` / `api-monitor.sync` manifestを追加し、対象5 Secretだけへ限定IAMを設定した。
- runtimeとAdmin資格情報の相互非混入、および5 provider endpointのHTTP 200を確認した。
- API Monitorの `global.env` 読込、`.env` 自動生成、SQLite平文キー保存、画面のキー登録・表示・コピーを廃止した。
- 新PCでの基本起動は可能。Google Billing同期は非秘密のproject / dataset / table設定と各PCのADC確認が残る。
- Shogunの設定・認証・session・Drive領域には変更を加えていない。

---

## 2026-07-11｜dori-manga新PC secret consumer実装

### 実装

- `mgmt-terminal` の中央helperへ `dori-manga.deploy` manifestを追加した。
- `codex-agent` にはCloudflare 2 Secretだけのaccessorを付与した。
- `workspace` へ新PC用Cloudflare Pages deploy runbookを追加した。
- helperの明示的引数転送不具合を修正し、回帰テストを追加した。

### 検証

- manifest検査とhelper引数転送テスト: pass。
- service account impersonationと子プロセス限定注入: pass。
- 別のactive gcloud accountを設定した親processからも、manifest指定アカウントでSecret取得: pass。
- `dori-manga-admin` Pages project読取: pass、production branch `main`。
- 一時preview deployとHTTP 200: pass。検証後にdeploymentを削除し、削除後HTTP 404を確認。
- productionはHTTP 200のまま。
- Secret値、Secret version、Pages配信内容、Shogunは変更していない。

### 現在地

- 新PCからの取得経路は利用可能。
- Cloudflare専用Pages Edit tokenへのrotationまでは `ready_with_rotation_pending`。
- コード変更がないためproduction deployは未実施。

---


## 2026-07-11｜議事録システム Secret Manager consumer移行

- `meeting-minutes.runtime` manifestからOpenAI資格情報1件だけを子processへ渡す構成へ変更した。
- `data/settings.json` のAPIキー平文保存、保存API、password入力、保存UIを撤去した。
- 旧JSONにキーが残る場合は初回読込で値を表示せず除去する。
- Google OAuth client JSONとtokenはSecret Managerへ入れず、各PCで `s.jinnouchi@yumekango.com` として再認証する。
- 既存の限定IAMを再利用したため、新規IAM付与はなく、`codex-agent` のアクセス可能数は9 / 41のまま。
- Shogunの設定・認証・session・Drive領域には変更を加えていない。

## 2026-07-11｜Kakeibo Cloudflare deploy consumer移行

- `kakeibo.deploy` manifestからCloudflare tokenとaccount IDだけを子processへ渡す構成へ変更した。
- Doriで設定済みの限定IAMを再利用し、新規IAM付与は行っていない。
- repo固有 `AGENTS.md`、secret運用文書、production確認付きdeploy wrapperを追加した。
- `yumekango` Workerのreadと一時Worker write/delete、Cloud Run 4 secret参照、live HTTP 200を確認した。
- production Worker、Cloud Run、route flag、GAS、LINE、Spreadsheet、Shogunは変更していない。
- `codex-agent` のアクセス可能数は9 / 41のまま。共有Cloudflare tokenの用途別rotationが残る。

## 2026-07-11｜Kアラート Cloudflare deploy consumer整備

- Kアラート専用Cloudflare accountとDori/Kakeibo用accountを分離した。
- 共通Cloudflare tokenはKアラートWorkerへHTTP 403であり、流用不可と確認した。
- `k-alert.deploy` manifest、限定IAM、確認付きdeploy wrapper、非秘密疎通checkerを整備した。
- 専用scoped API tokenの発行・Secret Manager version登録までは `blocked_pending_token` とし、`global.env` やWrangler OAuthへ戻さない。
- 本番Worker、Cloud Run、LINE、Supabase、GAS、Shogunは変更していない。

### 完了追記

- Kアラート専用Account API tokenをWorkers Scripts Writeだけで発行し、Secret Managerへ直接登録した。
- helper経由のproduction read 200、一時Worker write/delete 200、削除後404を確認した。
- 誤ってAccount IDを登録したversion 1は無効化し、正しいversion 2だけを有効にした。
- 新PC用Cloudflare deploy consumerを `ready` とした。本番deployは実施していない。

---

## 2026-07-12｜Shogun runtime誤判定防止

- `NUCBOX_K8_PLUS` のCodex隔離ユーザーでは、実ユーザー単位のWSL登録が見えず、`wsl.exe --list` が空になることを確認した。
- 共通起動手順へ、隔離環境の空結果だけでWSL/Shogun未導入と判定しない規則を追加した。
- メインホスト、使用ディストリビューション、repo入口、tmux session、WebUI入口を明記した。
- 別PCにローカル実体がない場合も、Shogun全体の未導入・消失とは判定しない境界を追加した。
- Codex Desktop用の共通カスタム指示文面を同じ規則へ更新した。
- このPCのグローバル `~/.codex/AGENTS.md` へ同内容を適用し、ファイル一致を確認した。
- Shogun本体、tmux session、WebUI、認証、秘密設定には変更を加えていない。

## 2026-07-14｜Shogun読み取り専用診断ゲートの有効化

- Source PR: https://github.com/sjinnouchi-ux/multi-agent-shogun/pull/11 (`2e386673877d1181eec0f0589069cf24a3445c6a`)
- Deployment record PR: https://github.com/sjinnouchi-ux/multi-agent-shogun/pull/13 (`45b249edc03976a661d3b51dc516f3df3ea6d639`)
- Deployment: source/deployed SHA-256一致、mode `0555`、schema version 1
- Verification: deployment-host `make test-no-skip` exit 0、test count > 0、skip 0
- Policy: 固定command、実行直前のGitHub active record照合、raw fallback禁止だけを限定例外化
- Non-changes: Shogun watcher/queue/launcher/WebUI/runtime schema、credentials、raw runtime state

## 2026-07-17｜Shogun読み取り専用診断provenance URL修復

- Root cause: Codex共通指示がdeployment registryをrepository未指定の相対pathで記載し、`sjinnouchi-ux/workspace` 配下として解釈すると404になった。
- Canonical registry: `sjinnouchi-ux/multi-agent-shogun` `main` の `docs/superpowers/plans/2026-07-14-codex-readonly-diagnostics-work-log.md`。
- Repair: 共通カスタム指示と起動手順を、上記registryの完全なraw GitHub URLへ変更した。
- Non-changes: registryをworkspaceへ複製せず、Shogun runtime、watcher、queue、launcher、WebUI、credentials、snapshot内容、生runtime stateは変更・直接参照していない。

---

## 2026-07-17｜Codex Desktopターン停止LINE通知 設計承認

### 確定内容

- Windows実ユーザー `jinnouchi` のCodex Desktopで、主ターンの `Stop` hookからローカルPythonを起動する。
- タスク完了判定は行わず、ターン停止ごとに公式LINEへ通知する。
- 通知本文は端末 `NUCBOX_K8_PLUS` とJST時刻だけとし、タスク名、会話、プロンプト、パス、モデル名を含めない。
- 既存の `notify = ["codex-computer-use.exe", "turn-ended"]` は上書きせず、`Stop` hookを並存させる。
- 家計簿APIがLINE Pushを担い、既存の管理通知購読者を共用する。
- LINE tokenとLINE user IDは家計簿API境界から出さず、ローカルPythonは専用OIDC principalで認証する。
- 初期版は再送キューを持たず、通知失敗でCodexを停止させない。

### 設計書

- `codex/docs/superpowers/specs/2026-07-17-codex-turn-line-notification-design.md`

### 未実施

- Python hook script、installer、`hooks.json` の変更
- kakeibo-liff endpoint実装・deploy
- service account、IAM、OIDC設定
- LINE実通知

### 2026-07-17 設計修正

- 実装計画化の際、公開LIFF・Webhookと同一の `kakeibo-api` serviceへ専用principal限定のCloud Run Invokerを要求すると既存公開routeへ干渉する矛盾を検出した。
- ユーザー承認により、既存Cloud Run公開IAMとInvoker設定は変更せず、新規endpoint内の厳密なOIDC検証で保護する方針へ修正した。
- Windows実ユーザーへ付与するIAMは、専用notifier service accountのID token mintに必要な最小impersonation権限だけとする。

### 2026-07-17 実装計画

- 公開 `kakeibo-api` のOIDC endpoint・identity・deploy・live検証をサーバー計画へ分離した。
- Windows実ユーザーのStop hook・Python notifier・安全なinstaller・E2Eをクライアント計画へ分離した。
- serverを先にcode review・merge・live検証し、その後だけclient hookを有効化する。
- 両計画にTDD、明示承認checkpoint、既存公開route/notify非回帰、rollbackを含めた。

## 2026-07-18｜Codexターン停止LINE通知 server preflight

- `kakeibo-liff` PR #6をmainへmergeし、merge commit `42b49b697c01320af8df4336706e9e4d3244304a` 上で54 testsを確認した。
- Windows実ユーザー境界はhost `NUCBOX_K8_PLUS`、user `jinnouchi`、active Google account `s.jinnouchi@yumekango.com` と確認した。
- live Cloud Run serviceは `kakeibo-api`、revision `kakeibo-api-00012-pf9`、runtime SA `kakeibo-api-sa@kakeibo-liff-prod.iam.gserviceaccount.com`。
- live serviceは `run.googleapis.com/invoker-iam-disabled=true` で公開され、`allUsers` の Run Invoker bindingはない。registered URLは2形式あり、既存 `CLOUD_RUN_SERVICE_URL` は `https://kakeibo-api-570965759130.asia-northeast1.run.app` のまま。
- pre-deploy IAM policy SHA-256は `200537b0ea74223f06f6b7f7310f0e0390c0bc900d190a320b6ead33605682a1`。
- notifier service accountは未作成。有効管理通知購読者はGoogle Sheets connector境界で1名と再確認した（LINE user IDは読み上げ・記録していない）。
- Google Cloud公式の推奨公開方式とlive stateに合わせ、server planのdeploy flagを `--allow-unauthenticated` から `--no-invoker-iam-check` へ補正した。
- service account作成、IAM付与、Cloud Run deploy、live API request、LINE Push、Windows hook installは未実施で、明示承認checkpoint待ち。

## 2026-07-18｜Codexターン停止LINE通知 server本番反映

- 利用者の明示承認後、専用keyless notifier service accountを作成し、業務Googleアカウントへservice-account-levelの `roles/iam.serviceAccountTokenCreator` だけを付与した。user-managed keyは0件である。
- `kakeibo-liff` merged main commit `42b49b697c01320af8df4336706e9e4d3244304a` をCloud Run revision `kakeibo-api-00013-tg5` へdeployし、100% trafficで稼働している。
- 既存のpublic mode、service IAM hash、runtime service account、4件のSecret Manager参照、Worker、LIFF、webhook、GAS、route flagsは変更していない。
- 認証付きsmokeは1回目 `sent`、同一eventの2回目 `deduplicated`。有効購読者1名に対し、利用者が公式LINEへの1件受信を確認した。
- health、直接/Worker LIFF・categories、categories完全一致、未署名webhook拒否、未認証内部API拒否、54件のrepository testを確認した。
- 本番記録は `kakeibo-liff` PR #7でreview後にmergeされ、main commitは `f7d47edbd6a905796440890c6bd96c58dbbbe296`。rollback targetは `kakeibo-api-00012-pf9` で、成功したためrollbackは実行していない。
- server側は完了。Windows Codex `Stop` hookの実装・install・E2Eはclient計画の別checkpointとして未実施である。

## 2026-07-18｜Codexターン停止LINE通知 client実装・文書化

- `workspace` mainのbase commit `beb30f5d343a5d80c37d73dee20734a87cb31d1e` からtask branchを作成した。
- Python notifierとunit testをcommit `b5fd780` (`feat(codex): add fail-open turn notifier`) で実装した。
- idempotent PowerShell installerとisolated installer testをcommit `1434fad` (`feat(codex): install turn notification hook safely`) で実装した。
- Python unit testは19件成功した。installer testは10件成功し、同じsuiteを2回実行して両方成功した。
- installerの `DryRun`、`Apply`、`Remove`、trust review、diagnostics、rollback、privacy、fail-openの運用手順を `codex/hooks/README.md` に記録した。
- `Stop` だけを対象とし、既存 `notify = ["codex-computer-use.exe", "turn-ended"]`、他hook、`config.toml` を保持する。`SubagentStop` は追加しない。
- 実Windows userの `~/.codex` へのinstall、Codex Desktopのrestart/trust操作、live API call、LINE E2Eは未実施であり、別の明示承認checkpoint待ちである。
- 独立reviewで、Codex command-hook schemaの必須 `command` 欠落と、このhostで `Get-Command gcloud` がPythonから直接起動できない `gcloud.ps1` を返す問題を検出した。必須 `command` と `commandWindows` を同一内容で設定し、`gcloud.cmd` だけを選択するよう修正し、実 `.cmd` wrapper起動testと `.ps1` 拒否testを追加した。

### 2026-07-18 client read-only preflight / DryRun

- 正しい境界をhost `NUCBOX_K8_PLUS`、Windows user `jinnouchi`、active Google account `s.jinnouchi@yumekango.com` と再確認した。
- PATH上に実体Python 3.13と実行不能なWindows Store aliasが併存していたため、WindowsApps aliasを除外して実体 `python.exe` を選択し、実行と `Asia/Tokyo` zoneinfoを確認した。gcloudはPythonから直接起動できる `gcloud.cmd` を選択した。
- 実ユーザーの `hooks.json` は存在せず、既存 `config.toml` のnotifyは `codex-computer-use.exe` / `turn-ended` のままである。`SubagentStop` handlerは0件だった。
- installer `DryRun` はhooks change / notifier installの両方をrequiredと報告した。既存config fileのhashは前後一致し、書き込みは行われていない。
- ID token発行、live API call、`Apply`、Codex Desktop restart/trust、LINE E2Eは未実施で、明示承認待ちである。

## 2026-07-18｜Codexターン停止LINE通知 timeout修正

- Codex CLIの1ターンで `hook: Stop Failed` を再現し、notifierログが更新されないことを確認した。
- notifier単独実行は8.41秒で終了したが、HTTP側は5秒で `TimeoutError` となった。同じリクエストをCloud Run request logで確認すると `HTTP 200`、latency `6.415641219s` だった。
- 根本原因は、正常な本番応答より短いHTTP timeout 5秒と、token取得・HTTP・Windows process起動を含めるには余裕のないhook timeout 10秒だった。
- 公開LIFF、Webhook、Cloud Run IAM、server deploymentは変更せず、token timeout 5秒を維持し、HTTP timeoutを15秒、hook timeoutを30秒へ補正する。
- Python unit testのHTTP期待値とPowerShell installer testのhandler期待値を先に変更し、実値5秒/10秒でREDを確認してから実装した。修正後はPython 19件、installer 10件が成功した。
- notifierのhashが変わるため、mainへmerge後にcanonical installerで再Applyし、`/hooks` でexact hookだけを再承認してからDesktop E2Eを行う。
- timeout修正PR #26をmain `532930495d98fea014a8140cc06189ed7a3bc9c6` へmerge後、実ユーザーへのApplyで既存notifier置換が `File.Replace(..., $null)` のillegal-pathとなる追加不具合を検出した。旧handler timeout 10と旧notifierは保持され、installer一時file残留は0件だった。
- stale notifierを再現するinstaller testを追加してREDを確認し、同directoryの実replacement-backup pathを `File.Replace` へ渡してfinallyで削除するよう補正した。修正後はinstaller 11件を2回、Python 19件を1回実行し、すべて成功した。

## 2026-07-18 — Codexターン停止LINE通知 timeout再補正

- `/hooks` でexact Stop hookを信頼し、`Stop 1 / Active 1` を確認した。
- CLI実機テストは `Stop hook (failed)` を表示し、ローカル最小ログに `TimeoutError` を記録した。
- 登録済みhookコマンドを同じcredential owner境界で直接実行し、exit 0、18.481秒、HTTP側 `TimeoutError` を確認した。秘密値、raw hook JSON、token、response bodyは出力していない。
- 公開LIFF、Webhook、Cloud Run設定を変更せず、token timeout 5秒を維持し、HTTP timeoutを30秒、hook timeoutを45秒へ再補正した。
- 期待値を先に変更してREDを確認後、Python 19件とinstaller 11件がすべて成功した。

## 2026-07-18 — Codex Stop hook PowerShell起動補正

- timeout 45秒版をApply・個別信頼・CLI再起動後も `Stop hook (failed)` / code 1を再現し、notifier最小ログが更新されないことを確認した。
- OpenAI公式Codex sourceを確認し、hook runnerが実行環境のshellを継承し、PowerShellでは `powershell -NoProfile -Command <handler.command>` を使うことを確認した。
- 現行のquoted executableから始まるcommandはPowerShell再現で315ms・exit 1、同じcommandの `cmd.exe /C` 再現は7.188秒・exit 0・`status=sent` だった。
- Windows overrideだけをPowerShell call operator付きの `& <base command>` とし、portable base `command` は保持した。期待値を先に変えてRED確認後、Python 19件とinstaller 11件が成功した。
- PowerShell対応PR #29をmain `760f5a0785dff0c9974af28aa492be44ec341139` へmergeし、canonical installerでhandlerだけを再Applyした。`commandWindows == '& ' + command`、timeout 45、notifier hash一致、`SubagentStop` 0件、既存Desktop notify保持を確認した。
- `/hooks` で変更済みexact Stop hookだけを信頼し、CLIを再起動した。最終主ターンは新しいhook失敗表示なしで完了し、最小ログへ `2026-07-18T18:40:57+09:00 status=sent` を記録した。ユーザーが公式LINEでの受信を確認した。

## 2026-07-19 — Codex経由Shogun task intake

- `workspace` main `c82796a06de3d3786f6d7d7493c3c1997fd9db20` からbranch `agent/codex-shogun-task-intake` を作成した。
- 毎task取得されるstartupへversioned `CODEX_SHOGUN_TASK_INTAKE_V1` contractを追加し、Custom Instructions正本から適用する二層構成とした。
- 明示的な継続がない依頼は新規taskとして前回taskを自動継続せず、明示継続だけを再開し、曖昧な依頼は配送前にユーザーへ確認する。
- Shogun task配送の権限をstart、stop、restart、repair、deployment、permission承認へ拡張しない。
- 文書contract test 7件、既存Python hook test 19件、PowerShell installer test 11件が成功し、失敗0、SKIP 0だった。
- 独立再レビューで `new` と `ambiguous` の定義重複を1件検出し、失敗testを追加してから `ambiguous`、`resume`、`new` の優先順を相互排他的に修正した。修正後の再レビューに未解決findingはない。
- Shogun repo、WebUI、WSL2 runtime、tmux session、各PCのCustom Instructions設定は変更していない。
- draft PR #32を作成した。GitHub status checkは未設定で、mainへのmergeと各PCへの設定反映は行っていない。

## 2026-07-22 — API Monitorの管理ターミナル統合ルーティング

- `workspace` main `528813861087063c02542758decd5c3e0f5cd1f4` の起動手順と台帳から、独立 `api-monitor` と `mgmt-terminal` のCanonical Entryを確認した。
- `APIモニター`、`api-monitor`、今回使われた `管理モニター` のAliasを、現役入口 `sjinnouchi-ux/mgmt-terminal` へ移した。
- 管理ターミナルのPrimary DocsへAPI provider同期設計と2026-07-22統合クローズアウトを追加した。
- 独立 `sjinnouchi-ux/api-monitor` は「API Monitor（独立版）」として凍結・参照へ移し、旧Windows Streamlit、SQLite、provider同期実装、移行履歴の参照用とした。
- 旧repoのコード、SQLite、Secret Manager値、IAM、provider keyは削除・変更していない。GitHub repo archiveとlegacy secret/IAM cleanupは別承認とした。

## 2026-07-22 — Windows UTF-8文字化けの最小ガード

- `CODEX_DESKTOP_STARTUP.md` のWindows共通手順へ、文字化け表示を根拠に編集しないこと、UTF-8を明示して再読すること、編集後にUTF-8再読と`git diff`確認を行うことを追加した。
- Windows PowerShell 5.1では、BOMなしUTF-8が必要なMarkdown、YAML、JSON、TOMLを `Set-Content`、`Out-File -Encoding utf8`、`>` で新規保存・全置換しないルールを追加した。
- 専用スキルや常時読込ファイルは追加していない。Shogun側は独立repoの `AGENTS.md` / `CLAUDE.md` に同等の最小ルールを追加し、runtime・tmux・テスト運転は変更・実行していない。
