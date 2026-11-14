# 旧家計簿Worker/GAS — Legacy / Frozen

状態：**Legacy / Frozen（2026-11-14）**。このフォルダは移行前のWorker/GASと作業履歴の保存参照用です。家計簿プロジェクト本体は稼働を続けており、現行の開発・保守・配備の正本は **[sjinnouchi-ux/kakeibo-liff](https://github.com/sjinnouchi-ux/kakeibo-liff)** です。

## 参照の入口

最初にworkspace mainの[共通起動手順](../codex/CODEX_DESKTOP_STARTUP.md)と[PROJECTS](../PROJECTS.md)、次に現行repo mainのAGENTS/Primary Docsを確認してください。現行repoへ向く既存Alias・Canonical Entryは維持しています。

このフォルダの `wrangler.toml` は、現行と同じWorker名 `yumekango` を指定する旧設定です。通常の配備入力として使うと現行Workerを上書きし得るため、ここから配備・GAS再公開・旧設定の復元を行わないでください。保存していることを、検証済みの本番rollback版であることとは扱いません。

## 保存対象

| ファイル | 扱い |
| --- | --- |
| `worker.js` | 旧GAS中継Workerの歴史的source |
| `wrangler.toml` | 旧配備設定。実行用ではなく参照専用 |
| `gas/Code.gs` | 旧GAS sourceの保存版 |
| `gas/sendBudgetReport_patch.gs` | 過去の独立patch。現行版へ自動適用しない |
| `docs/work_log.md` | 過去の実施・未完記録。古い未完checkboxを現役taskへ自動転記しない |

上記5ファイルは凍結整理時に内容を変更せず保持しました。過去ログにある `global.env`・token再発行・Secret更新・旧GAS配備の記述は、当時の記録であり現在の実行指示ではありません。現在の資格情報の扱いは現行repoの `docs/secret-management.md` を優先します。

## 凍結の範囲と保持

- このworkspace内の旧ソースだけを凍結します。workspace repo全体や現行家計簿repoをarchive/freezeする操作ではありません。
- 新規機能追加・通常配備・旧GASへの切戻しは行いません。履歴の読取り、証拠照合、案内・記録の保守は可能です。
- 旧LIFF、token/Secret/version/IAM、既存Worker version、Cloud Run旧revision/rollback版、Sheets/DBは削除・変更しません。実際のrollbackは現行repoの固定版・運用記録から判断します。
- 新たな具体的指示で変更や再開を行う場合は、先に現行repoで対象と必要性を整理し、現在の配備・認証・保存版を確認します。凍結前の配備コマンドをそのまま再実行しません。既承認の範囲は共通承認方針に従い引き継ぎます。

## 根拠と残範囲

- [旧GASと専用監視の退役記録](https://github.com/sjinnouchi-ux/mgmt-terminal/blob/6b10ab8e87252c2bf05af18066530cc32c079078/docs/reports/2026-11-14-legacy-gas-retirement-execution.md)
- [現行Workerの未使用GAS_URL整理記録](https://github.com/sjinnouchi-ux/kakeibo-liff/blob/2ef6dc6131d7695650689c3040924d0c3d806c84/docs/reports/2026-11-14-worker-gas-url-cleanup.md)
- [今回のworkspace凍結整理記録](../docs/reports/2026-11-14-yumekango-worker-legacy-freeze.md)

今回の文書整理を、旧LIFF廃止・token失効・Stage B全体の受入完了と混同しません。残件は[家計簿Issue #3](https://github.com/sjinnouchi-ux/kakeibo-liff/issues/3)で管理します。
