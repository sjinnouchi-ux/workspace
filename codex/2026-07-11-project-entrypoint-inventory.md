# Project Entrypoint Inventory - 2026-07-11

## Purpose

Codex Desktopで複数PCから同じプロジェクトへ到達できるように、GitHub上の正本、WindowsローカルのGit入口、Codexの信頼済みパス、`AGENTS.md`の読込構造を棚卸しした。

この文書は2026-07-11 JST時点の確認結果である。削除、移動、未同期ファイルの統合、ブランチのマージは実施していない。

Shogun関連はユーザー指定により別デスクトップで扱う。この棚卸しでは存在だけを記録し、内容変更や整理対象にはしていない。

## Confirmed Operating Model

- GitHubの各リポジトリと既定ブランチを永続的な正本とする。
- ローカルclone/worktreeは作業場であり、タスク完了後に削除可能な状態を目標とする。
- 削除前に、未コミット変更、未pushコミット、ローカル専用ログ、成果物、本番確認の残りがないことを確認する。
- プロジェクト一覧の正本は `sjinnouchi-ux/workspace` の `PROJECTS.md` とする。
- ローカルフォルダ名だけでプロジェクトを決定しない。`PROJECTS.md` のGitHub URLまたはリポジトリ内パスを先に確定する。

## Codex Automatic Instruction Entry

OpenAI公式仕様では、Codexは各runの開始時に次の順序で指示を構成する。

1. Codex homeの `AGENTS.override.md`。なければ `AGENTS.md`。
2. プロジェクトルートから現在の作業ディレクトリまでの `AGENTS.override.md` / `AGENTS.md`。
3. 現在の作業ディレクトリに近い指示ほど後から結合され、上位の指示を上書きできる。

公式資料: https://developers.openai.com/codex/guides/agents-md/

このPCの確認結果:

| Item | Confirmed state |
|---|---|
| Effective Codex home | `C:\Users\irodo\.codex` (`CODEX_HOME`未設定) |
| Global instruction | `C:\Users\irodo\.codex\AGENTS.md` |
| Global override | なし |
| Global AGENTS SHA-256 | `75E789917863183CE856976FC0C0E08E5193D24FB76E64130686094CAE43234A` |
| Global AGENTS size | 5,595 bytes |
| Codex config | `C:\Users\irodo\.codex\config.toml` |

したがって、各PCで共通運用を開始させる入口は `~/.codex/AGENTS.md` でよい。ただし、このローカルファイル自体はGitHub正本ではなく、このPCでは自動同期設定も確認できなかった。また、リポジトリ側の `AGENTS.md` が後から適用される。全PC統一には次の2段階が必要である。

- GitHubにグローバル `AGENTS.md` の正本テンプレートを置く。
- 各PCの `~/.codex/AGENTS.md` へ同じテンプレートを配布し、プロジェクト固有ルールは各リポジトリの `AGENTS.md` に限定する。

プロジェクト一覧そのものを各PCのグローバル `AGENTS.md` に複製すると古くなるため、グローバル指示にはGitHub上の `PROJECTS.md` を先に確認する規則だけを置く。

## GitHub Repository Inventory

GitHubアカウント `sjinnouchi-ux` で12リポジトリを確認した。すべて既定ブランチは `main`、GitHub上の `archived` は `false` だった。

| Repository | Visibility | Registry state | Root entry files | Classification |
|---|---|---|---|---|
| `api-monitor` | Private | `PROJECTS.md`登録済み | `AGENTS.md`, `README.md`, `PROJECT_BRIEF.md`, `DESIGN_LOG.md`, `IMPLEMENTATION_LOG.md` | Active |
| `k-alert-production` | Private | 登録済み | `AGENTS.md`, `README.md`, `PROJECT_BRIEF.md`, `DESIGN_LOG.md`, `IMPLEMENTATION_LOG.md` | Active |
| `kakeibo-liff` | Private | 登録済み | `README.md`, `IMPLEMENTATION_LOG.md`, `DESIGN.md`, `HANDOFF.md` | Active / Pilot。標準入口ファイルが一部不足 |
| `kango-mamori-studio-requests` | Private | `PROJECTS.md`未登録 | `README.md`のみ | 要分類 |
| `market-pilot` | Private | Frozen登録済み | `AGENTS.md`, `README.md` | Frozen。ただしGitHub archive未設定 |
| `meeting-minutes-system` | Private | 登録済み | `README.md`のみ | Active。標準入口ファイル不足 |
| `mgmt-terminal` | Private | `PROJECTS.md`未登録 | ルート入口ファイルなし | Active実体あり。台帳登録と入口整備が必要 |
| `multi-agent-shogun` | Public | `PROJECTS.md`には `shogun-lab/` のみ | `AGENTS.md`, `README.md`, `CLAUDE.md` | Shogun対象外 |
| `supabase-db-templates` | Private | 現行 `PROJECTS.md`未登録 | `README.md`のみ | 旧CSVではArchived / Reference |
| `taiwan-outreach` | Private | 登録済み | `AGENTS.md`, `README.md`, `PROJECT_BRIEF.md`, `DESIGN_LOG.md`, `IMPLEMENTATION_LOG.md` | Active |
| `workspace` | Public | 全体ルーター | `README.md`, `PROJECTS.md`, `MCP.md` | Cross-project registry |
| `yumekango-business-management` | Private | 登録済み | `README.md`のみ | Active。標準入口ファイル不足 |

