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
