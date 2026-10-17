# AI経営実装度診断の削除記録

確認日: 2026-10-18 JST。状態: **Deleted / 公開停止確認済み**。

## 対象と許可

利用者がAI経営実装度診断アプリ、対象スプレッドシート、Git記載の削除を明示依頼。正本は `sjinnouchi-ux/workspace` の旧 `ai-keiei-shindan/`。Kアラート本体と経営者労基診断は別対象。

## 完了結果

| 対象 | 結果・証跡 |
| --- | --- |
| 専用アプリ17ファイル | HTML、GAS、seed、tests、仕様・実装ログ・起動ルールをmainから削除。[PR #69](https://github.com/sjinnouchi-ux/workspace/pull/69)、merge `002390621dc04fefe93b4f18cc98efc07d044a3a` |
| 公開診断ページ | `https://sjinnouchi-ux.github.io/workspace/ai-keiei-shindan/` はHTTP 404。ブラウザでもFile not found表示 |
| 旧GAS公開API | 既存 `/exec?action=config` はHTTP 404。ブラウザで「リクエストされたファイルは存在しません」を確認。設定JSONを返さない |
| 専用Googleファイル | 下記8件を削除。全件で削除API成功、その後の認証済みmetadata読戻しが404 / NOT_FOUND |
| workspace台帳 | 現役行から除外し、Deleted行・削除記録だけを残す。旧入口棚卸しも訂正 |
| 管理ターミナルの参照 | 関連4文書に廃止済み注記。[PR #355](https://github.com/sjinnouchi-ux/mgmt-terminal/pull/355)、merge `47811667f884519ca2aed43f72b4ab89c9c29222` |
| Gitブランチ | mainに統合済みで未統合PRがない旧 `codex/ai-keiei-shindan-setup` と、今回の両repo作業branchをSHA照合後に削除 |

## 削除した専用Googleファイル

1. AI経営実装度診断WEBアプリ（GAS project）
2. AI経営実装度診断WEBアプリ_マスタ_2026-07-04（回答ログを含む専用Sheet）
3. ai_keiei_shindan_web_impl_spec.md（正本）
4. ai_keiei_shindan_web_impl_spec.md（旧版）
5. ai_keiei_shindan_app_spec.md
6. config.seed.json
7. codex_kickoff_prompt.md
8. ANSWERS_FROM_CLAUDE.md

所有者と接続アカウントの一致を確認してから削除した。回答行や個人情報本文は取得・転記していない。

## 検証

- 起動時workspace main `45d2afa2e96f3098c97d54d9de368d9a32e0b1cb`。GitHub共通起動・台帳・AGENTS・Primary Docsを確認し、対象を確定した。Memory MCP該当0件。
- GitHub owner内の名称・slug検索とworkspaceの専用ディレクトリ外64ファイルを調査。うち空の`.gitkeep`は内容なし。現役記載を削除または廃止注記へ変更。
- PR #69のFiles changedを照合。専用ファイル17件削除、その他変更対象は台帳・棚卸し・作業ログ・削除記録・計画。対象外61ファイルのblob SHAは不変。台帳の他プロジェクト行は完全一致。
- GitHub Pages build and deployment [run 39080566925](https://github.com/sjinnouchi-ux/workspace/actions/runs/39080566925) は対象merge SHAでsuccess。
- 旧公開ページとGAS URLのHTTP確認はともに404、curl exit code 0。ブラウザ表示でも確認。
- 管理ターミナルPRは文書5件のみ。change-scopeはsuccess、アプリ/Worker/Windows等の重い回帰はscope判定でskipped。code/DB変更はない。
- 旧診断アプリの機能テストは、機能撤去のため実行しない。変更範囲・残存ファイル・公開停止を検証した。

## 保存・対象外

GitHub connectorで直接branch・commit・PRを作成し、mainへ統合した。ローカルclone、未commit/未push変更、ローカル専用の必要成果物は作成していない。CLIは認証状態確認、既知SHAの統合済みbranch削除、公開URLの読取りに限定した。

共有workspaceリポジトリ、Git履歴、他プロジェクトのファイル、共通GitHub Pages設定、監視workflow、Google共通認証は保持する。Git履歴の強制書換えは行っていない。削除済みを示す台帳・注記・監査記録は意図して残す。

管理ターミナルは文書整理のみ。共有の本番DB内に残る当時の管理用登録行は今回照合・削除していない。診断アプリ本体・専用Sheet/GASの撤去とは区別する。再公開・旧cloneからの復元は行わない。
