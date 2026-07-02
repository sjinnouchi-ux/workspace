# dori-manga v3 Phase 4 デプロイ・検収報告

作成日: 2026-07-02
対象: dori-manga 管理システム改修 / Phase 4

## 結論

Cloudflare Pagesへのデプロイと主要検収を実施しました。

本番URL:

- https://dori-manga-admin.pages.dev/

最終デプロイ確認URL:

- https://8e6d5340.dori-manga-admin.pages.dev

## 変更ファイル

- `.gitignore`
  - Wranglerローカルキャッシュ `.wrangler/` をignore。
- `dori-manga/webapp/index.html`
  - Phase 4検収中に見つかったUIイベント・履歴表示・コピー・JSON不正時登録仕様を修正。
- `dori-manga/docs/work_log.md`
  - Phase 4実施内容を追記。
- `docs/reports/2026-07-02-dori-manga-v3-phase4-review.md`
  - 本報告。

## デプロイ

- Wrangler: `4.106.0`
- Pages project: `dori-manga-admin`
- 本番URL: `https://dori-manga-admin.pages.dev/`
- 本番URL HTTP確認: `200 text/html`

## 検収結果

### 1. ログイン → 3タブ表示

- 陣内さんのパスワード入力協力によりログイン。
- 制作／インポート／管理タブ表示を確認。
- ブラウザコンソールにCORSエラーなし。

### 2. 制作タブ

- 新規作品作成からDriveフォルダ自動生成を確認。
- コマ案・投稿案・PDF URLの保存をDBで確認。
- 状態変更とフィルター連動を確認。
- 作業中チェックを1件trueにし、インポートタブの作品初期選択に連動することを確認。

検収中修正:

- 新規作成をブラウザprompt依存から画面内入力フォームへ変更。
- 動的行の保存イベントを安定化。
- フォーカスアウト保存に加え、入力中の遅延保存を追加。

### 3. 新規作成 → Driveフォルダ

Pages本番URLから `create-episode-folder` を呼び、Driveフォルダと子フォルダ作成を確認しました。

- ブラウザコンソールにCORSエラーなし。
- Driveフォルダリンクが画面に表示されることを確認。

### 4. CSVインポート

CSVファイル:

- `phase4-csv-test.csv`

結果:

- 画面表示: `新規作成 1件`
- 作成title: `__codex_phase4_csv_test_20260702_2105`
- DB:
  - status: `未完成`
  - 1〜4コマ案保存済み
  - 投稿案保存済み
  - PDF URL保存済み
  - `drive_folder_id` / `drive_folder_url` 保存済み
- Drive:
  - 作品フォルダ作成済み
  - `OK` / `NG` / `CLOSE` / `完成` サブフォルダ作成済み

### 5. インポートタブ

- プロンプトコピー:
  - HTTPS本番URLで、陣内さんの手動クリックにより「OKの評価プロンプトをコピーしました。」表示を確認。
  - `navigator.clipboard.writeText` 失敗時の `document.execCommand("copy")` フォールバックと失敗表示を追加。
- 履歴表示:
  - PostgRESTリレーション曖昧性を修正し、履歴テーブル表示を確認。

画像登録仕様変更（陣内さん指示、Claude確認不要）:

- ChatGPT JSONが空または不正でも、画像アップロードを止めない仕様へ変更。
- DBには以下を保存する。
  - `evaluation_json.json_parse_status = "invalid"`
  - `evaluation_json.json_parse_error`
  - `evaluation_json.raw_text`
  - `evaluation_json.repair_needed = true`
- JSONが正常な場合は `evaluation_json.json_parse_status = "ok"` を保存。
- `attempt_number` が取得できない場合は、対象コマの既存最大値+1を自動採番。

不正JSON相当の実疎通:

- `upload-image`: `status=ok`
- `import_generation_attempt`: `status=ok`
- DB確認: `json_parse_status=invalid` / `repair_needed=true`

### 6. 管理タブ

- Supabase疎通OK表示を確認。
- 集計表示を確認。
- Drive親フォルダURLリンク表示を確認。
- 評価プロンプト編集欄を確認。
- CSVテンプレート導線を確認。

### 7. keepalive

- Phase 0でGitHub Actions手動実行成功済み。
- Phase 4では画面上のkeepalive案内表示を確認。

## テスト資材削除

DB:

- `__codex_phase4_%` episode残数0。
- `phase4-%` attempt残数0。

Drive:

- `19_J3af05c60Z9yXXOO00Tpo_SOWPOehP`: 削除API status `204`
- `1sFdJc_aWeSgMA2NMG-Ef0o9V7z90syHp`: 削除API status `204`
- `1HtYjjpEf0aeNvJcE_z0GaFsVpNfRhOnW`: 削除API status `204`

## 迷った点・制約

- ブラウザ自動操作ではファイル選択inputに任意Fileを設定できず、UI上の画像ファイル選択は完全自動化できませんでした。
- ただし、`upload-image` の実疎通はPhase 3とPhase 4のAPI経由で確認済みです。
- Phase 4ではPages本番URLから `create-episode-folder` がCORSエラーなしで呼べることを確認しました。
- JSON不正時にも画像格納を優先する仕様変更は、陣内さん指示として扱い、Claude確認は不要としました。

## v3.1バックログ

Claude指摘3件はv3.1へ持ち越します。

- 重複画像への対策。
- フィルター再描画の改善。
- CSV空行の扱い改善。

追加バックログ:

- `json_parse_status=invalid` / `repair_needed=true` のレコードを定期抽出し、CodexまたはCoworkでJSON補修する運用タスクを設ける。