GitHub URLs:

- https://github.com/sjinnouchi-ux/api-monitor
- https://github.com/sjinnouchi-ux/k-alert-production
- https://github.com/sjinnouchi-ux/kakeibo-liff
- https://github.com/sjinnouchi-ux/kango-mamori-studio-requests
- https://github.com/sjinnouchi-ux/market-pilot
- https://github.com/sjinnouchi-ux/meeting-minutes-system
- https://github.com/sjinnouchi-ux/mgmt-terminal
- https://github.com/sjinnouchi-ux/multi-agent-shogun
- https://github.com/sjinnouchi-ux/supabase-db-templates
- https://github.com/sjinnouchi-ux/taiwan-outreach
- https://github.com/sjinnouchi-ux/workspace
- https://github.com/sjinnouchi-ux/yumekango-business-management

## Workspace Registry Findings

現行 `PROJECTS.md` は9件の現役・移行中プロジェクトと3件の凍結・完了プロジェクトを持つ。

確認した問題:

- `dori-manga` の入口が `dori-manga/` という相対パスで、別PCからはリポジトリを特定しにくい。正本は `https://github.com/sjinnouchi-ux/workspace/tree/main/dori-manga`。
- `ai-keiei-shindan/` と `code-exchange/` も相対パスである。workspace内であることをURLで明示する余地がある。
- `mgmt-terminal`、`kango-mamori-studio-requests`、`supabase-db-templates` はGitHubに存在するが、現行 `PROJECTS.md` に行がない。
- `docs/notion/projects.csv` は旧管理面であり、現行 `PROJECTS.md` と状態が一致しない。例として `market-pilot` は旧CSVでActive、現行台帳でFrozenになっている。
- workspace内には台帳対象以外に `company-settings/`、`codex/`、`docs/`、`yumekango-worker/` がある。プロジェクト、共通資料、旧実装のどれとして扱うかを台帳で明示する必要がある。

Shogun関連の `multi-agent-shogun`、`shogun-lab/`、Shogun移行を理由とする `code-exchange/` は今回の整備対象から除外する。

## Local Git Inventory

検索範囲は `C:\Users\irodo\Documents` と `C:\tools`。22個の成立したGitルートを確認し、remoteがあるものは `git fetch origin --prune` 後に比較した。

