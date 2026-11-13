# workspace入口文書・旧PR整理

2026-11-13 JST。利用者の「それはすぐに整理してください」に基づく、workspace共通入口とPR16/31/35/62の限定整理。管理PR448/449および他repoの未整理PRは今回の対象外。

## 正本と開始状態

オンラインのstartup→PROJECTSを順に取得し、Canonical `sjinnouchi-ux/workspace`、default main `341188f96603e1d806029d24971577580d4ffd1d`、AGENTS、共通Actions/承認/Git handoff契約、README/MCP/責務文書/Codex入口を確認した。GitHub確認後のworkspace/component限定Memoryに関連する記録なし。ローカルclone・過去資産を正本にしていない。

README、MCP、責務文書は旧Shogunを現役の基盤・設計担当として記載していた。一方、最新startup/PROJECTSはCodex Desktop単独オーケストレーションと退役を指定しており、この不一致を現行文書で解消する。

## PR別の採否と保存

| PR・固定head | 有用な内容の扱い | 非採用・保持する境界 |
|---|---|---|
| [16](https://github.com/sjinnouchi-ux/workspace/pull/16) `6bec8ffd68adf90ab2931792a5f7b1838c1d7d24` | 接続境界とINCONCLUSIVE、別経路の失敗だけで認証を破棄しない方針をstartup/custom bootstrap/new boundary文書へ採用。7月の接続監査は履歴として保持 | 旧Shogun起動/ローカル配置や、無条件の新chat/restart要求を復元しない。旧GitHub確認scriptは必須化せず非実行snapshotへ。frontend-designのsource/licenseを同じblobで保存し、各PCへinstall/updateしない |
| [31](https://github.com/sjinnouchi-ux/workspace/pull/31) `f07cfef0328f4e5b2382ab202c143e1d81e698da` | Core DB/AIの旧router提案を固定原版として保持 | 現行Support/Workflow・Canonical mgmt-terminalを保持。Active/Parent・新alias・旧charterへのPrimary Docs差替えは採用しない。旧charterは管理repoのPR21履歴内に保存されており、現行primaryにない。将来のCore親構想を禁止せず、再採用時に現mainから別の必要差分と判断を作る |
| [35](https://github.com/sjinnouchi-ux/workspace/pull/35) `9d1e6b6f8be60beac8fcc08a4a8288e5e589fc07` | UTF-8再読、PowerShell5.1のBOMなしUTF-8保存注意、編集後再確認の3行をそのまま現在startupへ追加 | 古いstartup/log全体で現行内容を上書きしない。Shogun側同期は当時の記録であり今回再実行しない |
| [62](https://github.com/sjinnouchi-ux/workspace/pull/62) `4b5085aeb3ea732447caff0a5cf18affdc5dfe01` | 9/1のowned Stop handler除去記録を日付付きでwork_logへ採用し、hooks READMEへ状態境界を追補 | 現在のhandler数は未照会。通知・Remove/Apply再実行、server/Secret/IAM/配備変更なし。無効化履歴の保存を再有効化承認にしない |

管理側charterの保存先は、管理main `0dc1eea55306432090f606d58e853e39d5bbcf29` の `docs/history/task11-crm-20261113/pr-21/docs/superpowers/specs/2026-07-19-management-terminal-core-db-ai-charter.md`。PR31の旧依存を新規実装の指示へ変換しない。PROJECTS本文と全プロジェクト状態は今回変更しない。

## 原版の保持方法

全15file（PR16=11、31=1、35=2、62=1）について、固定PR headのrecursive treeとGitHub file-listのpath/mode/type/blobを照合した。[manifest](../history/workspace-pr-cleanup-2026-11-13/manifest.json)が原版の所在を固定する。

元head/branchは削除せず保持する。古いwork_log・bootstrap・PROJECTS全文の個人pathや退役手順を新pathへ重複コピーせず、これらは元Git原版への固定参照で保持する。追加保存するscript/skill/source/license4fileだけは元blobを再使用し、byte同一の非実行snapshotとする。原版15fileすべてを新規snapshotへコピーしたとは報告しない。旧README/MCP/責務文書の原版blobも同manifestへ固定する。

## 現行入口の変更範囲

- READMEと責務文書をCodex Desktop/host限定Memory/依頼時のみの固定read-only監査へ整合する。
- MCP入口の旧Shogun構築・一律credential backup/copy手順を現行方針から外し、接続境界と各repoのsecret契約へ案内する。runtimeやバックアップ実体を操作しない。
- Codex索引の既に存在しないofficial_line_ai_integration.mdへのリンクを外す。旧LINE資料の内容や通知設定は変更しない。
- Codex入口の過去clasp制約を全PCの現在値へ一般化しない。既存規則・承認・本人操作・安全停止は保持する。
- current custom instructionsのMemory marker、現行の退役/オンライン正本/秘密保護は維持する。各PCのSettingsやグローバルAGENTSへの同期は行わない。
- work_logの既存全文は保持し、今回記録とPR62の日付付き履歴を追記する。claude_logは履歴のまま変更しない。

## 検証と完了gate

文書・参照保存のみ。実行コード、workflow、依存、DB、配備入力、設定、権限を変更しないため、重いアプリ/DB試験、手動Actions、外部監査、live接続試験は不要。

公開前に相対リンク53件、追加差分の秘密値/個人path・UTF-8/文字化け/行末空白、原版15fileのfile-list/tree一致を確認し、問題なし。元4branchの存在とhead一致も照合した。4snapshotのblob一致と対象外blob保持は保存後の読戻しでも確認する。親SHA固定・expected-SHA非forceでmainへ保存し、固定commitから全文を読戻した後に旧4PRを未merge closeする。元title/本文/head/draft/branch保持とclosed状態を独立readbackし、結果を本書へ追記する。GitHub connectorで保存し、local clone・未commit・未push成果物を作らない。

本作業では新しい製品不具合の原因修正・検証はないためMemoryへVerifiedFailurePatternを追加しない。他taskへ進まない。

## 保存・終了結果

- 保存commit：`ad8a7ea15981139230b849911497c5e0ea27b0a7`。12文書全文のGitHub固定commit読戻し一致、追加snapshot4件の元blob/mode一致、変更対象外65blob不変、PROJECTS/AGENTS/claude_log不変を確認した。
- 2026-11-13 23:53 JSTにPR16/31/35/62をclosed / unmergedへ変更し、その後の独立GETで4/4を確認。元title/本文/head SHA/head branch/draftは不変。元4branchも同headで存在する。
- workspaceのopen PR一覧は0件を確認。他repoのPR448/449や保留項目には操作していない。
- PR16/31を元提案の全採用として扱わず、上表の採用・非採用・履歴を維持する。PR35の3注意行は採用済み、PR62の現local状態は未再検証。
- GitHub上の文書更新と旧PRの状態変更のみ。新しいPRコメント・他者への連絡、実行コード、skill install、各PC設定、通知hook、認証、runtime、配備、DB、Secret/IAM、手動Actions、外部監査の操作はなし。
- local clone/worktree・未commit・未push・local専用成果物は作成しておらず、ローカル整理対象なし。終了結果は本書とwork_logに追記する。
