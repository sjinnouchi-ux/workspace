# AI経営実装度診断の撤去計画

**Goal:** 利用者の2026-10-18 JSTの明示依頼に従い、専用アプリ・Googleファイル・現役のGit記載を撤去する。

**Architecture:** GitHub connectorでmainの固定SHAから専用branchとdraft PRを作成し、Google側の撤去前に差分を公開する。共有workspace、Kアラート、労基診断、管理ターミナルの実行環境は維持する。

**Tech Stack:** GitHub Pages、GitHub Git Data API、Google Drive、Google Apps Script。

## 制約

- 起動時main: `45d2afa2e96f3098c97d54d9de368d9a32e0b1cb`。オンライン正本・AGENTS・Primary Docsを確認済み。
- 秘密値、OAuth情報、回答データ本文を取得・保存しない。
- Git履歴全体の書換えや共有repo削除は行わず、削除済み台帳と監査記録を残す。
- 新規local cloneは作らず、GitHub上のcommit・ref・PRを読み戻す。

## 実行

- [x] 専用17ファイル、Googleファイル8件、現行Git参照を特定。
- [ ] `ai-keiei-shindan/` 一式を削除、`PROJECTS.md`を撤去状態へ変更、旧入口棚卸しを訂正。
- [ ] 専用branchへcommitし、mainをbaseとするdraft PRのFiles changedを照合。
- [ ] 確認済み所有者の専用GAS、マスタ/回答Sheet、仕様・seed・起動指示・レビュー回答を削除。
- [ ] GitHub差分の対象範囲、他プロジェクト行とworkflowの不変を検証し、mainへ統合。
- [ ] 公開ページが診断を表示しないこと、旧GASが設定JSONを返さないこと、Google削除結果を確認。
- [ ] 管理ターミナルの関連4文書へ削除済み注記を反映。
- [ ] 作業ログに結果・未完範囲を確定し、remoteとPR状態を照合。

## 検証方針

アプリを撤去するため旧アプリの機能テストは実行しない。Git tree差分、台帳の行数・他行不変、削除対象17件、公開ページとGAS停止、Driveメタデータ再取得で確認する。管理ターミナルは文書のみのためアプリ/DB/Windows全体テストを起動しない。
