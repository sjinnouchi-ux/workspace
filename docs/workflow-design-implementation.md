# 設計・実装・監査の分担

Codex Desktopを唯一のオーケストレーターとします。旧Shogunの役職・CLI割当やconfigを現行の権限・手順として使用しません。

## 責務

| 担当 | 役割と境界 |
|---|---|
| 利用者 | 目的、採用範囲、業務判断、必要な公開・配備・権限変更の承認を判断する |
| Codex Desktop | 要件確認、設計、実装、検証、GitHub反映、結果確認を担当する。承認済み範囲は[共通方針](../codex/AGENT_APPROVAL_POLICY.md)に従って進める |
| Windows Memory MCP | GitHub正本確認後の補助知識。host/repo/componentを限定し、原因・修正・検証が確定した再利用可能な失敗だけを記録する |
| WSL2 Claude CLI | 利用者が監査を求めた場合だけ固定runnerでread-only監査する。設計著者、実装者、task配送先、常設workerとして使用しない |

監査のexact commit、モデル、認証、receipt、no retry/no fallbackは[開発環境の監査契約](https://github.com/sjinnouchi-ux/development-environment/blob/main/docs/claude-audit.md)を確認します。repo固有の監査gateを守り、過去の監査を別変更の承認へ流用しません。subagentは利用者の選択・明示依頼に従います。

## 正本と保存先

- 全体ルーティングは[PROJECTS.md](../PROJECTS.md)、共通Codex運用は[起動手順](../codex/CODEX_DESKTOP_STARTUP.md)。
- 詳細設計、コード、実装ログ、受入証拠は対象Canonical repo。DESIGN_LOGやIMPLEMENTATION_LOGは経緯、spec/runbookは現在有効な契約を扱う。
- repo source、配備artifact、live観測、本人端末受入を分けて記録する。
- taskの会話、Memory、ローカルclone、旧queue/pane/reportをGitHub正本の代わりにしない。
- 必要な成果物と匿名化ログを保存し、固定commitから読戻した後にタスク作業場を整理する。詳細は[Git Handoff Protocol](../GIT_HANDOFF_PROTOCOL.md)。

## 作業の流れ

1. オンライン正本と現行状態を確認し、目的、対象、変更しない境界を確定する。
2. Codexが設計・必要差分を準備し、既承認の範囲を実装する。追加の判断が必要な場合は具体化して利用者へ提示する。
3. [Actions方針](../codex/GITHUB_ACTIONS_POLICY.md)に従い、影響に合う検証を行う。過去成功を再利用するときは固定sourceと適用範囲を確認する。
4. GitHubへ必要変更と作業ログを反映し、source・検証・配備・未完条件を分けて確認する。

## 作業依頼に含める情報

- Canonical repo / 対象component
- 背景、目的、対象scope、対象外
- 参照する固定commit・仕様・既存証拠
- 受入条件、必要な検証、公開・配備・業務書込みの有無
- 結果不明時の照会方法と、必要な場合の切り戻し条件

旧本文の正確な所在・blobは[整理manifest](history/workspace-pr-cleanup-2026-11-13/manifest.json)へ保存しています。旧構成へ戻すための手順ではありません。
