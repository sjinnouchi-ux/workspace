# Claude Desktop Report Intake

Claude Desktopアプリ（両PC個別環境・同期しない）の作業成果を、CodexがGitへ統合するオペレーションの正本です。

## 役割分担

- Claude Desktop: 相談・分析・調査の成果を「作業レポート」1ファイルにまとめ、Google Drive受信箱へ保存する。GitHubへは直接pushしない。
- Codex: 受信箱を確認し、レポートを対象repoへcommit/pushし、Drive側を処理済みへ移動する。
- 両PCのClaude Desktopは個別環境のまま運用し、環境の同期は行わない。共有されるのはDrive受信箱とGitHub上の統合結果だけである。

## Drive受渡場所

| 用途 | Windows path | 備考 |
|---|---|---|
| 受信箱 | `G:\マイドライブ\Claude保存\レポート\受信箱` | Claude Desktopが保存する唯一の受渡先 |
| 処理済み | `G:\マイドライブ\Claude保存\レポート\処理済み` | Codexが統合完了後に移動 |
| 保留 | `G:\マイドライブ\Claude保存\レポート\保留` | プロジェクト特定不能・要ユーザー確認のもの |

両PCでGoogle Drive同期済みのため、どちらのPCで作成したレポートも同じ受信箱に集まる。

## ファイル命名規則

```text
YYYY-MM-DD_<projectエイリアス>_<内容>.md
例: 2026-07-20_kakeibo_フェーズ3設計相談まとめ.md
```

- `<projectエイリアス>` は `PROJECTS.md` の `Alias` にある表記を使う。
- 同日同名の衝突時は末尾に `_2` を付ける。

## レポートテンプレート

```markdown
# <タイトル>

- Project: <PROJECTS.mdのProject名>
- Date: YYYY-MM-DD
- Source: Claude Desktop（デスクトップPC / ノートPC）
- Type: 設計相談 / 調査 / 分析 / レビュー / その他
- Target repo: <Canonical EntryのURL>
- 反映先希望: docs/reports/ （別の場所を希望する場合のみ変更）

## Summary

（3行以内の要約）

## 本文

（成果本体）

## Codexへの依頼事項

（統合以外に必要な作業があれば。なければ「なし」）
```

## Claude Desktop側のルール

- レポートに秘密値、token、認証情報、`.env` の中身を含めない。
- プロジェクトは `PROJECTS.md` と照合して書く。未登録の場合はレポート内に「未登録」と明記し、勝手に新プロジェクト名を作らない。
- 1レポート1ファイル。長大化する場合はテーマごとに分割する。

## Codex側の統合手順

1. Codex作業開始時（またはユーザー指示時）に受信箱を確認する。
2. レポートのProject欄を `PROJECTS.md` と照合し、対象repoを確定する。特定できない場合は保留へ移動し、ユーザーへ確認する。
3. 対象repoの `docs/reports/YYYY-MM-DD-<内容>.md` としてcommit/pushする（反映先希望があればそれに従う）。
4. レポートが設計判断を含む場合は、対象repoの `DESIGN_LOG.md` に1行の参照（日付・タイトル・パス）を追記する。
5. Drive側のファイルを処理済みへ移動する。
6. `codex/work_log.md` に統合結果（ファイル名、対象repo、commit）を記録する。

commit反映まで完了しないうちに受信箱からファイルを消さない。GitHubへの反映が正本、Driveは経路である。

## CODEX_DESKTOP_STARTUP.md への追記文面（案）

以下を `codex/CODEX_DESKTOP_STARTUP.md` の適切な位置（Deliverable Storageの後など）へ追記する。

```markdown
## Claude Report Intake

Claude Desktopの作業レポートは `G:\マイドライブ\Claude保存\レポート\受信箱` に集まる。

- Codex作業開始時に受信箱を確認し、`claude/REPORT_INTAKE.md` の手順で対象repoへ統合する。
- 統合完了（commit/push確認）まで受信箱からファイルを削除しない。処理後は処理済みへ移動する。
- プロジェクトを特定できないレポートは保留へ移動し、ユーザーへ確認する。
- レポートに秘密値が含まれていた場合は統合を停止し、該当箇所を報告する。
```
