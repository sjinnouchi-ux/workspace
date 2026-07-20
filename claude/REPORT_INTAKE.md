# Claude Desktop Report Intake

Claude Desktopアプリ（両PC個別環境・同期しない）の作業成果を、CodexがGitへ統合するオペレーションの正本です。

## 役割分担

- Claude Desktop: 相談・分析・調査の成果を「作業レポート」1ファイルにまとめ、Google Drive受信箱へ保存する。GitHubへは直接pushしない。
- Codex: 受信箱を確認し、レポートを対象repoへcommit/pushし、Drive側を処理済みへ移動する。
- 両PCのClaude Desktopは個別環境のまま運用し、環境の同期は行わない。共有されるのはDrive受信箱とGitHub上の統合結果だけである。

## 発動条件

- 受信箱の確認・統合は、**ユーザーの明示指示、または明示的なintakeタスクとしてのみ**行う。
- 通常タスクの開始時に受信箱を自動確認しない。

## Drive受渡場所

| 用途 | Windows path | 備考 |
|---|---|---|
| 受信箱 | `G:\マイドライブ\Claude保存\レポート\受信箱` | Claude Desktopが保存する唯一の受渡先 |
| 処理中 | `G:\マイドライブ\Claude保存\レポート\処理中\<PC名>` | Codexのclaim用。claim時に無ければ作成する |
| 処理済み | `G:\マイドライブ\Claude保存\レポート\処理済み` | Codexが統合完了後に移動 |
| 保留 | `G:\マイドライブ\Claude保存\レポート\保留` | プロジェクト特定不能・要ユーザー確認のもの |

- 両PCでGoogle Drive同期済みのため、どちらのPCで作成したレポートも同じ受信箱に集まる。
- ローカル `G:` が参照できない場合は、Google Drive connector経由で受信箱を確認する。それも不可なら「未確認」として報告する。**単独の `Test-Path` 失敗を理由に、intake以外の通常作業を停止しない。**

## ファイル命名規則

```text
YYYY-MM-DD_<projectエイリアス>_<内容>.md
例: 2026-07-20_kakeibo_フェーズ3設計相談まとめ.md
```

- `<projectエイリアス>` は `PROJECTS.md` の `Alias` にある表記を使う。
- 同日同名の衝突時は末尾に `_2` を付ける。
- 元ファイル名を **Report-ID** として扱い、統合commitと `codex/work_log.md` の記録に必ず含める。

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

## 二重処理防止（Claim）

両PCのCodexが同じ受信箱を見るため、処理権は移動（claim）で確定する。

1. 統合を開始する前に、対象ファイルを受信箱から `処理中\<PC名>\` へ移動する。フォルダが無ければ作成する。
2. **移動に成功したインスタンスだけが処理権を持つ。** 移動に失敗した、またはファイルが既に受信箱に無い場合は、他インスタンスが処理中とみなして手を出さない。
3. 統合完了後、`処理中\<PC名>\` から処理済みへ移動する。
4. 処理中に中断した場合、ファイルは `処理中\<PC名>\` に残る。再開時は自PC名のフォルダ内のファイルを優先処理し、他PC名のフォルダには触れない。

## Codex側の統合手順

1. 発動条件（ユーザー明示指示または明示的intakeタスク）を確認してから受信箱を確認する。
2. 対象ファイルを `処理中\<PC名>\` へ移動してclaimする（上記Claim規則）。
3. レポートのProject欄を `PROJECTS.md` と照合し、対象repoを確定する。特定できない場合は保留へ移動し、ユーザーへ確認する。
4. **統合前に対象repoの既定branch、HEAD SHA、`AGENTS.md`、Primary Docsを読み、repo固有のbranch/PR規則・保存先規則があればそれを優先する。** `docs/reports/YYYY-MM-DD-<内容>.md` はrepo固有規則がない場合の既定である。
5. 反映先希望があればそれに従い、commit/pushする。commit messageにReport-ID（元ファイル名）を含める。
6. レポートが設計判断を含む場合は、対象repoの `DESIGN_LOG.md` に1行の参照（日付・タイトル・パス）を追記する。
7. Drive側のファイルを処理済みへ移動する。
8. `codex/work_log.md` に統合結果（Report-ID、対象repo、commit）を記録する。

commit反映まで完了しないうちにファイルを削除しない。GitHubへの反映が正本、Driveは経路である。レポートに秘密値が含まれていた場合は統合を停止し、該当箇所を（値を再掲せずに）報告する。

## CODEX_DESKTOP_STARTUP.md への追記文面（案）

以下を `codex/CODEX_DESKTOP_STARTUP.md` の適切な位置（Deliverable Storageの後など）へ追記する。

```markdown
## Claude Report Intake

Claude Desktopの作業レポートは `G:\マイドライブ\Claude保存\レポート\受信箱` に集まる。

- 受信箱の確認・統合は、ユーザーの明示指示または明示的なintakeタスクとしてのみ行う。通常タスクの開始時に自動確認しない。
- ローカル `G:` が見えない場合はGoogle Drive connector経由で確認し、単独の `Test-Path` 失敗を理由にintake以外の通常作業を停止しない。
- 処理開始時に対象ファイルを `処理中\<PC名>\` へ移動してclaimし、二重処理を防ぐ。移動できなかったファイルには手を出さない。
- 統合前に対象repoの既定branch、HEAD SHA、`AGENTS.md`、Primary Docsを読み、repo固有のbranch/PR・保存先規則を優先する。
- 統合完了（commit/push確認）までファイルを削除しない。処理後は処理済みへ移動し、`codex/work_log.md` にReport-IDとcommitを記録する。
- プロジェクトを特定できないレポートは保留へ移動し、ユーザーへ確認する。
- レポートに秘密値が含まれていた場合は統合を停止し、値を再掲せずに該当箇所を報告する。
- 詳細手順は `claude/REPORT_INTAKE.md` を正本とする。
```
