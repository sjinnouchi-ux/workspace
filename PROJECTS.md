# PROJECTS

Claude / Codexが、ユーザー発言から正しいプロジェクトを特定するためのオンライン正本です。

作業開始時はローカルフォルダ名を先に信頼せず、GitHub `main` 上のこのファイルを取得してください。`Alias` 列で表記ゆれを吸収し、該当行の `Canonical Entry` から対象Gitへ進みます。ここにない場合は、新規作成・凍結・既存フォルダへの割当を推測せず、ユーザーへ確認します。

Codex Desktop共通起動手順:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md
```

## 現役・移行中

| Project | Alias | Status | 設計 | 実装 | Canonical Entry | Primary Docs | Notes |
|---|---|---|---|---|---|---|---|
| 開発環境 | development-environment, Codex開発環境, Memory MCP, Claude監査 | Active | Codex Desktop | Codex Desktop | `https://github.com/sjinnouchi-ux/development-environment` | `AGENTS.md`; `README.md`; `docs/HANDOFF.md`; `docs/MIGRATION_MANIFEST.md`; `docs/claude-audit.md`; `docs/memory-mcp.md` | private repo。Codex Desktopを唯一のオーケストレーターとし、Windowsローカルの `development_memory` を補助知識、WSL2 Claude CLIを一回限りのread-only監査として使う。秘密値や生ログは保存しない。旧Shogun runtime/WebUI/GitHub repoは削除済みで、新規作業を配送しない。 |
| ENZAプロジェクト | ENZA, enza | Active / Setup | 未定 | 未定 | `https://github.com/sjinnouchi-ux/enza` | `AGENTS.md`; `README.md`; `PROJECT_BRIEF.md`; `IMPLEMENTATION_LOG.md` | private repo。プロジェクト専用Googleアカウントを使用し、全タスクでGoogle実作業前のログイン確認が必須。目的、要件、技術構成、設計・実装担当、Googleサービスの利用範囲は未確定。 |
| 税理士事務所DX | 税理士DX, zeirishi-office-dx | Active / Planning | 未定 | 未定 | `https://github.com/sjinnouchi-ux/zeirishi-office-dx` | `AGENTS.md`; `README.md`; `PROJECT_BRIEF.md`; `docs/secret-management.md`; `docs/multi-pc-integrations.md`; `docs/freee-access.md`; `docs/freee-mcp.md`; `docs/supabase-access.md`; `docs/box-receipt-source.md`; `docs/moneyforward-access.md`; `IMPLEMENTATION_LOG.md` | `yumekango.com` ではない別Googleアカウントを使用し、全タスクで実作業前のログイン確認が必須。アカウント識別子はprivate repoを正本とする。GCP project、Cloud Billing、Secret Managerを構築済み。freee公式Remote MCPはプロジェクト専用名でOAuth接続済みで、個人用freeeは流用禁止。freee自前API appのClient ID/SecretをSecret Managerへ登録済み。Money Forwardは39事業者を対象範囲として承認済みで、会計OAuth appのClient ID/SecretをSecret Managerへ登録し、公式Remote MCPも会計専用scopeで現PCのOAuth接続済み。他PCは同じscopeで個別OAuthとする。Boxはクライアント領収書スキャン受領元で、read-only API appのClient IDをSecret Managerへ登録済み。Client Secret、管理者承認、service account、対象folder権限はBox二段階認証待ち。領収書管理Supabase Projectは東京RegionのFree Planで、GitHub Actions Pythonの6時間keepaliveを実疎通済み。個別ファイル読取り、OCR、Box→Supabase/freee連携、領収書用テーブル・カラムは未設計・未実施。既存の別Supabase設定は流用禁止。その他の要件、対象業務、技術構成、設計・実装担当は未確定。 |
| SUUMOプロジェクト | SUUMO, スーモ, suumo-project | Active / Parent | Claude / Codex | Codex | `https://github.com/sjinnouchi-ux/suumo-project` | `AGENTS.md`; `README.md` | SUUMO関連派生プロジェクトの統括repo。個別実装は派生repoを正本とする。 |
| SUUMO 分析テスト開発 | SUUMO分析, スーモ分析, suumo-analysis-test, 分析テスト開発 | Active / Requirements | Claude / Codex | Codex | `https://github.com/sjinnouchi-ux/suumo-analysis-test` | `AGENTS.md`; `README.md`; `PROJECT_BRIEF.md`; `IMPLEMENTATION_LOG.md`; `docs/secret-management.md` | 博多駅登録58店舗のローカルPython収集 + Turso。Web UIは別フェーズ。 |
| 家計簿LIFF FastAPI化 | 家計簿, kakeibo, kakeibo-liff, yumekango-worker | Active / Pilot | Codex Desktop + WSL Fable 5 audit | Codex | `https://github.com/sjinnouchi-ux/kakeibo-liff` | `AGENTS.md`; `README.md`; `HANDOFF.md`; `DESIGN.md`; `IMPLEMENTATION_LOG.md`; `docs/secret-management.md` | Phase 3 Stage Aはmainへ反映済み。materialなFinance authority変更は固定WSL runnerによるFable 5の必須read-only監査を行うが、設計・改版・実装はCodex Desktopが担当する。Cloud Run runtimeはSecret Manager参照、Cloudflare deployは `kakeibo.deploy` roleから子process限定で取得する。共有Cloudflare tokenの用途別rotationは未完了。 |
| Kアラート本番開発 | Kアラート, K-alert, kalert, k-alert-production | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/k-alert-production` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md`; `docs/reports/2026-06-30-k-alert-production-current-status.md` | 本番運用あり。runtime secretとCloudflare deploy consumerは `ready`。専用Account API token、manifest、限定IAM、read/write/delete疎通を確認済み。共通tokenやWrangler OAuthへフォールバックしない。 |
| 台湾プロジェクト | 台湾, taiwan, taiwan-outreach, インバウンド | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/taiwan-outreach` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md`; `docs/work-log.md` | 看護守台湾向けLP/SNS/YouTube/GA4/Search Console。 |
| dori-manga | どり漫画, dori, どり看護師 | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/workspace/tree/main/dori-manga` | `dori-manga/CLAUDE.md`; `dori-manga/docs/work_log.md`; `dori-manga/docs/secret-management.md`; `dori-manga/docs/cloudflare-pages-deploy.md` | 独立repoではなく `workspace` 内の正本パス。空の同名ローカルGitを入口にしない。Cloudflare deployの新PC用manifest/IAM/helper経路は整備済み。専用Pages Edit tokenへのrotationまでは `ready_with_rotation_pending`。 |
| AI経営実装度診断WEBアプリ | 経営者AI診断, 経営者AI診断アプリ, AI経営診断, ai-keiei-shindan | Active | Claude / Opus 4.8 | Codex | `https://github.com/sjinnouchi-ux/workspace/tree/main/ai-keiei-shindan` | `ai-keiei-shindan/AGENTS.md`; `ai-keiei-shindan/PROJECT_BRIEF.md`; `ai-keiei-shindan/DESIGN_LOG.md`; `ai-keiei-shindan/IMPLEMENTATION_LOG.md` | GitHub Pages + GAS + Google Sheets。仕様書所在の確認が初回実装前の停止条件。 |
| 経営者労基診断アプリ開発 | 社長の労基認識, 社長の労基認識診断, 労基診断, 経営者労基診断, 労務リスク診断, keieisha-rouki-shindan | Active / Production | Claude / Codex | Codex | `https://github.com/sjinnouchi-ux/keieisha-rouki-shindan` | `AGENTS.md`; `README.md`; `PROJECT_BRIEF.md`; `IMPLEMENTATION_LOG.md`; `docs/reports/2026-07-16-production-status.md` | 15問の○×診断と3タイプ判定を行う通常Web MVP。本番公開済み。プロダクト仕様・画像は本repo、実行コード・本番設定は `k-alert-production` のmainが正本。3タイプ画像は暫定版。 |
| 看護守HP管理 | 看護守HP, kango-mamori, STUDIO, kango-mamori-studio-requests | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/kango-mamori-studio-requests` | `README.md`; `docs/site-overview.md`; `docs/studio-design-inventory.md`; `docs/change-history.md` | STUDIO修正、デザイン監査、GA4/Search Console、多言語展開を管理。台湾プロジェクトと関連するがHP運用の正本はこのrepo。 |
| 看護守ブログ記事作成 | 看護守ブログ, 看護守記事作成, 神社紹介記事 | Active / Workflow | Codex Desktop | Codex Desktop | `https://github.com/sjinnouchi-ux/kango-mamori-studio-requests` | `AGENTS.md`; `docs/blog-articles/README.md`; `docs/blog-articles/article-template.md`; `docs/blog-articles/studio-draft-checklist.md`; `docs/blog-articles/troubleshooting.md`; `docs/studio-article-workflow.md`; `docs/change-history.md` | private repo。1記事1 Issueで情報収集、原稿、必要時のみのFable 5 read-only監査、最終確認、STUDIO非公開下書きまでを管理する。公開はユーザーの明示承認後に限る。 |
| 管理ターミナル | management-terminal, mgmt-terminal, 管理モニター, APIモニター, api-monitor | Support / Workflow | Claude | Codex | `https://github.com/sjinnouchi-ux/mgmt-terminal` | `README.md`; `docs/MINIPC_PATROL_OPERATIONS.md`; `docs/DATABASE_SCHEMA.md`; `docs/PHASE_2_API_PROVIDER_USAGE_SYNC.md`; `docs/reports/2026-07-22-api-monitor-integration-closeout.md`; `docs/superpowers/specs/2026-07-15-finance-foundation-design.md`; `docs/superpowers/plans/2026-07-15-finance-foundation-roadmap.md`; `docs/reports/2026-07-15-finance-core-implementation-log.md` | API Monitorのprovider同期・費用表示・LLM単価・監査を統合済み。独立API Monitorは履歴参照。2026-07-06の設計相談メモ・引継ぎメモは履歴資料。Migration 1のlinked Supabase適用状態は実装ログを正本とし、Migration 2AまではHTTP/API権限を変更しない。MiniPC常設巡回の完成仕様・運用入口は `docs/MINIPC_PATROL_OPERATIONS.md`。 |
| 議事録システム | meeting-minutes, 議事録 | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/meeting-minutes-system` | `AGENTS.md`; `README.md`; `docs/secret-management.md` | リアルタイム文字起こし、Google Docs/Calendar出力、DB/API参照チャット。OpenAI資格情報はSecret Managerのruntime roleから子process限定で取得し、ローカルJSONへ保存しない。Google OAuthは各PCで再認証し、認証ファイルをコピーしない。 |
| ゆめ看護 事業管理 | yumekango-business-management, 看護守事業, 事業振り返り | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/yumekango-business-management` | `README.md` | 事業全体管理、月次振り返り、KPI、派生プロジェクト連携。 |

