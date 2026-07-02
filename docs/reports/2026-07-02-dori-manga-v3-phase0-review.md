# dori-manga v3 Phase 0 Claude確認依頼

作成日: 2026-07-02
対象: dori-manga 管理画面 全面改訂 Phase 0
実装担当: Codex
設計担当: Claude

## 実施内容

- Claudeからの橋渡しDriveフォルダを確認し、同梱ファイルをGit管理下へ配置した。
  - Driveフォルダ: https://drive.google.com/drive/folders/1GBnVR2eorz0KAjDFrUcKGhLGeHUDVyCd
- v3引き継ぎ書を `dori-manga/docs/handoff/codex-handoff-v3.md` に配置した。
- v2設計経緯・セットアップ資料・参考SQLを `dori-manga/docs/supabase/` に配置した。
- GitHub Actions keepalive workflowを `.github/workflows/supabase-keepalive.yml` に配置した。
- GitHub CLIで `sjinnouchi-ux/workspace` に GitHub Secret `SUPABASE_ANON_KEY` を登録・更新した。値はローカルsecret管理ファイルから読み込み、Markdownには記録していない。
- Actions `Supabase keepalive` を手動実行し、成功を確認した。
  - Run: https://github.com/sjinnouchi-ux/workspace/actions/runs/28577872303
  - Job: `ping`
  - Step: `Ping dori-manga (REST select)`
  - Status: success
- Phase 3の土台として、同梱されていたv2版 `index.html` を `dori-manga/webapp/index.html` に配置した。
- 旧GAS資産を `dori-manga/gas/_retired/` に移動した。
- `dori-manga/docs/work_log.md` に本改訂の経緯と、Claude側で適用済みとされたmigration一覧を追記した。

## 変更ファイル一覧

- `.github/workflows/supabase-keepalive.yml`
- `docs/reports/2026-07-02-dori-manga-v3-phase0-review.md`
- `dori-manga/docs/handoff/codex-handoff-v3.md`
- `dori-manga/docs/supabase/db-import-redesign-v2.md`
- `dori-manga/docs/supabase/import_generation_attempt_v1.sql`
- `dori-manga/docs/supabase/webapp-setup.md`
- `dori-manga/docs/work_log.md`
- `dori-manga/webapp/index.html`
- `dori-manga/gas/_retired/create_manga_folders.gs`
- `dori-manga/gas/_retired/clasp-project/appsscript.json`
- `dori-manga/gas/_retired/clasp-project/create_manga_folders.gs`
- `dori-manga/gas/_retired/supabase-import/dori-manga-import.gs`

## 判断に迷った点

- `codex-handoff-v3.md` のPhase 0には `index.html` の配置が明記されていないが、4.1とPhase 3で「同梱のv2版」を土台にするとあるため、Phase 3に備えて `dori-manga/webapp/index.html` へ配置した。
- `import_generation_attempt_v1.sql` は「参考保管用・適用禁止」と明記されているため、実行せず `dori-manga/docs/supabase/` に参考資料として配置した。
- Phase 0完了後にActions `Supabase keepalive` を手動実行し、成功を確認済み。

## 次Phaseの予定

- Claude承認後、Phase 1として `dori-manga/supabase/functions/create-episode-folder/index.ts` と `dori-manga/supabase/functions/upload-image/index.ts` を実装する。
- Phase 1ではコードのみ実装し、デプロイは行わない。
- Supabase migrationは適用済み扱いとし、再実行・スキーマ変更は行わない。

## 確認してほしいこと

- Phase 0の配置先と旧GAS退避方針がv3設計意図と一致しているか。
- v2版 `index.html` をPhase 0で `dori-manga/webapp/index.html` に配置した判断で問題ないか。
- `import_generation_attempt_v1.sql` を参考資料としてリポジトリに残す方針で問題ないか。
