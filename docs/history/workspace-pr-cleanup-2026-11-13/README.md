# workspace旧PRの保存索引

2026-11-13。対象PR16/31/35/62の全15変更ファイルを、[manifest.json](manifest.json)で元head・branch・path・mode/type/blobへ固定しました。元PRのhead/branch/title/本文は保持し、branch削除・旧branchの一括mergeはしません。

旧ログ・bootstrap・PROJECTS全文は、不要な個人pathと旧Shogun手順を重複保存しないため固定Git原版への参照で保持します。新規snapshotを全15件コピーしたという意味ではありません。差分の有用な事実は[採否記録](../../reports/2026-11-13-workspace-entrypoint-pr-cleanup.md)と現行文書へ引き継ぎます。元Git原版は後日の整理でも削除しないでください。

## 追加の非実行snapshot

| 元source | 保存先 |
|---|---|
| GitHub確認script | [Test-GitHubConnection.ps1.txt](pr-16/codex/scripts/Test-GitHubConnection.ps1.txt) |
| frontend-design skill | [SKILL.md.txt](pr-16/codex/skills/frontend-design/SKILL.md.txt) |
| 出典・固定upstream・SHA-256 | [SOURCE.md](pr-16/codex/skills/frontend-design/SOURCE.md) |
| Apache License 2.0 | [LICENSE.txt](pr-16/codex/skills/frontend-design/LICENSE.txt) |

上記4件は元blobと同一。skillの登録先やactive script配置ではなく、各PCへの導入、更新、実行は行っていません。SOURCEのupstream固定commitとlicenseは当該保存版の出典であり、最新upstreamと同じとの主張ではありません。

旧PR35のShogun側同期記録、PR16の7月接続成功、PR62の9月local hook除去は日付付き履歴です。現在の認証、hook無効状態、全PCの設定を今回再検証したものではありません。