## 凍結・参照

| Project | Alias | Status | Frozen/Completed Date | Canonical Entry | Primary Docs | Notes |
|---|---|---|---|---|---|---|
| market-pilot | market, 株, ETF, 売買シグナル | Frozen | 2026-07-01 | `https://github.com/sjinnouchi-ux/market-pilot` | `AGENTS.md`; `README.md` | 保守も原則停止。再開時はユーザー確認後にActiveへ戻す。 |
| API Monitor（独立版） | 旧API Monitor, legacy-api-monitor | Merged / Legacy | 2026-07-22 | `https://github.com/sjinnouchi-ux/api-monitor` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md`; `docs/secret-management.md` | 現役機能は管理ターミナルへ統合済み。旧Windows Streamlit、SQLite、provider同期実装、移行履歴の参照用として保持する。GitHub repoのarchiveとlegacy secret/IAM cleanupは別承認。 |
| Kアラート・テスト開発 | k-alert-test, Kアラートテスト | Archived / Legacy | 2026-07-09 | なし | なし | 過去にテスト版が存在したことだけを残す。現行はKアラート本番開発を参照。 |
| code-exchange | Claude Desktop, CLI橋渡し | Frozen / Legacy | 2026-07-01 | `https://github.com/sjinnouchi-ux/workspace/tree/main/code-exchange` | `code-exchange/README.md` | 旧Desktop/CLI橋渡しは廃止。現行のClaude read-only監査は `development-environment` を参照する。 |
| Shogun | Shogun Lab, multi-agent-shogun, FABLE5, 要件定義 | Deleted | 2026-08-11 | `https://github.com/sjinnouchi-ux/development-environment` | `docs/HANDOFF.md`; `docs/MIGRATION_MANIFEST.md` | 旧 `multi-agent-shogun` GitHub repo、WSL2 runtime、固定Ops/diagnosticsは削除済み。新規taskを配送せず、移行・削除記録は開発環境repoを正本とする。 |
| Shogun WEBUI | Shogun Web UI, shogun-webui, Shogun管理画面 | Deleted | 2026-08-11 | `https://github.com/sjinnouchi-ux/development-environment` | `docs/HANDOFF.md`; `docs/MIGRATION_MANIFEST.md` | 旧 `shogun-webui` GitHub repo、WebUI、管理モニター、Streamlit資産は削除済み。再起動・再配備せず、移行・削除記録は開発環境repoを正本とする。 |
| supabase-db-templates | Supabaseテンプレート | Archived / Reference | 2026-06-06 | `https://github.com/sjinnouchi-ux/supabase-db-templates` | `README.md` | 参照用。dori-manga資産は置かず、workspace内の正本を使う。 |

