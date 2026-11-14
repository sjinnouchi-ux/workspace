# 共通workspaceの旧ブランチ保持確認

2026-11-15 JST。GitHub整理の続行依頼により、前回の「一致するmerged PRがない」7本を確認した。元branchの削除・更新、merge/close、旧提案の再採用は行わない。

## 起動・範囲

GitHub mainの共通startup→PROJECTS→既定main/AGENTS・README/Codex入口・関連作業記録を先に確認した。照合元は `00c978297e1e34ae90f7325acd277702d48c39e8`。Canonicalは `sjinnouchi-ux/workspace` のCodex Desktop共通運用。GitHub確認後の `workspace branch-preservation` Memory検索は関連0件。Codex単独・GitHub connectorのみで実施し、ローカルclone/worktreeは作成しない。

7本のうちKアラートは本人保留、SNS案は破棄済みのため内容調査・採用判断を進めない。残る5本について、現在tip・closed/unmerged PR・mainとの履歴関係・固定source tree・既存保存台帳を確認した。

## 7本の判定

| branch / 固定tip | 判断と根拠 |
| --- | --- |
| `agent/add-frontend-design-skill` / `6bec8ffd68adf90ab2931792a5f7b1838c1d7d24` | [PR16](https://github.com/sjinnouchi-ux/workspace/pull/16)はclosed/unmerged。11原版は保存台帳に固定され、うちscript/skill/source/license4件はmainの非実行snapshotとblob一致。残る旧ログ・bootstrap等7件は元head/branch参照で保持する設計なのでbranch保持 |
| `agent/mgmt-terminal-core-project-router` / `f07cfef0328f4e5b2382ab202c143e1d81e698da` | [PR31](https://github.com/sjinnouchi-ux/workspace/pull/31)はclosed/unmerged。PROJECTS原版1件は固定参照保存。旧Core親構想は未採用、現行routerを維持しbranch保持 |
| `agent/windows-utf8-guidance` / `9d1e6b6f8be60beac8fcc08a4a8288e5e589fc07` | [PR35](https://github.com/sjinnouchi-ux/workspace/pull/35)はclosed/unmerged。UTF-8の有用な注意は現行startupへ採用済み。旧startup/log2原版の参照元としてbranch保持 |
| `docs/nucbox-memory-mcp-policy` / `7000d12e61010de710898316744199070976b750` | [PR55](https://github.com/sjinnouchi-ux/workspace/pull/55)はclosed/unmerged、[終了理由](https://github.com/sjinnouchi-ux/workspace/pull/55#issuecomment-5248279120)はPR56への置換。旧4原版をbranchに保持し、現行V2を上書きしない |
| `ops/disable-codex-line-notify-20260901` / `4b5085aeb3ea732447caff0a5cf18affdc5dfe01` | [PR62](https://github.com/sjinnouchi-ux/workspace/pull/62)はclosed/unmerged。9/1の通知停止記録は採用済みだが旧work_log原版1件は固定参照保存。branch保持。現在のhook状態を今回調べたとは扱わない |
| `codex/k-alert-production-cloud-run` / `ac85cfbc82b9812bb9eb8fd477962b388b5f9499` | Kアラート保留。ref存在確認のみで内容再評価・配備再開なし |
| `research/sns-local-feasibility-20261114` / `bab7073e86bf554122fdd4c52ec8063d4d764463` | [PR80](https://github.com/sjinnouchi-ux/workspace/pull/80)は利用者指示による破棄・closed/unmerged。終了方針の確認まで。mainへの案の移管、実装、外部取得を再開しない |

## 原版と現行運用を区別

[既存の保存方針](../history/workspace-pr-cleanup-2026-11-13/README.md)は、旧PR16/31/35/62の全15原版を固定head/path/mode/type/blobへ結び、元branch/headを削除しないことを明記している。[manifest](../history/workspace-pr-cleanup-2026-11-13/manifest.json)の15件を今回の各branch treeと照合し一致した。追加snapshot4件もmain treeと一致した。4件だけコピーした状態を15件の全文コピーと取り違えない。

[過去の採否記録](2026-11-13-workspace-entrypoint-pr-cleanup.md)も再確認した。branchがmainの祖先でなくても、有用な方針の採用と原版の固定参照保存は成立している。逆に、PRが終了していても、元branchを前提にした保存方針は消えない。

PR55の後継[PR56](https://github.com/sjinnouchi-ux/workspace/pull/56)はmerge `74eff4c3b1b80199b27eb96e8823e93ed27caa8a` が照合元mainの祖先であることを確認。現行custom instructionsのV2 marker、`development_memory`、Codex単独オーケストレーションと依頼時の固定read-only監査を照合した。旧V1の `shogun_memory` や退役済み運用へ戻さない。

### PR55の旧原版4件

次の元blobは照合元main treeの同一path/別pathに同一blobがなく、今回の固定head/branchを保管場所として明記する。これは情報喪失の報告ではなく、原版がbranchに存在することの確認である。現行方針への置換と旧原版の全文保存を分ける。

| 元path（固定headは上表） | 確認したblob |
| --- | --- |
| `codex/CODEX_DESKTOP_CUSTOM_INSTRUCTIONS.md` | `07bc68e39b753bbe8c23a93a2c29e03f81adbda6` |
| `codex/docs/superpowers/plans/2026-08-11-nucbox-codex-memory-mcp-policy.md` | `939c6c95e6d5c3773006e430c33e4aae8d5d7d4a` |
| `codex/docs/superpowers/specs/2026-08-11-nucbox-codex-memory-mcp-policy-design.md` | `d15be6dde3409dd9c6b23a23c4b417f1d4aa6132` |
| `codex/work_log.md` | `4e60d7000bdf2e0a9f00d14533dd79541a8906af` |

## 検証・境界

- 実査5本のbranch差分19 branch/pathを確認し、4件はmain snapshot、11件は既存の元head固定参照、4件は上記PR55原版として確認した。
- mainに当該branch固有commitがないことと、有用な内容が後継へ採用済みであることを混同しない。変更元のtree・保存台帳のblob/mode/type・closed/unmerged状態を照合した。
- 文書2件だけを保存し、既存work_log全文はそのまま保持する。GitHub固定commitから全文を読戻し、対象外全blobと7本のtipを再照合する。
- コード/設定/配備入力を変更しないため、重いアプリ/DB試験、手動Actions、外部監査、skill installは不要。過去の成功試験を今回実行したとは扱わない。
- 本番/DB/認証/token/Secret/version/IAM・旧revision/rollback、通知hook/Windows/Memory設定には操作しない。保留/破棄を解除しない。
- 旧branch・PRをすべて保持。ローカル作業場・未commit/未push/ローカル専用の必要成果物なし。実障害修正ではないためMemoryへの新規失敗pattern登録なし。

本件でworkspaceの削除候補を追加しない。開発環境repoの3本を含む全体の判定は同repoの日付付き作業記録で管理する。
