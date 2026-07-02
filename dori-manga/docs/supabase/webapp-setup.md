# どり漫画DB 管理画面 セットアップ手順（v2時点）

作成日：2026-07-02
※ 本書はv2時点の手順書。v3全面改訂の作業手順は codex-handoff-v3.md を正とする。
※ Authユーザー作成（STEP 1）と LOGIN_EMAIL 設定（STEP 2）は**実施済み**。

## 適用済みの作業（Claude実施済み・2026-07-02）

- ✅ Supabase dori-manga プロジェクト復元（ACTIVE_HEALTHY）
- ✅ migration `drop_folder_status_column`（冗長カラム削除）
- ✅ migration `rls_policies_authenticated_read`（ログインユーザーに読み取り許可）
- ✅ migration `import_generation_attempt_rpc_v2`（インポートRPC・authenticated実行許可）
- ✅ RPC冪等性テスト（duplicate検出の動作確認済み）
- ✅ Authユーザー作成：s.jinnouchi@yumekango.com
- ✅ index.html の LOGIN_EMAIL 設定

## STEP 3：Cloudflare Pages にデプロイ

**方法A：直接アップロード（最速）**
1. https://dash.cloudflare.com → Workers & Pages → Create → Pages → Upload assets
2. プロジェクト名（例: `dori-manga-admin`）→ index.html をアップロード
3. 発行されたURL（`https://dori-manga-admin.pages.dev`）を奥様のMacでブックマーク

**方法B：GitHub連携（更新が楽・推奨）**
1. `dori-manga/webapp/index.html` としてリポジトリにpush
2. Cloudflare Pages → Connect to Git → workspace リポジトリを選択
   - Build command: なし / Build output directory: `dori-manga/webapp`
3. 以後は git push だけで自動デプロイ

## STEP 4：動作確認

1. ブックマークからページを開く → パスワードでログイン
2. 「✅ データベースは稼働中です」の表示を確認
3. テスト登録：既存と同じコマ番号・試行回数のJSONで登録
   →「⚠️ 同じコマ・試行回数のレコードが既に存在します」が出ればOK（冪等性確認）

## STEP 5：GAS後片付け

- スプシのメニュー「🛑 Supabase定期更新を停止」でkeepaliveトリガー削除
- Apps Scriptのスクリプトプロパティから `SUPABASE_SERVICE_ROLE_KEY` を削除
- `dori-manga/gas/` はリポジトリ上 `gas/_retired/` へ移動（履歴として保持）

## STEP 6（標準実装）：GitHub Actions keepalive

休止対策の本線は「画面アクセス」だが、旅行等の空白期間に備え標準装備とする。
**費用：無料**（publicリポジトリはActions無制限。privateでも月2,000分無料に対し、このジョブは月1分未満）。

1. `supabase-keepalive.yml` を `.github/workflows/supabase-keepalive.yml` として配置しpush
2. GitHubリポジトリ → Settings → Secrets and variables → Actions →
   New repository secret：`SUPABASE_ANON_KEY` = `sb_publishable_b8a4K90d5R6S5RZReLa-HA_G6nNwKKW`
3. Actionsタブ →「Supabase keepalive」→「Run workflow」で手動実行し、緑✅を確認
4. 以後2日おきに自動ping。失敗するとGitHubから登録メールへ自動通知
   → 通知が来たらSupabaseダッシュボードでRestore

## 奥様の日常運用（v2フロー・参考）

1. ChatGPTで画像生成 → OK/NG/CLOSE判断 → 評価JSONを出力させる
2. Driveへの1次保存とフォルダ振り分け
3. ブックマークから管理画面を開く
4. JSON貼り付け＋Drive URL＋コマ番号＋判定を入力 →「DBに登録する」
5. 完了メッセージを確認して終わり（ページを開くだけで休止防止にもなる）

※ v3ではDrive振り分け・URL貼り付けが自動化される（codex-handoff-v3.md参照）
