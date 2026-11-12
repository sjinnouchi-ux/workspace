# GitHub整理 タスク3・4 — 2026-11-12

Canonical: `workspace` / default `main`。共通起動・台帳確認: workspace `02b6777c9f13f6651a62ccabf503f60ce09b9c52`。repoのAGENTSとPrimary DocsをGitHubから先に確認した。Memory MCPのrepo/github検索は該当なし。

開始main: `02b6777c9f13f6651a62ccabf503f60ce09b9c52`。履歴検証main: `02b6777c9f13f6651a62ccabf503f60ce09b9c52`。

## タスク3: 記録救出

このrepoはタスク4の対象。タスク3の重点対象は管理ターミナル・議事録・社労士事務所・家計簿の未統合実施記録である。

## タスク4: マージ済みブランチ

開始時の全branch数: 53（既定branchを含む）。検証済み削除候補: 46。保持する非既定branch: 6。[全候補・先端SHA・統合PR・保持理由](2026-11-12-merged-branch-cleanup.json)。

候補の必須条件:

1. 既定branch・保護branchではない。
2. 同一repoのmerged PRのheadと現在tipが完全一致し、マージ後の追加commitがない。
3. merge commitが検証mainの祖先である（squash/rebaseのsource SHA非一致だけでは除外/採用しない）。
4. 開PRのhead/baseから参照されず、mainの実行コード・設定・workflowにbranch名の参照がない。
5. 実削除前に一覧・開PR・稼働中Actionsを再取得し、先端SHAを固定したforce-with-lease付きatomic pushで削除する。変更されたbranchは削除しない。

削除結果: 46本を削除し、GitHub一覧で消失を確認。実行直前53本 → 実行後7本（mainを含む）。対象外branchの消失0・SHA変更0。削除見送り0。自動削除設定は不変。[実行結果](2026-11-12-merged-branch-cleanup-result.json)。削除前証拠commit: `380dc60c564c03b92aa1494b0cc3e3509a4b8f06`。保存した先端SHAから同名refを復元可能。

## 検証と範囲

文書差分は固定Git commitから抽出し、secret形式を走査した。対象path・PR/head・main祖先関係・内容hash・保存後読戻しの全文一致を確認した。sourceやmigrationを変更しないためアプリ/DBの重いテストと手動Actionsは不要。既存必須チェック・保護・自動削除設定・本番・権限・課金・外部データを変更しない。

作業環境はWindows Codex Desktop。タスク専用bare cloneを履歴の読取りだけに使用し、GitHub文書変更はconnectorで保存する。bareにはworking tree/upstream/未追跡作業なし、ローカル実装commitなし。取得元は上記CanonicalのHTTPS originで、既存cloneは使っていない。最終記録のGitHub読戻し後に専用取得物を整理する。
