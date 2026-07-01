# PROJECTS

Claude / Codex は、ユーザー発言から該当プロジェクトを探すとき、まずこの表を見る。

`Alias` 列で表記ゆれを吸収する。ここにない場合は、勝手に新規作成・凍結扱いせず、ユーザーに確認する。

## 現役・移行中

| Project | Alias | Status | 設計 | 実装 | Last Design | Last Impl | Repo / Path | Notes |
|---|---|---|---|---|---|---|---|---|
| 家計簿LIFF FastAPI化 | 家計簿, kakeibo, kakeibo-liff, yumekango-worker | Active / Pilot | FABLE 5 / Claude | Codex |  |  | `yumekango-worker` / local pilot repo TBD | 最初のShogun/Codex分業パイロット。既存LIFF/GAS/WorkerをFastAPI化する。 |
| Kアラート本番開発 | Kアラート, K-alert, kalert, k-alert-production | Active | Claude | Codex |  | 2026-07-01 | `https://github.com/sjinnouchi-ux/k-alert-production` | 本番運用あり。Cloud Run / Cloudflare Worker / GAS / Supabase。 |
| 台湾プロジェクト | 台湾, taiwan, taiwan-outreach, インバウンド | Active | Claude | Codex |  | 2026-07-01 | `https://github.com/sjinnouchi-ux/taiwan-outreach` | 看護守台湾向けLP/SNS/YouTube/GA4/Search Console。 |
| dori-manga | どり漫画, dori, どり看護師 | Active（移行中） | Claude | Codex |  |  | `dori-manga/` | 既存workspace配下から新方式へ移行予定。 |
| API Monitor | APIモニター, api-monitor | Active | Claude | Codex |  | 2026-07-01 | `https://github.com/sjinnouchi-ux/api-monitor` | 3社API usage/cost同期。独立プロジェクトGitへ移行済み。 |
| Shogun Lab | Shogun, multi-agent-shogun, FABLE5, 要件定義 | Support / Workflow | FABLE 5 / Claude | Codex | 2026-07-01 | 2026-07-01 | `shogun-lab/` | Shogun設計MDをCodex実行へ渡す中継領域。実装コード置き場ではない。 |
| 議事録システム | meeting-minutes, 議事録 | Active | Claude | Codex |  |  | `https://github.com/sjinnouchi-ux/meeting-minutes-system` | 単体GitHub repoあり。 |
| ゆめ看護 事業管理 | yumekango-business-management, 看護守事業 | Active（移行検討） | Claude | Codex |  |  | `https://github.com/sjinnouchi-ux/yumekango-business-management` | 事業管理系Markdown。 |

## 凍結・完了

| Project | Alias | Status | Frozen/Completed Date | Final Repo / Path | Notes |
|---|---|---|---|---|---|
| market-pilot | market, 株, ETF, 売買シグナル | Frozen | 2026-07-01 | `https://github.com/sjinnouchi-ux/market-pilot` | 凍結。保守も原則停止。再開時はユーザー確認後にActiveへ戻す。 |
| Kアラート・テスト開発 | k-alert-test, Kアラートテスト | Completed / Legacy |  | `k-alert-test/` | 本番開発へ知見移行済み。必要時のみ参照。 |
| code-exchange | Claude Desktop, CLI橋渡し | Frozen / Legacy | 2026-07-01 | `code-exchange/` | Shogun + MiniPC集約方針により旧Desktop/CLI橋渡しは廃止。 |

## 記入ルール

- Statusは `Active` / `Active / Pilot` / `Active（移行中）` / `Support / Workflow` / `Frozen` / `Completed` / `Legacy` を使う。
- 日付は `YYYY-MM-DD`（JST）。未確定なら空欄にする。
- 設計/実装列はCLI割当または担当エージェント名を書く。
- Shogunの `projects/{name}.yaml` はこの表から最小項目をミラーする従属物。正本はこの表。
