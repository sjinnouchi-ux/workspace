# GitHub整理メモ

## 2026-06-06 時点の整理方針

- `market-pilot` は単体リポジトリ `sjinnouchi-ux/market-pilot` を正本にする。
- `workspace/market-pilot` は削除済み。`workspace/INDEX.json` から単体リポジトリへリンクする。
- `dori-manga` は `workspace/dori-manga` を正本にする。
- `supabase-db-templates/dori-manga` は削除済み。DB設計・ChatGPT指示・Supabase連携GASは `workspace/dori-manga` に集約する。
- Notionは詳細ログの置き場ではなく、プロジェクト一覧・ステータス・優先度・次アクションの上層管理に使う。

## Markdown運用ルール

- `README.md`: 人間向けの入口。
- `AGENTS.md`: Codex向けの入口。
- `CLAUDE.md`: Claude向けの入口。Codex管理プロジェクトでは読取専用の注意を書く。
- `docs/work_log.md`: 詳細な作業履歴。
- `docs/*/residual_tasks.md`: 残課題台帳。
- Notionには詳細ログをコピーしない。Notionには最新状態と次アクションだけを書く。

## Notionへ持っていく情報

- Project
- Status
- Stage
- Priority
- Owner
- GitHub URL
- Primary Docs
- Production URL
- Preview URL
- Supabase URL
- Google Drive URL
- Google Sheets URL
- Apps Script URL
- Admin URL
- Reference URLs
- Next Action
- Blocker
- Review Cycle
- Last Updated
- Notes

## AI初期会話ルール

- 最初の会話では `INDEX.json` と `docs/notion/projects.csv` だけで全体像を把握する。
- ユーザーが特定プロジェクト名を出すまで、詳細な `work_log.md` や設計書は読みに行かない。
- ユーザーが「market-pilotを進めたい」「dori-mangaを確認したい」のように指定した時だけ、`Primary Docs` に記載されたファイルから読む。
- Notionは進捗とURLの司令塔、GitHubは詳細ログと制作物の正本として扱う。
