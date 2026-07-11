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