| Local path under `C:\Users\irodo\Documents` | Origin / branch | State after fetch | Classification |
|---|---|---|---|
| `APIモニター` | remoteなし / unborn `master` | commitなし、clean | 危険入口。正本repoと無関係 |
| `Codex\2026-06-03\mac-github\workspace` | `workspace` / `main` | 131 behind、14 deleted | 退役候補。削除表示は現在のoriginでも削除済み |
| `Codex\2026-06-06\github-github-claude-codex-md-github\work\repos\sjinnouchi-ux__market-pilot` | `market-pilot` / `main` | 同期、clean | Frozen clone |
| `Codex\2026-06-06\github-github-claude-codex-md-github\work\repos\sjinnouchi-ux__supabase-db-templates` | `supabase-db-templates` / `main` | 同期、clean | Reference clone |
| `Codex\2026-06-06\github-github-claude-codex-md-github\work\repos\sjinnouchi-ux__workspace` | `workspace` / `main` | 114 behind、3 local differences | 要救出。ローカル固有Markdownあり |
| `Codex\2026-06-07\liff-k-notion-github-k-line\work\repos\workspace` | `workspace` / `main` | 99 behind、clean | 退役候補 |
| `Codex\2026-06-08\github-notion\work\repos\sjinnouchi-ux__workspace` | `workspace` / `main` | origin/mainと同期、clean | 現在の一時作業場 |
| `Codex\2026-06-08\github-notion\work\repos\sjinnouchi-ux__workspace\api-monitor` | `api-monitor` / `main` | origin/mainと同期、clean | 正しい内容だが入れ子の一時clone |
| `Codex\2026-06-08\github-notion\work\repos\sjinnouchi-ux__yumekango-business-management` | `yumekango-business-management` / `main` | 1 behind、clean | 重複・退役候補 |
| `Freee` | remoteなし / unborn `master` | commitなし、clean | 未登録の危険入口。用途確認が必要 |
| `kakeibo-liff` | `kakeibo-liff` / `codex/phase-1-fastapi-worker` | remote branchと同期、clean | 有効作業場。ただしHEADはmainに未統合の1 commitを含む |
| `k-alert-production-workspace-push` | `workspace` / `codex/k-alert-production-cloud-run` | origin/mainより60 behind、1 unique commit | 要照合。削除禁止 |
| `Kアラート` | remoteなし / unborn `master` | commitなし、clean | 危険入口。正本は `k-alert-production` |
| `Kアラート・テスト開発` | remoteなし / unborn `master` | commitなし、`.wrangler/` と `outputs/` が未追跡 | Archived入口。生成物確認前は削除禁止 |
| `Kアラート・本番開発` | `k-alert-production` / `main` | origin/mainと同期、clean | 有効な安定clone |
| `workspace` | `workspace` / `main` | 4 behind、clean | 安定入口候補。更新が必要 |
| `どり看護師マンガプロジェクト` | remoteなし / unborn `master` | commitなし、clean | 危険入口。正本はworkspace内 `dori-manga` |
| `家計簿` | remoteなし / unborn `master` | commitなし、clean | 危険入口。正本は `kakeibo-liff` |
| `管理ターミナル` | `mgmt-terminal` / `main` | origin/mainと同期、clean | 有効な安定clone。台帳未登録 |
| `議事録システム` | `meeting-minutes-system` / `main` | origin/mainと同期、clean | 有効な安定clone |
| `事業振り返り` | `yumekango-business-management` / `main` | origin/mainと同期、clean | 有効な安定clone |
| `台湾プロジェクト` | `taiwan-outreach` / `main` | HEADはorigin/mainと同期、9 local differences | 有効だが未同期情報あり。削除禁止 |

## Incomplete Git Markers

次の3か所には空の `.git` ディレクトリがあるが、`config`もなくGitリポジトリとして成立していない。

| Path | State |
|---|---|
| `C:\Users\irodo\Documents\Codex\.git` | empty |
| `C:\Users\irodo\Documents\Codex\2026-06-16\files-mentioned-by-the-user-mov\.git` | empty |
| `C:\Users\irodo\Documents\Codex\2026-06-25\iwa\.git` | empty |

## Local Information That Must Be Preserved

次の情報はGitHub `main` と同一ではないため、整理前に内容確認と移送判断が必要である。

| Location | Local-only or different information |
|---|---|
| stale workspace clone dated 2026-06-06 | modified `dori-manga/docs/work_log.md` |
| same stale workspace clone | untracked `docs/kango-mamori-hp-management.md` |
| same stale workspace clone | untracked `taiwan-outreach/studio-copy-page-log.md` |
| `台湾プロジェクト` | modified `docs/work-log.md` plus 8 untracked output entries |
| `Kアラート・テスト開発` | untracked `.wrangler/` and `outputs/` |
| `kakeibo-liff` | remote feature branchにあり、既定 `main` には未統合の1 commit |
| `k-alert-production-workspace-push` | workspace `main` にない1 unique commit |

`Codex\2026-06-03\mac-github\workspace` の14削除は、対象パスが現在の `origin/main` にも存在しないことを確認した。ただし、この確認だけでローカルディレクトリ削除を許可するものではない。

## Codex Trusted Path Inventory

`C:\Users\irodo\.codex\config.toml` には31個の `[projects]` trusted pathがある。

分類:

- 日付別タスクフォルダ: 20
- 日本語名などの固定フォルダ: 10
- `Documents\Codex` 全体: 1
- trusted pathのうち成立した正規Git clone: `台湾プロジェクト`、`議事録システム`、`事業振り返り`、`管理ターミナル` の4
- trusted pathのうちremoteもcommitもないGit入口: `Kアラート・テスト開発`、`家計簿`、`APIモニター`、`Freee`、`どり看護師マンガプロジェクト`、`Kアラート` の6
- 正式なローカルcloneだが明示的trusted pathにない: `Kアラート・本番開発`、`kakeibo-liff`、`workspace`

日付別trusted path 20件:

