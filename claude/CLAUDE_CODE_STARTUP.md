# Claude Code Startup

## Role

この文書は、Claude Codeがプロジェクト作業を始める際のオンライン正本です。ローカルclone、過去セッション、メモリ、フォルダ名より先に、GitHub `main` 上のこの文書と `PROJECTS.md` を確認します。

Canonical URLs:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/claude/CLAUDE_CODE_STARTUP.md
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/PROJECTS.md
```

Codex側の対称文書: `codex/CODEX_DESKTOP_STARTUP.md`

## Execution Surfaces

Claude Codeの実行面は次の2つに限定する。各PCへのClaude Code個別インストールは行わない。

| 面 | 実体 | 用途 |
|---|---|---|
| クラウドセッション | Claude Code on the web（claude.ai/code、環境定義 `yumekango-standard`） | 設計・調査・レビュー、軽微なPR作業。デスクトップPC・ノートPC・スマホから同一セッションを継続できる共有作業場 |
| Shogun配下のClaude CLI | MiniPC `NUCBOX_K8_PLUS` のWSL2 `Ubuntu` | Shogunの `config/settings.yaml` でClaude割当となっている役職の作業 |

- クラウドセッションのVMはセッション単位の使い捨てである。永続するのは環境定義・セッション履歴・GitHubへpushした成果だけ。
- 予備経路: クラウドセッションは `claude --teleport` でローカル端末へ引き込める。恒常運用にはせず、障害時・特殊作業時のみ使う。
- Claude Desktopアプリは本書の対象外。Desktopの成果は作業レポートとして `claude/REPORT_INTAKE.md` の受渡経路に従い、Codexが各repoへ統合する。

## Startup Order

1. GitHub `sjinnouchi-ux/workspace` の `main` を取得し、この文書と `PROJECTS.md` を読む。
2. 取得に使った `workspace` のcommit SHAを確認する。
3. ユーザーの表現を `PROJECTS.md` の `Alias` と照合し、Canonical Entryを確定する。
4. 対象Gitの既定ブランチを取得し、repoの `CLAUDE.md` / `AGENTS.md` があれば最初に読む。
5. `PROJECTS.md` のPrimary Docsを読み、現在状態と作業範囲を確定する。
6. クラウドセッションでは、セッション作成時にcloneされたrepoが対象repoと一致しているかを確認する。

URL取得、GitHub認証、対象プロジェクト特定のいずれかに失敗した場合は、推測で作業せず、停止して不足している接続または登録を報告します。未登録プロジェクトは新規作成も凍結扱いもせず、ユーザーへ確認します。

## Role Split With Codex

- Claude Codeの主担当: 要件定義、仕様整理、設計判断、レビュー、調査。結果は各プロジェクトの `DESIGN_LOG.md`、`docs/requirements/`、`docs/specs/` に残す。
- 実装・検証・デプロイの既定担当はCodex。Codexへの実装依頼は `docs/workflow-design-implementation.md` のテンプレートに従う。
- クラウドセッションでの実装は、ユーザーが明示的に指示した軽微な範囲（ドキュメント、設定、小規模修正）に限り、PR作成までを担当する。deployとlive反映は行わない。
- 同一タスクをCodex・Shogunと並行して実装しない。着手前に `IMPLEMENTATION_LOG.md` と未クローズPRで進行中作業がないことを確認する。
- 設計と実装の食い違いは `Questions Back To Design` の仕組みをそのまま使う。

## Branch And PR Discipline

- 既定ブランチ（`main`）へ直接pushしない。作業は `claude/<topic>` 形式の専用branchで行い、PRを作成する。
- PRのマージ判断はユーザーまたはCodex側の既存規則に従う。
- クラウドセッションのcommitに付く `Claude-Session:` トレーラーとPR本文のセッションURLは削除しない（トレーサビリティ確保）。

## Cleanup Gate

クラウドセッションのVMはセッション終了・失効で消える。次を確認するまで作業を完了と報告しない。

- 必要な変更がcommit済みで、専用branchとしてremoteへpush済み
- PR作成済み、またはpush済みbranch名を報告済み
- 必要な作業ログ（`DESIGN_LOG.md` 等）をGitHubへ反映済み
- VM内にだけ存在する未push成果物がない

push できない状態で終了せざるを得ない場合は、未保存の対象と理由を明示して報告します。

## GitHub Access

- GitHub owner/account: `sjinnouchi-ux`
- `s.jinnouchi@yumekango.com` はGoogle業務用アカウントであり、GitHub owner名ではない。
- クラウドセッションのGitHub認証はClaude GitHub App承認（またはGitHub proxy）による。token値を表示・保存しない。
- `gh` はセットアップスクリプトで導入済み（`claude/CLOUD_ENVIRONMENT.md` 参照）。`GH_TOKEN` が `proxy-injected` の場合はproxyが認証を代行している正常状態であり、実tokenの取得を試みない。

## Secrets And Accounts

- 秘密値、OAuthコード、token、認証JSON、`.env` の中身をチャット、Markdown、GitHub、環境定義へ表示・保存しない。
- クラウド環境定義（環境変数・セットアップスクリプト）には秘密値を置かない。専用secretsストアが提供されるまで、秘密値が必要な作業はクラウドセッションで行わない。
- project repoのsecret管理文書（`docs/secret-management.md`）の規則を優先する。Secret Manager正本のrepoでは実値へアクセスせず、必要ならCodex側の作業として返す。
- Google業務操作は、ユーザーが別指定しない限り `s.jinnouchi@yumekango.com` を使う。

## Shogun Boundary

- クラウドセッションはShogun runtime（tmux session、queue、`config/settings.yaml`、reports、logs）へアクセスできず、アクセスを試みない。
- Shogun配下のClaude CLIはShogun側の運用規則（`multi-agent-shogun` repo）を正本とし、本書はStartup Order・Role Split・Secretsの共通原則だけを適用する。
- Shogunへのtask配送はCodex側の `CODEX_SHOGUN_TASK_INTAKE_V1` が正本であり、Claude Codeは代行しない。

## Per-Project CLAUDE.md

- 各プロジェクトrepoの直下に `CLAUDE.md`（内容は `@AGENTS.md` の1行）を置き、既存の `AGENTS.md` をClaude Codeにも読ませる。二重管理しない。
- `workspace` 直下はREADMEの方針（Shogun自動生成ルートCLAUDE.mdを手書き正本にしない）に従い対象外。
- クラウドセッションには各PCの `~/.claude` 設定が引き継がれない仕様のため、プロジェクト固有ルールは必ずrepo側の `CLAUDE.md` / `AGENTS.md` / `.claude/settings.json` に置く。

## Reporting

- 確認済み事実だけを報告する。
- 実行面（クラウドセッション / Shogun配下CLI）、GitHub URL、branch、commit、PR、変更ファイルを可能な範囲で含める。
- GitHub反映前、PRのみ、`main` 反映済みを区別する。deployment/live反映はClaude Codeの担当外であり、必要ならCodexへの依頼事項として明記する。
- 未完了または未同期の項目は、対象と理由を明示する。
