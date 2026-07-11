# PROJECTS

Claude / Codex / 将来のShogun実行環境が、ユーザー発言から正しいプロジェクトを特定するためのオンライン正本です。

作業開始時はローカルフォルダ名を先に信頼せず、GitHub `main` 上のこのファイルを取得してください。`Alias` 列で表記ゆれを吸収し、該当行の `Canonical Entry` から対象Gitへ進みます。ここにない場合は、新規作成・凍結・既存フォルダへの割当を推測せず、ユーザーへ確認します。

Codex Desktop共通起動手順:

```text
https://raw.githubusercontent.com/sjinnouchi-ux/workspace/main/codex/CODEX_DESKTOP_STARTUP.md
```

## 現役・移行中

| Project | Alias | Status | 設計 | 実装 | Canonical Entry | Primary Docs | Notes |
|---|---|---|---|---|---|---|---|
| 家計簿LIFF FastAPI化 | 家計簿, kakeibo, kakeibo-liff, yumekango-worker | Active / Pilot | FABLE 5 / Claude | Codex | `https://github.com/sjinnouchi-ux/kakeibo-liff` | `README.md`; `HANDOFF.md`; `DESIGN.md`; `IMPLEMENTATION_LOG.md` | Phase 1はremote branch `codex/phase-1-fastapi-worker` にあり、既存LIFF/GAS/Workerを段階的にFastAPI化する。Cloud Run runtime secretはSecret Manager参照済みだが、Cloudflare deployの新PC用manifest/IAMは未整備。 |
| Kアラート本番開発 | Kアラート, K-alert, kalert, k-alert-production | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/k-alert-production` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md`; `docs/reports/2026-06-30-k-alert-production-current-status.md` | 本番運用あり。Cloud Run / Cloudflare Worker / GAS / Supabase。runtime secretはSecret Manager/Worker storeで確認済み。Cloudflare deployの新PC用manifestは未整備。 |
| 台湾プロジェクト | 台湾, taiwan, taiwan-outreach, インバウンド | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/taiwan-outreach` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md`; `docs/work-log.md` | 看護守台湾向けLP/SNS/YouTube/GA4/Search Console。 |
| dori-manga | どり漫画, dori, どり看護師 | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/workspace/tree/main/dori-manga` | `dori-manga/CLAUDE.md`; `dori-manga/docs/work_log.md`; `dori-manga/docs/secret-management.md`; `dori-manga/docs/cloudflare-pages-deploy.md` | 独立repoではなく `workspace` 内の正本パス。空の同名ローカルGitを入口にしない。Cloudflare deployの新PC用manifest/IAM/helper経路は整備済み。専用Pages Edit tokenへのrotationまでは `ready_with_rotation_pending`。 |
| API Monitor | APIモニター, api-monitor | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/api-monitor` | `AGENTS.md`; `PROJECT_BRIEF.md`; `DESIGN_LOG.md`; `IMPLEMENTATION_LOG.md` | 独立プロジェクトGitへ移行済み。現行 `run_windows.ps1` は旧 `global.env` を直接読むため、新PCのSecret Manager consumer移行前は実行を停止する。 |
| AI経営実装度診断WEBアプリ | 経営者AI診断, 経営者AI診断アプリ, AI経営診断, ai-keiei-shindan | Active | Claude / Opus 4.8 | Codex | `https://github.com/sjinnouchi-ux/workspace/tree/main/ai-keiei-shindan` | `ai-keiei-shindan/AGENTS.md`; `ai-keiei-shindan/PROJECT_BRIEF.md`; `ai-keiei-shindan/DESIGN_LOG.md`; `ai-keiei-shindan/IMPLEMENTATION_LOG.md` | GitHub Pages + GAS + Google Sheets。仕様書所在の確認が初回実装前の停止条件。 |
| 看護守HP管理 | 看護守HP, kango-mamori, STUDIO, kango-mamori-studio-requests | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/kango-mamori-studio-requests` | `README.md`; `docs/site-overview.md`; `docs/studio-design-inventory.md`; `docs/change-history.md` | STUDIO修正、デザイン監査、GA4/Search Console、多言語展開を管理。台湾プロジェクトと関連するがHP運用の正本はこのrepo。 |
| 管理ターミナル | management-terminal, mgmt-terminal | Support / Workflow | Claude | Codex | `https://github.com/sjinnouchi-ux/mgmt-terminal` | `2026-07-06-management-terminal-design-brief.md`; `2026-07-06-management-terminal-opus-handoff.md` | 管理ターミナルAPI・運用資料。 |
| 議事録システム | meeting-minutes, 議事録 | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/meeting-minutes-system` | `README.md` | リアルタイム文字起こし、Google Docs/Calendar出力、DB/API参照チャット。API keyは現行ローカルJSON保存で、Secret Manager consumer未移行。Google OAuthは各PCで再認証し、tokenファイルをコピーしない。 |
| ゆめ看護 事業管理 | yumekango-business-management, 看護守事業, 事業振り返り | Active | Claude | Codex | `https://github.com/sjinnouchi-ux/yumekango-business-management` | `README.md` | 事業全体管理、月次振り返り、KPI、派生プロジェクト連携。 |
| Shogun | Shogun Lab, multi-agent-shogun, FABLE5, 要件定義 | Support / Workflow | FABLE 5 / Claude | Shogun / Codex | `https://github.com/sjinnouchi-ux/multi-agent-shogun` | `README_ja.md`; `AGENTS.md`; `CLAUDE.md` | WSL2 Linux + WebUI上でGitHub境界連携方式として独立運用する。専用branchを使用してmainへ直接pushせず、対象repoの既存規則を優先する。Codex Desktopの設定・認証・session・worktree/cleanup方式・Drive領域は共有しない。実装方針はv1.1 lightweight approved。 |