```text
C:\Users\irodo\Documents\Codex\2026-06-06\youtuber-35-coo-40-10-0
C:\Users\irodo\Documents\Codex\2026-06-06\github-github-claude-codex-md-github
C:\Users\irodo\Documents\Codex\2026-06-07\liff-k-notion-github-k-line
C:\Users\irodo\Documents\Codex\2026-06-07\https-kango-mamori-com-tw-url
C:\Users\irodo\Documents\Codex\2026-06-07\notion
C:\Users\irodo\Documents\Codex\2026-06-07\hp-hp
C:\Users\irodo\Documents\Codex\2026-06-08\google
C:\Users\irodo\Documents\Codex\2026-06-08\github-notion
C:\Users\irodo\Documents\Codex\2026-06-08\notion-plugin-notion-openai-curated
C:\Users\irodo\Documents\Codex\2026-06-08\new-chat
C:\Users\irodo\Documents\Codex\2026-06-08\https-docs-google-com-spreadsheets-d
C:\Users\irodo\Documents\Codex\2026-06-11\supabase
C:\Users\irodo\Documents\Codex\2026-06-16\lm-s-jinnouchi-yumekango-com-google
C:\Users\irodo\Documents\Codex\2026-06-16\files-mentioned-by-the-user-2
C:\Users\irodo\Documents\Codex\2026-06-16\files-mentioned-by-the-user-mov
C:\Users\irodo\Documents\Codex\2026-06-17\files-mentioned-by-the-user-xlsx
C:\Users\irodo\Documents\Codex\2026-06-20\new-chat
C:\Users\irodo\Documents\Codex\2026-06-21\new-chat
C:\Users\irodo\Documents\Codex\2026-06-21\new-chat-2
C:\Users\irodo\Documents\Codex\2026-06-25\iwa
```

固定trusted path 10件:

```text
C:\Users\irodo\Documents\台湾プロジェクト
C:\Users\irodo\Documents\Kアラート・テスト開発
C:\Users\irodo\Documents\家計簿
C:\Users\irodo\Documents\APIモニター
C:\Users\irodo\Documents\議事録システム
C:\Users\irodo\Documents\Freee
C:\Users\irodo\Documents\事業振り返り
C:\Users\irodo\Documents\どり看護師マンガプロジェクト
C:\Users\irodo\Documents\管理ターミナル
C:\Users\irodo\Documents\Kアラート
```

残る1件は `C:\Users\irodo\Documents\Codex` であり、Gitリポジトリではない。また直下に空の `.git` がある。

`trust_level` の登録はプロジェクト正本を選ぶ台帳ではない。現在は、正式cloneよりも空フォルダの方が明示登録されている例があるため、プロジェクト入口として利用してはいけない。

## Shogun Exclusion

確認した存在:

- GitHub: `https://github.com/sjinnouchi-ux/multi-agent-shogun`
- workspace path: `shogun-lab/`
- このPCの `C:\tools\multi-agent-shogun`: 2026-07-11時点では存在しない

Shogun関連ファイル、設定、ブランチ、台帳行は変更していない。今後の削除・移動・統一作業からも、ユーザーが別デスクトップで扱う範囲として除外する。

## Target Cross-PC Structure

```text
GitHub: sjinnouchi-ux/workspace/PROJECTS.md
  -> project GitHub URL or workspace path
     -> repository AGENTS.md and project entry docs
        -> task-scoped local clone/worktree
           -> commit / push / main or PR verification
              -> local cleanup gate
```

各PCに永続保持するもの:

- Git / GitHub CLI / Codex
- GitHub認証
- `~/.codex/config.toml`
- GitHub正本から配布した `~/.codex/AGENTS.md`
- 秘密情報そのものではなく、安全な秘密情報ストアへの参照設定

タスクごとに使い捨てるもの:

- clone/worktree
- build cache
- `.wrangler/` 等のツール生成物
- ダウンロードや検証用HTML/JSON

GitHubまたは指定保存先へ残すもの:

- コード
- `PROJECT_BRIEF.md`
- `DESIGN_LOG.md`
- `IMPLEMENTATION_LOG.md`
- 必要な作業ログと検証証跡
- GitHubに置けない最終成果物は指定Google Drive

## Recommended Remediation Order

