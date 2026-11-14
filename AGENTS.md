# エージェントの作業指示

既存のプロジェクト文書と作業範囲を確認してから変更する。

## 承認と本人操作

[承認・本人操作・継続方針](codex/AGENT_APPROVAL_POLICY.md)に従う。具体的に承認済みの作業はCodexが検証・報告まで進め、repo独自の記述だけを理由に本人PC操作や重複承認を要求しない。必要な追加承認は可能ならチャットで受ける。上位のツール規則による必須確認・本人操作、認証・権限・秘密保護・重複防止・読戻しは維持する。

## GitHub Actions・検証コストの共通ルール

- 途中の確認は変更範囲に絞り、重い全体テストは統合前に行う。
- 文書・作業記録だけの変更では、原則として重いテストを起動しない。
- 同じコードで成功済みの検証は、新しい変更や失敗調査の必要がなければ繰り返さない。
- テストを省略した場合は、理由と統合前に必要な検証を明記する。
- DB変更は、スキーマ・権限・データ整合性への影響に応じた検証を残す。
- 定期監視・休止防止・本番配備は、テスト削減と混同して停止しない。
- 予算・課金上限は、利用者の明示指示なしに変更しない。

作業開始時に[共通方針](https://github.com/sjinnouchi-ux/workspace/blob/main/codex/GITHUB_ACTIONS_POLICY.md)も読む。必須チェック・既存の承認ルールは維持する。検証済み結果を再利用する場合は対象commit・検証範囲・結果を確認し、今回の変更に適用できることを示す。

## Memory MCP の活用

GitHubの共通起動手順と台帳でCanonical Entryを確定し、対象repoの既定ブランチ・AGENTS.md・Primary Docsを確認する。その後、このWindows端末に設定された `development_memory` をCanonical repo名とcomponent名で検索する。関連する既知の失敗は、症状・原因・修正・証拠を読み、今回の環境にも当てはまる場合に活用する。GitHubと食い違う場合はGitHubを優先し、MCPが使えない場合や該当0件の場合もGitHub正本で作業を続ける。

原因が確定し、修正後の検証に通った再利用可能な失敗だけを `VerifiedFailurePattern` として記録する。端末、repoまたは共通領域、component、匿名化した症状、原因、修正、証拠（commit・PR・テスト結果など）、検証日を残す。同じパターンには既存項目へ検証結果を追記する。秘密値・認証情報・個人情報・生ログ・会話全文は保存しない。

[端末別のMemory MCP運用手順](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/memory-mcp.md)