## 共通・補助入口

| Area | Canonical Entry | Role |
|---|---|---|
| Codex Desktop運用 | `https://github.com/sjinnouchi-ux/workspace/tree/main/codex` | 共通起動手順、パーソナライズ文面、Windowsセットアップ、作業ログ |
| 共通ワークフロー | `https://github.com/sjinnouchi-ux/workspace/tree/main/docs` | 設計/実装分担、横断資料 |
| 会社共通設定 | `https://github.com/sjinnouchi-ux/workspace/tree/main/company-settings` | GA4 / Google Ads等の参照資料 |
| 旧家計簿Worker/GAS | `https://github.com/sjinnouchi-ux/workspace/tree/main/yumekango-worker` | 家計簿LIFF FastAPI化の既存実装参照。新規プロジェクトとして分離しない |
| 開発環境・Claude監査・Memory MCP | `https://github.com/sjinnouchi-ux/development-environment` | Codex Desktop運用、WindowsローカルMemory MCP、WSL2 Claude read-only監査の正本 |

## 記入ルール

- `Canonical Entry` は別PCから到達できる完全なGitHub URLを書く。
- 日付は `YYYY-MM-DD`（JST）。未確認なら空欄にする。
- 未登録のローカルフォルダや空Gitを、既存プロジェクトへ推測で割り当てない。
- 退役済みのShogunローカル設定、旧runtime、旧repoを正本または作業入口にしない。
- プロジェクト固有の最新状態は、Canonical Entryの既定ブランチとPrimary Docsで確認する。