1. ローカル固有Markdownと未統合commitを内容確認し、正しいGitHub repoへ救出する。
2. `PROJECTS.md` の相対パスを完全なGitHub URLへ直し、未登録repoをActive / Support / Reference / Archivedに分類する。
3. GitHub正本のグローバル `AGENTS.md` テンプレートとWindows配布スクリプトを作る。
4. このPCと別PCの `~/.codex/AGENTS.md` を同じテンプレートから導入し、ハッシュで一致確認する。
5. 正式な安定cloneの場所と、タスク用一時フォルダの命名を統一する。
6. 空Git入口、空 `.git`、重複clone、古いtrusted pathを、救出完了後にユーザー確認の上で削除する。
7. 各repoに不足する `AGENTS.md` と標準入口文書を追加する。

## Changes Made During Inventory

- 読み取りと `git fetch origin --prune` によりremote refsを更新した。
- 公式Codex仕様確認のため、`C:\Users\irodo\.codex\config.toml` に `openaiDeveloperDocs` MCPを追加した。現在のCodexアプリでツール一覧へ反映するにはアプリ再起動が必要。
- プロジェクトファイルの削除、移動、マージ、未同期内容の書換えは行っていない。

## Traffic Control Decision

棚卸し後、ユーザーは次の運用を採用した。

- Codex Desktopのパーソナライズには、GitHub上の共通起動手順と `PROJECTS.md` を毎回取得する短いbootstrapだけを置く。
- 全プロジェクトの正本はオンラインGitHubとし、ローカルclone/worktreeはタスク単位の作業場として扱う。
- タスク完了時はcommit、push、ログ更新、必要なlive確認を終えてからローカルを整理する。
- ShogunはWSL2 Linuxで起動しWebUIから利用する。Codex Desktop設定完了後、同じGitHub pushとcleanup規則へ改修する。
- Shogun実装・WSL2・WebUIの変更は今回行わない。

## Traffic Control Execution Result

前節までのローカル一覧は交通整理実施前のスナップショットである。2026-07-11 JSTに次を実施した。

### Resolved

| Item | Result |
|---|---|
| 共通ルーターと起動手順 | `workspace` PR #4をmerge。`main` は `e976f29352eaf08f996c1182e7509233e11ed99f` |
| stale workspaceのdori-mangaログ | 確認済み2026-06-16記録を `workspace/main` へ救出 |
| stale workspaceの看護まもりSTUDIOメモ | 現行repoへ整理し、`kango-mamori-studio-requests` PR #2、`44c676065d37a2e95493ae22275544ef50e309bf` へ反映 |
| 台湾プロジェクトの確認済みログ | `taiwan-outreach` PR #1、`dc02db8cd879f7e4f7dba96dc9ffc42d1e9d489d` へ反映 |
| 台湾プロジェクトの生成物 | `outputs/` をignore対象として保持。OAuth関連を読まず、commitしていない |
| このPCの共通入口 | `C:\Users\irodo\.codex\AGENTS.md` をオンラインbootstrapへ切替。変更前ファイルを `C:\Users\irodo\.codex\backups` へ保存 |
| 安定workspace clone | `C:\Users\irodo\Documents\workspace` を更新後の `origin/main` へfast-forward |
| 今回作成した一時clone | PR反映とclean状態を確認後、`C:\Users\irodo\Documents\Codex\2026-07-11\traffic-control` を削除 |

共通起動文書、`PROJECTS.md`、パーソナライズ用文面のraw URLはHTTP 200を確認した。`PROJECTS.md` に記載したPrimary Docsと起動文書の参照先も解決できることを確認した。

### Preserved Pending Explicit Approval

| Category | Preserved item | Reason |
|---|---|---|
| 空または誤誘導Git入口 | `APIモニター`、`どり看護師マンガプロジェクト`、`家計簿`、`Freee`、`Kアラート`、`Kアラート・テスト開発` | 既存資産の破壊的削除には明示承認が必要 |
| 空 `.git` | `C:\Users\irodo\Documents\Codex\.git` ほか棚卸し済み3件 | 親フォルダの用途を維持したまま削除判断が必要 |
| stale / duplicate clone | 旧workspace clone、重複business-management clone、入れ子の一時clone | 救出済み内容と残存差分を最終照合してから削除する |
| 未統合branch | `kakeibo-liff`、`k-alert-production-workspace-push` | `main` にないcommitを保持している |
| ローカル生成物 | `Kアラート・テスト開発` の `.wrangler/` と `outputs/`、台湾のignored `outputs/` | 内容確認または安全な廃棄判断が未完了 |
| Codex trusted path | `config.toml` の31件 | `trust_level` はルーティングではなくproject設定の信頼境界であり、一括削除対象ではない |

Shogunは将来のWSL2 Linux + WebUI改修方針だけを共通文書へ記録した。実装、WSL2設定、WebUI設定は変更していない。
