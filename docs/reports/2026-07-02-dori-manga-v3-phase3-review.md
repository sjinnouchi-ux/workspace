# dori-manga v3 Phase 3 webapp実装レビュー依頼

作成日: 2026-07-02
対象: dori-manga 管理システム改修 / webapp v3実装

## 結論

Phase 3（webapp v3実装）は、単一HTML構成を維持して完了しました。

`dori-manga/webapp/index.html` を3タブ（制作／インポート／管理）構成へ全面改訂し、CSV仕様、保存タイミング、Edge Functions導線、Phase 1・2レビュー申し送りを反映しています。

## 変更ファイル

- `dori-manga/webapp/index.html`
  - webapp v3本体。
- `dori-manga/docs/work_log.md`
  - Phase 3実装・疎通テスト・削除確認を追記。
- `docs/reports/2026-07-02-dori-manga-v3-phase3-review.md`
  - 本レビュー依頼。

## 実装内容

### 制作タブ

- 作品一覧をスプシ代替テーブルとして実装。
- 列: 作業チェック / タイトル / 状態 / 1〜4コマ案 / 投稿案 / PDF URL。
- コマ案・投稿案・PDF URLはフォーカスアウトでDB自動保存。
- 状態は `完成` / `未完成` / `不採用` のプルダウンで即保存。
- フィルター `すべて` / `完成` / `未完成` / `不採用` と件数表示を実装。
- 作業チェックは `episodes.is_working` を更新し、同時に1件のみtrueにする。
- 「新しい漫画を作る」は `create_episode_with_panels` → `create-episode-folder` の順に実行。
- CSVインポート／エクスポート導線を実装。

### インポートタブ

- 評価プロンプト OK / NG / CLOSE のコピーボタンを実装。
- 押下時にDB `prompt_templates` から最新activeテンプレートを再取得してコピー。
- 画像登録フォームを実装。
  - 作品
  - コマ番号
  - 判定
  - 画像ファイル
  - ChatGPT JSON
- 登録処理は `upload-image` → `import_generation_attempt` の順に実行。
- 判定不一致時はconfirmを表示。
- 10MB超画像はクライアント側で停止。
- `duplicate` 応答時は、画像はDriveに残るがDB重複登録はされない旨を警告表示。

### 管理タブ

- Supabase疎通・最終DB登録日時・keepalive案内を表示。
- 作品数、完成、未完成、不採用、画像評価数、改善ルール数を集計表示。
- `app_settings` のDrive親フォルダURL/ID表示・保存を実装。
- 評価プロンプト OK / NG / CLOSE の編集保存を実装。
- CSVテンプレートダウンロードを実装。

## CSV仕様

- 列:
  - `タイトル,状態,1コマ案,2コマ案,3コマ案,4コマ案,投稿案,PDF URL`
- エクスポート／テンプレート:
  - UTF-8 BOM付き
  - CRLF
  - 全フィールド引用符囲み
- インポート:
  - 自前RFC4180パーサーを実装。
  - 引用符内カンマ、引用符内改行、`""` エスケープに対応。
- 状態4値:
  - `新規作成`
  - `完成`
  - `未完成`
  - `不採用`
- 二重登録防止:
  - `新規作成` は既存タイトル一致時にスキップ。
  - 同一CSV内で同じ新規タイトルが複数回出た場合もスキップ。
  - `完成` / `未完成` / `不採用` は既存タイトルの更新のみ。
  - 未知タイトルの更新行はスキップ。

## Phase 1・2レビュー申し送りへの対応

1. `create-episode-folder` 呼び出し時は必ずDB上のタイトルを渡す
   - 呼び出し直前に `manga_episodes` をidで再取得し、取得した `title` を送信。
2. `episode_folder_missing` / `status_folder_missing` 受信時の導線
   - インポート画面で該当エラーを受けた場合、「フォルダ作成を実行しますか？」とボタンを表示。
3. `upload-image` の実画像疎通
   - 1x1 PNGで実疎通済み。
4. `reused=true` の動作確認
   - 同一episodeに対して `create-episode-folder` を2回実行し、2回目が `reused=true` になることを確認。
5. 単一HTML構成・定数流用
   - `index.html` 単一ファイルのまま実装。
   - `SUPABASE_URL` / `SUPABASE_ANON` / `LOGIN_EMAIL` は既存値を流用。

## 実疎通テスト

テストepisode:

- title: `__codex_phase3_upload_test_20260702_201426`
- episode id: `ddf69776-9477-4965-bc66-eecdb93374d1`

結果:

- `create-episode-folder` 1回目: `reused=false`
- `create-episode-folder` 2回目: `reused=true`
- Drive folder id: `1XQmH7N39vhJ8NXefY7AAJXsnh1zbyplU`
- `upload-image`:
  - file: `phase3-upload-test.png`
  - uploaded file id: `1IAwZ9_oN79M-xbFEaLNZrDI2rbQFCxVb`
  - response: `status=ok`
- `import_generation_attempt`:
  - response: `status=ok`
  - attempt id: `45c2aea0-214c-4c58-869d-099468fa97af`

削除確認:

- Supabaseテスト `generation_attempts` / `prompt_lessons` / `manga_panels` / `manga_episodes`: 削除済み。
- `__codex_phase3_upload_test_20260702_%` のテストepisode残数0。
- `phase3-upload-test.png` のテストattempt残数0。
- DriveテストフォルダはDrive APIで削除済み。削除API status `204`。
- 親Driveフォルダ直下は空に戻ったことを確認。

## 検証

- `index.html` のインラインJavaScriptをNode `new Function` で構文チェックし成功。
- ローカルHTTP `http://127.0.0.1:8787/index.html` でログイン画面表示を確認。
- ブラウザコンソールエラー0件。
- ログイン後UIはパスワードを記録していないため自動操作していません。DB/Edge Function/Drive疎通はAPI経由で確認済みです。

## 迷った点

- `prompt_templates` は既存列 `name` / `template_text` / `is_active` を使用しました。新規列追加はしていません。
- CSV新規作成直後のコマ案保存は、メモリ上の一覧ではなくDBから `manga_panels` を取り直して保存する実装にしました。
- `status_folder_missing` は本来フォルダ構成欠損ですが、画面導線としてはまず `create-episode-folder` 再実行を案内します。既存子フォルダは再利用され、不足分が作成される想定です。

## Claude重点レビュー依頼

- フォーカスアウト保存・状態即保存のタイミングが妥当か。
- CSVパーサーがスプシCSVの引用符内カンマ/改行/`""` に十分対応できているか。
- CSV二重登録防止の条件が安全か。
- `episode_folder_missing` / `status_folder_missing` の画面導線が十分か。
- `upload-image` → `import_generation_attempt` の順序とduplicate時の表示が妥当か。

## Phase 4予定

- Cloudflare Pagesへデプロイ。
- ログイン後UIを実ブラウザで検収。
- 引き継ぎ書7章の検収チェックリストを実施。
- 検収結果を `docs/reports/` に記録し、work_log更新後にpush。
