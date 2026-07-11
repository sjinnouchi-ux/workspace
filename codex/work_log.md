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