## 凍結・参照

| Project | Alias | Status | Frozen/Completed Date | Canonical Entry | Primary Docs | Notes |
|---|---|---|---|---|---|---|
| market-pilot | market, 株, ETF, 売買シグナル | Frozen | 2026-07-01 | `https://github.com/sjinnouchi-ux/market-pilot` | `AGENTS.md`; `README.md` | 保守も原則停止。再開時はユーザー確認後にActiveへ戻す。 |
| Kアラート・テスト開発 | k-alert-test, Kアラートテスト | Archived / Legacy | 2026-07-09 | なし | なし | 過去にテスト版が存在したことだけを残す。現行はKアラート本番開発を参照。 |
| code-exchange | Claude Desktop, CLI橋渡し | Frozen / Legacy | 2026-07-01 | `https://github.com/sjinnouchi-ux/workspace/tree/main/code-exchange` | `code-exchange/README.md` | Shogun集約方針により旧Desktop/CLI橋渡しは廃止。 |
| supabase-db-templates | Supabaseテンプレート | Archived / Reference | 2026-06-06 | `https://github.com/sjinnouchi-ux/supabase-db-templates` | `README.md` | 参照用。dori-manga資産は置かず、workspace内の正本を使う。 |

## 共通・補助入口

| Area | Canonical Entry | Role |
|---|---|---|
| Codex Desktop運用 | `https://github.com/sjinnouchi-ux/workspace/tree/main/codex` | 共通起動手順、パーソナライズ文面、Windowsセットアップ、作業ログ |
| 共通ワークフロー | `https://github.com/sjinnouchi-ux/workspace/tree/main/docs` | 設計/実装分担、横断資料 |
| 会社共通設定 | `https://github.com/sjinnouchi-ux/workspace/tree/main/company-settings` | GA4 / Google Ads等の参照資料 |
| 旧家計簿Worker/GAS | `https://github.com/sjinnouchi-ux/workspace/tree/main/yumekango-worker` | 家計簿LIFF FastAPI化の既存実装参照。新規プロジェクトとして分離しない |
| Shogun-Codex中継資料 | `https://github.com/sjinnouchi-ux/workspace/tree/main/shogun-lab` | 将来のWSL2/WebUI改修まで中継資料として保持 |

## 記入ルール

- `Canonical Entry` は別PCから到達できる完全なGitHub URLを書く。
- 日付は `YYYY-MM-DD`（JST）。未確認なら空欄にする。
- 未登録のローカルフォルダや空Gitを、既存プロジェクトへ推測で割り当てない。
- Shogunのローカル設定や `projects/{name}.yaml` はこの表の従属物とし、正本にしない。
- プロジェクト固有の最新状態は、Canonical Entryの既定ブランチとPrimary Docsで確認する。
