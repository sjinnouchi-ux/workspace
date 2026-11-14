# workspace旧家計簿Worker/GASのLegacy/Frozen整理（2026-11-14）

## 結果と範囲

利用者の明示依頼に従い、workspaceの `yumekango-worker/` を **Legacy / Frozen** の保存参照用として位置付けた。現行家計簿のCanonical Entry `sjinnouchi-ux/kakeibo-liff`、Active / Pilot、Aliasは維持する。workspace repo全体や現行家計簿をfreeze/archiveする作業ではない。

変更はPROJECTSの関連2セル、旧フォルダのREADME/AGENTS追加、本記録の文書4件だけ。旧Worker/GAS/配備設定/過去ログは移動・削除・編集しない。旧LIFF、token、Secret/version/IAM、既存Worker version、Cloud Run旧revision/rollback版、Sheets/DBには変更操作を行っていない。

## 正本確認

オンライン起動手順→PROJECTS→対象のdefault branch/AGENTS→Primary Docsの順に確認した。workspace開始main `5799f5daf931e19732c1534928d8099db71fbdae`、default main、root AGENTS/README/Git Handoff Protocolと旧作業ログを確認。現行家計簿main `2ef6dc6131d7695650689c3040924d0c3d806c84` とAGENTS/Primary Docs、直前の配備記録も確認した。正本確認後のMemory MCP検索は関連0件。

## 変更内容

- `PROJECTS.md`：現行家計簿行のNotesに旧ソースの凍結を追記。Status・Alias・Canonical Entry・Primary Docsは不変。「共通・補助入口」の旧Worker/GAS行をLegacy/Frozen・参照専用へ更新し、新READMEへ案内する。新しい独立project行や重複Aliasを追加しない。
- `yumekango-worker/README.md`：凍結日、現行repo、保存5ファイル、通常配備に使わないこと、保持対象、新しい具体的指示時の確認先と根拠を明記する。
- `yumekango-worker/AGENTS.md`：当該ディレクトリ配下だけの取扱いを明記。履歴参照/文書保守は可能とし、旧設定の通常配備や古い未完taskの自動再開を防ぐ。
- 本report：判断・保持対象・検証と未実施範囲を残す。

旧wranglerのWorker名は現行と同じ `yumekango`。source名だけで安全な別環境と推測して配備しない。保存版の存在を、現在のruntimeに対して検証済みのrollback手順と扱わない。

## 保存対象のblob

以下5件は内容不変で保持する。

| ファイル | 開始時Git blob |
| --- | --- |
| `yumekango-worker/worker.js` | `19cbbae464755bd59c583803fd6b8d0c0a2efc6b` |
| `yumekango-worker/wrangler.toml` | `5583dda391f49db7d2e722f960a76a9d5b2f0561` |
| `yumekango-worker/gas/Code.gs` | `e94d7ecf2ae7313b39e605daaab06711dfad4df6` |
| `yumekango-worker/gas/sendBudgetReport_patch.gs` | `9130b6413dbccc70363bc1a5e1c219cf16b908df` |
| `yumekango-worker/docs/work_log.md` | `9987b95b6e65f422cd420d2180dae14faa7c8cf3` |

過去作業ログの完了/未完欄、古い認証元やGAS配備の記述を歴史的内容のまま保ち、現在の運用は新READMEと現行Canonicalへ案内する。古いログに含まれる個人情報やURL実値を本記録へ複製しない。

## 照合した既存証拠

- [旧GASと専用監視の退役](https://github.com/sjinnouchi-ux/mgmt-terminal/blob/6b10ab8e87252c2bf05af18066530cc32c079078/docs/reports/2026-11-14-legacy-gas-retirement-execution.md)：GAS archive、監視pause、台帳disabled、履歴/旧LIFF/token/rollback版の保持。
- [Worker設定整理](https://github.com/sjinnouchi-ux/kakeibo-liff/blob/2ef6dc6131d7695650689c3040924d0c3d806c84/docs/reports/2026-11-14-worker-gas-url-cleanup.md)：plain GAS_URLをmain/本番から除去、codeと他bindings/settings不変、旧version保持。
- 今回は上記固定commitの既存証拠を参照した。live再配備や新しい実スマホ受入を行ったとは数えない。

## 検証・操作境界

完了前の検証として、PROJECTSの行数・列数、変更2セル以外の一致、現行Alias/Status/Canonical/Primary Docsの保持、新文書のリンク先とscope、秘密値を含まないことを確認する。保存後は固定commitから文書全文、差分が文書4件だけであること、保存対象5blobの一致をreadbackする。家計簿Issue #3はPROJECTS更新とLegacy/Frozenの2項目を完了へ更新し、他のチェック・open状態は保持する。

workspaceのworkflowも確認し、既存Supabase keepaliveのschedule/workflow_dispatchだけで、今回の文書pushから旧Workerを自動配備するworkflowはない。既存workflowは変更・手動実行しない。

これは文書・routing案内だけの変更で、アプリの挙動・配備入力・本番接続先・自動実行設定は変更しない。したがってアプリ全体試験・手動CI・配備・監視停止・認証/Secret取得を起動しない。runtime保持は「本タスクで変更操作なし」として記録し、token値やlive全項目を新しく読み出して再検証したと主張しない。

GitHub connectorで必要文書を直接保存し、local clone/scratch/未commit/未push成果物は作成しない。新しい実装や修正した障害はないため、Memory MCPへVerifiedFailurePatternを追加しない。MF/M17凍結、Kアラート/SBA/公開/LINE画像等の保留、GA4別チャットは維持する。

## 残範囲

[家計簿Issue #3](https://github.com/sjinnouchi-ux/kakeibo-liff/issues/3)のStage B全体はopen継続。旧LIFF廃止、token/rollback版撤去、保持Secret binding2件の処理、Stage B全体の安定稼働評価・実登録等の受入・設計完了記録は今回の完了へ含めない。他タスクへ進まず、今回の結果を利用者へ報告する。
