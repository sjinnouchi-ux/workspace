# エージェント運用制限の文書レビュー

2026-11-01 JST。利用者の具体的な依頼に基づく運用文書改善。

- Canonical repo: `sjinnouchi-ux/workspace`、既定branch `main`。
- 調査base: `28f129d458932492b6812054c88b6e99097a1e77`。
- 作業branch: `codex/agent-consent-operations-20261101`。タスク専用の新規Windows-native clone、開始時clean / ahead 0 / behind 0。
- fetch refspecは取得量を絞るmain-only。push先branchは明示指定し、Git transportでremote HEADを照合する。
- 関連Memory MCP検索は0件。GitHubを正本として継続した。実システム障害の修正・live再検証ではないため新たなVerifiedFailurePatternは登録しない。

## 調査と変更

共通起動手順・オンライン台帳から開始し、共通AGENTS/Git引継ぎ/Actions方針とGAS手順を確認した。`gas_browser_operation.md`のOAuth同意・アカウント選択の一律本人操作、公開ごとの再確認、同意後の無条件の関数再実行を改訂した。共通承認方針を追加し、startup/AGENTS/Git引継ぎから接続した。個別repoの認証・秘密管理契約を解除せず、本人の承認判断と実操作担当を分ける。

## 判断の確認

| 場面 | 改訂後の運用 |
| --- | --- |
| 対象・scope・影響が具体的に承認済み | 既承認を照合しCodexが実行・読戻しまで継続。工程名/repo/ブラウザ切替だけの再承認は不要 |
| 標準Google同意 | 本人の判断は具体的なチャット承認、許可された実操作はCodex。広いDrive scopeと固定folder制限を区別 |
| 新scope/対象/費用/規約など未承認差分 | 依存しない準備を済ませ、差分を具体化して可能ならチャットで確認。未回答は承認ではない |
| 上位ツールの確認・専用承認UI・本人操作/安全停止 | 根拠を示して遵守。repo方針や既承認で迂回しない |
| MFA等の本人しか行えない部分 | 必要操作だけ引継ぎ、可能ならスマホで継続。秘密値をチャットへ要求しない |
| 文書だけの作業 | 本番ログイン/3画面保持は不要。実操作前の対象別本人確認は維持 |
| 完了済みまたは結果不明の操作 | 現状/元IDで照会。migration/認可/配備を無条件に再実行せず、新IDや再送で解決しない |
| 明示的停止・本人不一致・権限不足 | 指示と認証境界を維持し、影響を受ける操作を停止。独立した文書準備・検証は継続 |

## 検証と非変更範囲

- 初回差分検証は3repo計19 Markdownで成功。`git diff --check`、UTF-8、追加した相対/3repo間リンクの実ファイル存在、追加行の秘密値形式検査、旧一律本人クリック/全タスクログイン記述の除去を確認した。記録追加後も同じ検査を行う。
- 議事録の必須 `tools/verify_legacy_removed.ps1` は `LEGACY_REMOVAL_VERIFIED`。
- 文書の判断表を利用者要件と照合した。新規runtime試験/Google認可/実データ処理はしていない。
- 重い全体回帰・live試験は文書のみでコード/実行入力/manifest変更がないため省略。統合前は最新main差分、Markdown限定、リンク、独立レビューと必須GitHub checksを確認する。必須チェックの解除・迂回はしない。
- 手動Actions dispatch/rerunは0。workflowの変更・課金上限変更・定期監視停止はしない。PR自動実行は既存scope判定に従い、結果はPRに記録する。
- OAuth scope/grant/IAM/Secret、DB/Storage/API、worker/GAS/trigger、配備・公開・本番の安全機構は変更しない。文書上の承認解釈をlive権限の付与や受入成功と扱わない。

## レビュー指摘への対応

作業ログの冒頭説明を日付別の新節から分離し、元の位置へ戻した。 最終差分を再検証し、push後の完全SHAで独立再確認する。

## GitHub引継ぎ

最終head/base完全SHA、PR、独立レビュー、Actions結果と統合状態は対応PR本文へ記録する。全変更と本記録をpush・照合し、必要な未コミット/未push/ローカル専用情報がないことを確認後、今回の専用cloneと一時編集・検証補助だけを整理する。別タスクの作業場、稼働runtime、既存証拠には触れない。
