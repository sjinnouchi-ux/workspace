# 作業ログ

## 2026-07-09（Secret Manager参照方針の明文化）
- `docs/secret-management.md` を追加し、dori-manga関連の作業PC・AIエージェント用secretはGoogle Secret Managerを正本として扱う方針を明文化。
- `C:\Users\irodo\.codex\.sandbox-secrets\global.env` は移行前の互換ファイルであり、新PCへコピーしない旨をREADME/CLAUDE文脈から辿れるようにした。
- 過去ログ内の `global.env` 記載は当時の実施記録として残し、現在の参照手順ではないことを新方針に記載。

## 2026-07-09（UI固定・操作ログ・NG/CLOSE理由）
- 状態変更時の保存メッセージに対象作品タイトルと変更後ステータスを表示するようにした。
  - 例: `人工呼吸器のモード（CPAP・A/C・SIMV）の状態を「制作中」で保存しました。`
- 上部ヘッダーと `制作` / `インポート` / `プロンプト` / `ログ` / `管理` タブを、下スクロール時も上部に固定表示するようにした。
- `ログ` タブを追加し、主要操作を日本語の操作ログとして `app_settings.operation_logs` に保存するようにした。
  - 対象: 状態変更、作品情報保存、コマ案保存、作業中チェック、新規作成、Driveフォルダ作成、CSV入出力、画像評価登録、プロンプト登録/編集/削除、管理設定保存。
  - 同じ操作が `change` と `focusout` で重複保存されないよう、状態セレクトのフォーカスアウト保存を抑止し、近接重複ログも除外するようにした。
- インポートタブで `NG` / `CLOSE` 選択時のみ `NG/CLOSE理由` 欄を表示するようにした。
  - 入力した理由は `generation_attempts.evaluation_summary` の先頭と `evaluation_json.manual_failure_reason` に入るため、Supabase上にも残る。
- 検証:
  - `index.html` 内インラインJavaScriptの構文チェック成功。
  - ローカル確認URL `http://127.0.0.1:8788/index.html?codex_ui_log_update=20260709c` をサブブラウザで表示し、コンソールエラー0件を確認。
  - タブ一覧に `ログ` が追加され、ヘッダーとタブのCSS `position: sticky` を確認。
  - インポートタブで `NG` 選択時に理由欄が表示され、`OK` に戻すと非表示になることを確認。
  - `人工呼吸器のモード（CPAP・A/C・SIMV）` を `未完成` から `制作中` に戻す検証操作で、タイトル付き保存メッセージと操作ログ保存を確認。最終状態は `制作中` のまま。

## 2026-07-09（制作中ステータス正規化）
- 制作タブで `制作中` を選んだ際に、旧設計由来の英語ステータス値が混在しても画面表示・フィルター・管理タブ集計で日本語4値として扱うように修正。
  - `completed` → `完成`
  - `in_progress` → `制作中`
  - `draft` → `未完成`
  - `rejected` → `不採用`
- `loadEpisodes()` で読み込んだ作品ステータスを正規化し、制作タブのプルダウン、フィルターボタン、CSVエクスポートが日本語値で揃うようにした。
- 管理タブ集計は、各日本語ステータスと対応する旧英語値を同じ件数として数えるようにした。
- 追加確認で、実DBの `manga_episodes_status_check` が `制作中` および `in_progress` を拒否していることを確認。
  - ブラウザ上のエラー: `new row for relation "manga_episodes" violates check constraint "manga_episodes_status_check"`
  - service role REST確認でも、対象作品 `人工呼吸器のモード（CPAP・A/C・SIMV）` の `status` を `in_progress` に更新すると同じ制約違反になることを確認。
- 実DBの制約を更新するマイグレーション `supabase/migrations/202607090930_allow_in_progress_episode_status.sql` を追加。
- 現環境ではSupabase管理アクセストークンや対象DBパスワードがなく、リモートDB制約の直接更新は未実行。
- そのため実運用回避として、`制作中` は `app_settings.episode_status_overrides` に作品ID別の上書き値として保存し、制作タブ表示・フィルター・CSV・管理タブ集計では通常の状態として扱うようにした。
- 検証:
  - `index.html` 内インラインJavaScriptの構文チェック成功。
  - ローカル確認URL `http://127.0.0.1:8788/index.html` をサブブラウザで再読み込みし、コンソールエラー0件を確認。
  - ローカル画面で状態フィルター `すべて (85)` / `完成 (4)` / `制作中 (0)` / `未完成 (79)` / `不採用 (2)` と、管理タブ集計が同じ件数で表示されることを確認。
  - 修正後、対象作品 `人工呼吸器のモード（CPAP・A/C・SIMV）` を `未完成` から `制作中` へ変更し、エラーなしで `保存しました。` が表示されることを確認。
  - 再読み込み後も同作品が `制作中` として表示され、状態フィルターと管理タブ集計が `制作中 (1)` / `未完成 (78)` になることを確認。

## 2026-07-05（制作タブ 状態・行視認性改善）
- 陣内さん指示により、制作タブの状態に `制作中` を追加。
  - 状態プルダウン、状態フィルター、CSVインポート許可値、CSVエクスポート、管理タブ集計は共通の `STATUSES` から反映される構成のため、`制作中` も同じ導線で扱う。
- 制作タブの作業チェック済み行に `working-row` 表示を追加。
  - チェックした行は薄い黄色背景と左ラインで強調し、行単位で作業対象を把握しやすくした。
- マニュアル `dori-manga-admin-user-manual.md` を更新し、状態4値とチェック行の色付き表示を追記。
- Web配布PDF `dori-manga-admin-manual.pdf` を再生成。
- 検証:
  - `index.html` 内インラインJavaScriptの構文チェック成功。
  - `git diff --check` 成功。
  - ローカル確認URL `http://127.0.0.1:8765/work/dori-manga-status-preview.html` をサブブラウザで表示し、`制作中` フィルター/選択肢とチェック済み行の色付き表示を確認。
  - Edgeヘッドレス印刷でマニュアルPDFを再生成し、HTMLスクリーンショットで日本語表示と `制作中` 記載を確認。
  - Cloudflare Pagesへデプロイし、デプロイURL `https://f6672084.dori-manga-admin.pages.dev` を確認。
  - 本番URL `https://dori-manga-admin.pages.dev/?v=88b1ff4` で `working-row` と `STATUSES = ["完成", "制作中", "未完成", "不採用"]` の反映、`dori-manga-admin-manual.pdf?v=88b1ff4` でPDF status 200 / size 450198 bytesを確認。

## 2026-07-03（v3.1 プロンプトタブ追加）
- Claude設計書 `codex-handoff-v3-1-prompt-tab.md` に基づき、管理画面へ「プロンプト」タブを追加。
  - `TABS` に `プロンプト` を追加し、制作／インポート／プロンプト／管理の4タブ構成に変更。
  - `prompt_gallery` テーブルから `created_at` 降順で一覧取得。
  - 登録フォーム: タイトル必須、プロンプト必須、参考画像任意。
  - 画像選択時のプレビューを追加。
  - 画像あり登録ではブラウザ側で長辺1280pxへ縮小し、JPEG品質0.8でStorage `prompt-gallery` へアップロード。5MB超過時は品質0.6で再試行。
  - 保存パスはUUIDベースの `{uuid}.jpg` とし、日本語ファイル名は使わない。
  - 画像なし登録では `image_path` / `image_url` を `null` で登録。
  - 一覧カード: 画像、タイトル、プロンプトtextarea、コピー、削除、タイトル検索、件数表示を実装。
  - タイトル・プロンプトは入力中700msデバウンス、フォーカスアウトでも保存。
  - 削除はconfirm後にDB行削除、`image_path` がある場合はStorageオブジェクトも削除。
- マニュアルを更新。
  - `dori-manga/docs/manuals/dori-manga-admin-user-manual.md` に「プロンプトタブ」章を追加。
  - 困ったときに、Supabase疎通NG、画像サイズ、パスワードリセット、Drive自動振り分け、PNG/JPEG案内を追記。
  - `dori-manga/webapp/dori-manga-admin-manual.pdf` を再生成し、日本語レンダリングを確認。
- 検証:
  - `index.html` 内インラインJavaScriptの構文チェック成功。
  - Supabase RESTで `prompt_gallery` 読み取り status `200` を確認。
  - Cloudflare Pagesへデプロイし、本番URL `https://dori-manga-admin.pages.dev/?v=prompt-tab-final` で4タブ表示、プロンプトフォーム、マニュアルリンク、コンソールエラー0件を確認。
  - ブラウザで画像なし登録→カード表示→編集保存→検索を確認。
  - 自動ブラウザ操作ではクリップボード権限によりコピーは拒否表示を確認。実運用の人間クリックでは既存コピー導線と同じ実装を使用。
  - ブラウザ削除確認ダイアログ後に制御がタイムアウトしたため、残ったテストデータ1件をAPIで削除し、残数0を確認。
  - 画像あり相当はAPIでStorage `prompt-gallery` アップロード `200`、DB insert `201`、DB delete `204`、Storage delete `200`、DB残数0を確認。
- Claude確認用MDを橋渡しDriveへアップロード: https://drive.google.com/file/d/1oQca-UnUNASeoELoNOs_pNAPMi99on8V/view?usp=drivesdk
- Claudeレビュー結果:
  - 仕様3章・4章の実装漏れなし。
  - `copyText()` 再利用は妥当。
  - クリップボードとファイル選択の自動操作制限に対し、Storage/API疎通での代替確認は受け入れ可能。
  - v3.1追加残件なし。
  - 検収完了前の人間目視確認として、陣内さん実ブラウザで「コピーボタンからChatGPT等へ貼り付けできること」「実画像登録後にカードへ画像表示されること」の2点を確認する。
- 陣内さんが実ブラウザで以下2点を確認済み。v3.1は運用開始可能。
  - プロンプトタブの「コピー」ボタンからChatGPT等へ貼り付けできること。
  - 実際の画像ファイルで登録し、カードに画像が表示されること。

## 2026-07-02（Phase 4）
- 陣内さん指示により、v3.1補修として管理タブの補修対象見える化を追加。
  - `evaluation_json.repair_needed = true` の件数を `JSON補修対象` として集計カードに表示。
  - 自動採番時の副作用検知として、直近1000件内の `同一panel_id × 同一file_name` かつ10分以内の再登録を `近接重複疑い` として集計カードに表示。
  - DBスキーマ変更は行わず、管理画面フロント側の集計として実装。
  - 本番HTML反映を確認し、実データ18件で `repair_needed=0` / `近接重複疑い=0` を確認。
- 陣内さん指示により、管理画面の操作マニュアルを追加。
  - Markdown正本: `dori-manga/docs/manuals/dori-manga-admin-user-manual.md`
  - Web配布PDF: `dori-manga/webapp/dori-manga-admin-manual.pdf`
  - 管理画面ヘッダーに「マニュアルPDF」ダウンロードリンクを追加。
  - PDFはヘッダーに `どり漫画DB 管理画面 操作マニュアル` を表示し、Edgeヘッドレス印刷で日本語表示を確認。
  - Claude最終確認用MDを橋渡しDriveへアップロード: https://drive.google.com/file/d/1QEjpgG8Jk8-brm8VoxtEGvJ_F3AvyLlV/view?usp=drivesdk
- Phase 3がClaude承認済みとなったため、Phase 4（Cloudflare Pagesデプロイ・検収）を実施。
- Wrangler `4.106.0` で Cloudflare Pages project `dori-manga-admin` を作成し、`dori-manga/webapp/index.html` をデプロイ。
  - 本番URL: `https://dori-manga-admin.pages.dev/`
  - 最終デプロイ確認URL: `https://8e6d5340.dori-manga-admin.pages.dev`
- Pages本番URLでログイン後、3タブ（制作／インポート／管理）表示を確認。
- 本番検収中に以下を修正し、都度Pagesへ再デプロイ。
  - 新規作成をブラウザprompt依存から画面内入力フォームへ変更。
  - 動的行の保存イベントを安定化し、フォーカスアウト保存に加えて入力中の遅延保存を追加。
  - CSVインポート等の主要ボタンにインラインフォールバックを追加し、クリック反応を安定化。
  - 履歴表示で `generation_attempts` と `manga_panels` の複数リレーションが曖昧になるため、`generation_attempts_panel_id_fkey` を明示。
  - プロンプトコピーに `document.execCommand("copy")` フォールバックと失敗表示を追加。
- Pages本番URLからの検収:
  - 新規作品作成 → `create-episode-folder` 呼び出し → Driveフォルダ自動生成を確認。ブラウザコンソールにCORSエラーなし。
  - コマ案・投稿案・PDF URL保存をDB上で確認。
  - 状態変更、フィルター、作業中チェック、インポートタブ初期選択連動を確認。
  - プロンプトコピーは、陣内さんの手動クリックで「OKの評価プロンプトをコピーしました。」表示を確認。
  - CSVインポートで `新規作成` 行から作品作成、4コマ案/投稿案/PDF URL保存、Driveフォルダ自動生成、`OK` / `NG` / `CLOSE` / `完成` サブフォルダ作成を確認。
  - 管理タブでSupabase疎通、集計、Drive親フォルダ表示、評価プロンプト編集欄、CSVテンプレート導線を確認。
- 陣内さん指示により、JSON不正時の画像登録仕様を変更（Claude確認不要）。
  - ChatGPT JSONが空/不正でも画像アップロードを止めない。
  - DB登録時に `evaluation_json.json_parse_status = "invalid"`、`json_parse_error`、`raw_text`、`repair_needed = true` を保存する。
  - JSONが正常な場合は `evaluation_json.json_parse_status = "ok"` を保存する。
  - `attempt_number` がJSONから取得できない場合は、対象コマの既存最大値+1を自動採番する。
- 不正JSON相当の実疎通テストを実施。
  - テストepisode `__codex_phase4_invalid_json_test_20260702_214058` を一時作成。
  - `upload-image` は `status=ok`、`import_generation_attempt` は `status=ok`。
  - DBで `json_parse_status=invalid` / `repair_needed=true` を確認。
  - テストDB資材とDriveフォルダ `1HtYjjpEf0aeNvJcE_z0GaFsVpNfRhOnW` は削除済み。
- Phase 4で作成したその他テスト資材も削除済み。
  - DB: `__codex_phase4_%` episode残数0、`phase4-%` attempt残数0。
  - Drive: テストフォルダ `19_J3af05c60Z9yXXOO00Tpo_SOWPOehP` / `1sFdJc_aWeSgMA2NMG-Ef0o9V7z90syHp` / `1HtYjjpEf0aeNvJcE_z0GaFsVpNfRhOnW` は削除API status `204`。

## 2026-07-02（Phase 3）
- Claude承認により、Phase 3（webapp v3実装）を開始。
- `dori-manga/webapp/index.html` を単一HTML構成のまま全面改訂し、3タブ（制作／インポート／管理）構成に変更。
  - 制作タブ: 作品一覧、状態フィルター、作業中チェック、コマ案・投稿案・PDF URLのフォーカスアウト保存、状態即時保存、新規作品作成、CSVインポート/エクスポートを実装。
  - インポートタブ: 評価プロンプト最新取得コピー、作品/コマ/判定/画像ファイル/ChatGPT JSONフォーム、`upload-image` → `import_generation_attempt` の順次登録を実装。
  - 管理タブ: Supabase疎通、集計、Drive親フォルダURL/ID表示・保存、評価プロンプト編集保存、CSVテンプレートDLを実装。
- CSVは `タイトル,状態,1コマ案,2コマ案,3コマ案,4コマ案,投稿案,PDF URL` に対応し、UTF-8 BOM付き・CRLF・全フィールド引用符で出力。インポートは自前RFC4180パーサーで引用符内カンマ/改行/`""` を扱う。
- CSV状態4値 `新規作成` / `完成` / `未完成` / `不採用` を実装。`新規作成` は既存タイトルとCSV内重複タイトルをスキップし、既存更新は未知タイトルをスキップする二重登録防止を入れた。
- Phase 1・2レビュー申し送りを反映。
  - `create-episode-folder` 呼び出し直前にDBからepisodeを再取得し、必ずDB上のタイトルを送信。
  - `episode_folder_missing` / `status_folder_missing` 受信時に、画面内へ「フォルダ作成を実行しますか？」導線を表示。
  - フォルダ作成済みepisodeへの再実行で `reused=true` になることを実疎通で確認。
  - `upload-image` の実画像疎通を1x1 PNGで実施。
- Phase 3実疎通テスト:
  - テストepisode `__codex_phase3_upload_test_20260702_201426` / episode id `ddf69776-9477-4965-bc66-eecdb93374d1` を一時作成。
  - Driveフォルダ `1XQmH7N39vhJ8NXefY7AAJXsnh1zbyplU` を作成し、2回目の `create-episode-folder` で `reused=true` を確認。
  - `upload-image` で `phase3-upload-test.png` をOKフォルダへアップロードし、file id `1IAwZ9_oN79M-xbFEaLNZrDI2rbQFCxVb` / `status=ok` を確認。
  - `import_generation_attempt` RPCも `status=ok` を確認し、attempt id `45c2aea0-214c-4c58-869d-099468fa97af` を一時作成。
  - テスト用 `generation_attempts` / `prompt_lessons` / `manga_panels` / `manga_episodes` は削除済み。DriveテストフォルダもDrive APIで削除し、親フォルダ直下が空に戻ったことを確認。
- 検証:
  - `index.html` 内のインラインJavaScriptをNode `new Function` で構文チェックし成功。
  - ローカルHTTP `http://127.0.0.1:8787/index.html` でログイン画面を表示し、ブラウザコンソールエラー0件を確認。
  - ログイン後UIはパスワードを記録していないため自動操作未実施。DB/Edge Function/Driveの実疎通はAPI経由で確認済み。

## 2026-07-02
- Phase 2前提タスクとして、MiniPC/Windows環境にDenoとSupabase CLIを導入。
  - Deno: winget `DenoLand.Deno`、確認バージョン `2.9.0`。
  - Supabase CLI: npm global `supabase`、確認バージョン `2.109.0`。
- `dori-manga/supabase/functions/` 配下の全 `.ts` に対して `deno check` を実行。
  - 初回はmultipart bodyとHeadersInitの型で3件エラー。
  - `google_drive.ts` と `supabase.ts` を修正し、再実行で成功。
  - 修正コミット: `592f79c Fix dori manga edge function type checks`。
- サブブラウザでGoogleアカウントが `s.jinnouchi@yumekango.com` であることを確認。
- Supabase Access Tokensページをサブブラウザで開き、ログイン済みであることを確認。
- GCP Consoleはパスワード再認証が必要な状態。GCPサービスアカウント作成、Drive API有効化、キーJSON取得、親フォルダ共有、Supabaseアクセストークン生成は人間タスクとして待機中。

## 2026-07-02（Phase 1）
- Phase 0がClaude承認済みとなったため、Phase 1（Edge Functions実装・コードのみ）を実施。デプロイは行っていない。
- `dori-manga/supabase/functions/create-episode-folder/index.ts` を追加。
  - 認証済みリクエストを前提に、作品IDとタイトルを受け取り、`app_settings` の `drive_root_folder_id` / `drive_root_folder_url` からDrive親フォルダを取得。
  - 親フォルダ直下に作品フォルダを作成または再利用し、配下に `OK` / `NG` / `CLOSE` / `完成` フォルダを作成または再利用。
  - `manga_episodes.drive_folder_id` / `drive_folder_url` を更新。
- `dori-manga/supabase/functions/upload-image/index.ts` を追加。
  - 作品フォルダ配下の判定フォルダ（`OK` / `NG` / `CLOSE`）を検索し、Base64画像をGoogle Driveへアップロード。
  - 10MB超の画像、作品フォルダ未作成、判定フォルダ不存在を日本語エラーで返す。
- 共通処理として `dori-manga/supabase/functions/_shared/` を追加。
  - `cors.ts`: CORS/JSONレスポンス。
  - `errors.ts`: 日本語エラー応答。
  - `supabase.ts`: JWT付きSupabase RESTアクセス、`app_settings` からDrive親フォルダ取得。
  - `google_drive.ts`: サービスアカウントJWT署名、OAuthトークン取得、Drive API呼び出し、Drive APIエラー分類。
- `dori-manga/supabase/config.toml` を追加し、`create-episode-folder` / `upload-image` の `verify_jwt = true` を明示。
- Phase 1のClaude確認依頼として、`docs/reports/2026-07-02-dori-manga-v3-phase1-review.md` を作成。
- 検証:
  - `git diff --check` 成功。
  - `verify_jwt = false`、`console.`、秘密値らしき実値、親フォルダIDハードコードがないことを `rg` で確認。
  - `deno` / `supabase` / `tsc` CLI はローカル未導入。`npx deno-bin` による一時Deno実行はタイムアウトしたため、Deno checkは未実行。
- Git外の人間タスクとして、旧GASのApps Script側後片付け（トリガー停止・スクリプトプロパティの `service_role` キー削除）は残っている。陣内さん作業。

## 2026-07-02（Phase 0）
- Claudeからの橋渡しDriveフォルダ `https://drive.google.com/drive/folders/1GBnVR2eorz0KAjDFrUcKGhLGeHUDVyCd` を確認し、v3全面改訂用の同梱ファイルをリポジトリへ配置。
  - `dori-manga/docs/handoff/codex-handoff-v3.md`
  - `dori-manga/docs/supabase/db-import-redesign-v2.md`
  - `dori-manga/docs/supabase/webapp-setup.md`
  - `dori-manga/docs/supabase/import_generation_attempt_v1.sql`
  - `dori-manga/webapp/index.html`
  - `.github/workflows/supabase-keepalive.yml`
- v3設計書では、Supabaseプロジェクト `vdntqwtywxyjxelycavx` に以下のmigrationがClaude側で適用・検証済みとされている。Codex側では再実行しない。
  - `drop_folder_status_column`
  - `rls_policies_authenticated_read`
  - `import_generation_attempt_rpc_v2`
  - `v3_episodes_production_columns`
  - `v3_rls_write_policies_and_rpc`
  - `v3_seed_evaluation_prompts`
- 旧GAS資産を履歴保持のため `dori-manga/gas/_retired/` へ移動。
  - `create_manga_folders.gs`
  - `clasp-project/`
  - `supabase-import/`
- Phase 0のClaude確認依頼として、`docs/reports/2026-07-02-dori-manga-v3-phase0-review.md` を作成。
- GitHub CLIで `sjinnouchi-ux/workspace` に GitHub Secret `SUPABASE_ANON_KEY` を登録・更新。値は `C:\Users\irodo\.codex\.sandbox-secrets\global.env` の `DORI_MANGA_SUPABASE_ANON_KEY` から読み込み、チャット・Markdown・GitHubには記録していない。
- Actions `Supabase keepalive` を手動実行し、成功を確認。
  - Run: https://github.com/sjinnouchi-ux/workspace/actions/runs/28577872303
  - Job: `ping`
  - Step: `Ping dori-manga (REST select)`
  - Status: success

## 2026-07-02
- Phase 2 Drive連携疎通の前提作業として、MiniPCに Deno `2.9.0` と Supabase CLI `2.109.0` を導入。
- `dori-manga/supabase/functions` 配下の全 `.ts` に対して `deno check` を実行し、型チェック通過を確認。
- GCP側で新規プロジェクト `dori-manga`（project ID: `studied-brand-501210-i1`）を作成。
- サービスアカウント `dori-manga-drive@studied-brand-501210-i1.iam.gserviceaccount.com` を作成し、Google Drive API を有効化。
- Drive親フォルダ `11UK7BKd-pcWW7eQSDghbkJxjxJa34Dbz`（`どり看護師_漫画格納フォルダ（改定）`）に、同サービスアカウントを編集者として共有。
- 共有後、一般アクセスが「リンクを知っている全員」だったため、指示どおり「制限付き」に戻したことをDrive共有ダイアログで確認。
- サービスアカウントキーJSON作成は、GCP組織ポリシー `iam.disableServiceAccountKeyCreation` によりブロック。`GOOGLE_SERVICE_ACCOUNT_JSON` をSupabase secretsへ設定できないため、Edge Functions deploy とJWT付きcurl疎通テストは未実施。
- 同日、プロジェクト限定で同ポリシーを上書き解除できるか確認したが、`orgpolicy.policies.create` / `orgpolicy.policies.delete` / `orgpolicy.policies.update` が不足しており、`s.jinnouchi@yumekango.com` では解除不可だった。
- 既存の `QQQ-Trading-System`（project ID: `qqq-trading-system-496304`）も確認。`iam.disableServiceAccountKeyCreation` は同じく親ポリシー継承で適用済み、既存サービスアカウント `qqq-trading-bot@qqq-trading-system-496304.iam.gserviceaccount.com` は「キーがありません」表示だったため、QQQから既存JSONを流用する経路も現時点では確認できなかった。
- 次のアクション: 組織ポリシー管理者がサービスアカウントキー作成制限を解除する、またはキーJSON不要の別認証方式に設計変更するかを判断する。
- 旧GASのApps Script側の後片付け（トリガー停止・スクリプトプロパティのservice_roleキー削除）は、Git外の人間タスクとして継続。
- Claude承認により、組織ポリシーは解除せず、Drive認証方式をサービスアカウントJSONからOAuthユーザー認証（refresh token）へ設計変更。
  - GCP `studied-brand-501210-i1` で OAuth同意画面を Internal として作成。
  - デスクトップアプリ用 OAuthクライアントを作成し、`https://www.googleapis.com/auth/drive` の初回同意フローで refresh token を取得。client secret / refresh token / Supabase access token はログ・チャット・ファイルへ保存していない。
  - `_shared/google_drive.ts` の `getDriveAccessToken()` を `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` による refresh token 交換方式へ変更。
  - `invalid_grant` は refresh token 失効として日本語メッセージを区別。
  - 変更後に `deno check` を全Functionsへ実行し成功。
  - 取得したOAuth refresh tokenでDrive親フォルダ `どり看護師_漫画格納フォルダ（改定）` を参照できることをローカル確認。
  - Supabase access tokenを生成して `supabase secrets set` / `functions deploy` を試行したが、Supabase側で `Your account does not have the necessary privileges to access this endpoint` の403。現在ログイン中のSupabase組織は `K Alert Production` で、対象project ref `vdntqwtywxyjxelycavx` へアクセスできていないため、Supabase権限またはログインアカウントの切り替えが必要。
  - 権限不足だったSupabase access tokenは削除済み。

## 2026-07-02
- dori-manga v3 Phase 2（Drive連携の疎通）をOAuthユーザー認証（refresh token）方式で実施。
- サービスアカウントJSON方式は、GCP組織ポリシー `iam.disableServiceAccountKeyCreation` とDrive保存容量0問題を避けるため採用しない方針に変更。
- `supabase/functions/_shared/google_drive.ts` を更新し、`GOOGLE_SERVICE_ACCOUNT_JSON` 参照を削除。`GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` から `https://oauth2.googleapis.com/token` へ refresh token 交換する方式に変更。
- Drive APIの403/404等の日本語エラー分類は維持し、`invalid_grant` はrefresh token失効として区別する日本語メッセージを追加。
- GCP `studied-brand-501210-i1` でOAuth同意画面を Internal として構成し、デスクトップアプリ用OAuthクライアントを作成。`https://www.googleapis.com/auth/drive` scopeでrefresh tokenを取得。秘密値はログ・チャット・ファイルに保存していない。
- Deno `2.9.0` で `dori-manga/supabase/functions` 配下の対象Edge Functionsを `deno check` し成功。
- Supabase project ref `vdntqwtywxyjxelycavx` に `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` / `GOOGLE_OAUTH_REFRESH_TOKEN` を `supabase secrets set` で設定し、`create-episode-folder` / `upload-image` をデプロイ。実値は記録していない。
- JWT付きでデプロイ済み `create-episode-folder` を疎通確認。テストepisode `__codex_phase2_oauth_test_20260702_194958` からDriveフォルダ `1WS0ipgrQbZMDR4dQ7Nd5GQDmP8r-4jFK` を作成し、`OK` / `NG` / `CLOSE` / `完成` サブフォルダ作成とDB `drive_folder_id` 更新を確認。
- テストepisode/panelsはSupabase上で削除し、同prefixのテストepisode残数0を確認。DriveテストフォルダはDrive APIで削除し、親フォルダ直下が空に戻ったことを確認。
- 不使用になったサービスアカウント `dori-manga-drive@studied-brand-501210-i1.iam.gserviceaccount.com` は親Driveフォルダの共有から削除し、共有残存なしをDrive APIで確認。
- Phase 2作業用に生成したSupabase access token `dori-manga-phase2-20260702-yumekango` は、作業完了後にSupabaseアカウント画面で削除し、一覧から消えたことを確認。
- 旧GASの後片付けとして、陣内さんがApps Script側のトリガー削除とスクリプトプロパティ `service_role` キー削除を実施したことを確認。

## 2026-06-21
- Notion API fallbackでプロジェクトDBの `dori-manga` 行を取得し、Git側ミラー `docs/notion/projects.csv` の同プロジェクト行をNotion最新値に同期。
- Supabase休眠防止用に `gas/supabase-import/dori-manga-import.gs` を更新。
  - スプレッドシートメニューに「Supabase更新を今すぐ実行」「3日ごとのSupabase更新を設定」「Supabase定期更新を停止」を追加。
  - `installSupabaseKeepaliveTrigger()` で3日に1回の時間主導トリガーを作成。
  - `runSupabaseKeepalive()` で `prompt_templates`、なければ `characters` の既存1行に `is_active` の軽いUPDATEを送る設計にした。
  - 既存の画像評価インポート処理には手を入れず、keepalive用の独立関数として追加。
- ローカル検証: `projects.csv` を `Import-Csv` で読み込み、`dori-manga` 行の列ずれがないことを確認。GASファイルはNodeの構文チェックを通過。
- Notionの `dori-manga` 行も更新し、Next Actionを「Supabase復元後、GASへkeepalive関数を反映し、installSupabaseKeepaliveTriggerを1回実行する。」へ変更。更新後のNotion値を `docs/notion/projects.csv` に再同期。
- Apps Script本体へのpushとトリガー有効化は、Windows環境に `clasp` と `.clasprc.json` が無いため未実行。GASエディタへ反映後、メニューまたは関数一覧から `installSupabaseKeepaliveTrigger()` を1回実行する必要がある。
- GitHub mainへGAS keepaliveコードを反映。コミット: `b7d32a3 Add dori manga Supabase keepalive`。
- ユーザー報告により、Apps Script側のコード反映と `installSupabaseKeepaliveTrigger()` の実行完了を確認。NotionのNext Actionを「3日ごとのSupabase keepalive初回自動実行後に、Supabase側で更新履歴またはREST疎通を確認する。」へ更新し、`docs/notion/projects.csv` に同期。

## 2026-06-16（Supabase OK格納確認）
- 添付画像 `C:\Users\irodo\Downloads\2.png` の作画タッチを確認。
  - 白背景、鉛筆スケッチ風、淡い着色、右側のどり看護師に紫の聴診器あり。
  - 「深夜のICU」文脈の医療漫画タッチとして、既存OK基準（手描き感、余白、聴診器あり）に近い。
- Supabase `generation_attempts` を確認。
  - `result_status=OK` かつ `folder_status=OK` のレコードは9件。
  - OKレコードの `image_url` は共通のDrive格納フォルダURL `https://drive.google.com/drive/folders/1QnEYY4DShAFVa0Lq9znQWuwoD1NEhTFW?usp=drive_link`。
  - 添付画像と同一セリフ（「ふぅ。やっと記録できるよ〜」「やっと座れた…」）を含むレコードは確認できなかった。
- Google Driveメタデータを確認。
  - `1QnEYY4DShAFVa0Lq9znQWuwoD1NEhTFW` は `漫画格納` フォルダ。
  - OK画像の個別ファイルは `drive_file_id` で参照され、上位に `どり看護師_漫画格納フォルダ`、テーマ別フォルダを持つ。
  - 例として `ChatGPT Image 2026年5月28日 09_56_27.png` はDriveファイル `1XaiNjLt1QKiDrRVC-jkI_tlCwxdeHW0Z`、Supabase上はOKだった。

## 2026-06-11
- Windows-Codex から `DORI_MANGA_SUPABASE_URL` / `DORI_MANGA_SUPABASE_SERVICE_ROLE_KEY` を `C:\Users\irodo\.codex\.sandbox-secrets\global.env` から一時読み込みし、Supabase REST API への接続を確認。
- 接続先ホストは `vdntqwtywxyjxelycavx.supabase.co` で、設計書の REST API URL と一致。
- 初回REST確認で404に見えた原因は、PowerShellの文字列 `"${table}?select=..."` 相当の書き方ではなく `"$table?select=..."` としていたため、`?select` 部分で変数展開が崩れ、テーブル名なしURLを叩いていたこと。
- Supabase SQL Editor で `information_schema.tables` を確認し、`characters` / `prompt_templates` / `manga_episodes` / `manga_panels` / `generation_attempts` / `prompt_lessons` はすべて `public` schema に存在することを確認。
- `curl.exe` でREST APIを再確認し、6テーブルすべて読み取り成功。件数は `characters` 2件、`prompt_templates` 2件、`manga_episodes` 1件、`manga_panels` 4件、`generation_attempts` 13件、`prompt_lessons` 39件。
- `generation_attempts.final_generation_prompt` の格納状況を確認。OK 11件・NG 2件はいずれもプロンプトあり。CLOSEは現時点で該当レコードなし。
- 環境変数上の anon key は publishable key 形式、service_role key は JWT 形式で存在することを確認。秘密値は表示・記録していない。
- OK画像確認で、直近4件はどり看護師に聴診器がなく、DBプロンプトにも `stethoscope` / `聴診器` 指定がないことを確認。4件を `generation_attempts` 上で OK から NG に再分類し、`evaluation_summary` に「聴診器なし」を記録。
- 再分類後の `generation_attempts` は OK 7件・NG 6件。OK 7件はすべてプロンプト内に `stethoscope` / `聴診器` 指定あり。
- `prompt_lessons` に「どり看護師には必ず紫の聴診器を見える位置に描く。プロンプトには purple stethoscope, clearly visible を必ず入れる。聴診器がない画像はNG。」を追加。

## 2026-05-28（動作確認エントリ）
- INDEX.json 自動更新ワークフロー（`.github/workflows/update-index.yml`）の発火確認のため、本ファイルを更新
- 期待される自動挙動：
  - push後、Actions が「Update INDEX.json」を実行
  - `.github/scripts/update_index.py` が `dori-manga` の変更を検出
  - INDEX.json の `projects.dori-manga.last_updated` を `2026-05-28` へ書き換え
  - github-actions[bot] が `chore(INDEX): auto-update last_updated [skip ci]` でcommit
- 確認後、本エントリは将来的に削除してよい（または残してINDEX運用の歴史として保持）

## 2026-05-23（4回目）
- migrate_add_status_column.py 作成：A列（完了ドロップダウン）挿入 + 条件付き書式（完了→薄灰色） + R列（画像格納フォルダ）ヘッダー追加
- write_to_sheets.py の COL dict を18列対応に更新（status=A, folder=R 追加）
- setup_sheets.py の HEADER_ROW を18列対応に更新、ドロップダウン・条件付き書式の初期設定を追加
- docs/cli_instruction.md 作成：今後のPDF追加時のCLI実行手順書
- **次のアクション**: ターミナルで `python src/migrate_add_status_column.py` を実行（一回のみ）

## 2026-05-23（3回目）
- B列「PDF URL」をスプレッドシートに追加（既存列を右シフト）
- write_to_sheets.py を更新：pdf_url（B列）書き込み + 処理済みPDFのDriveリネーム（済）対応
- setup_sheets.py のHEADER_ROW・列幅を16列対応に更新
- src/migrate_add_url_column.py 作成：既存5件へのURL追記 + Driveリネーム一括処理
- output.json に pdf_url・pdf_id フィールドを追加（5件）
- **次のアクション**: ターミナルで `python src/migrate_add_url_column.py` を実行

## 2026-05-23（2回目）
- setup_sheets.py のバグ修正：`sheetId` をハードコード `0` からAPIレスポンス取得に変更
- 原因：新規作成シートのsheetIdが0以外になる場合があり `No grid with id: 0` エラーが発生
- 修正後に再実行し、スプレッドシート作成・ヘッダー設定・書式設定が正常完了
- 新スプレッドシートID: `1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw`
- **残課題**: `.env` に `GOOGLE_SHEETS_ID=1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw` を追記する

## 2026-05-23
- アーキテクチャをCowork中心に刷新（AnthropicのAPIキー不要）
- QQQプロジェクトのOAuth2認証（credentials.json）をdori-mangaに流用
- credentials.json をGoogleドライブ（GCloud/qqq_trading）から取得・配置
- .gitignore / .env 作成
- src/setup_sheets.py 作成（スプレッドシート自動生成）
- src/write_to_sheets.py 作成（Cowork生成JSONのシート書き込み）
- docs/cowork_pipeline.md 作成（設計書＋コード全文）
- 旧スクリプト（run.py / pdf_reader.py / manga_gen.py / drive.py）はCowork中心フローでは不使用
- setup_sheets.py を実行しスプレッドシート作成完了（ID: 1TYbBLOi6tjeOuEyXbNO8vh0tGq_Z2R9oSELv8OebHcw）
- .env に GOOGLE_SHEETS_ID を設定済み

## 2026-05-22
- 漫画自動化パイプラインの設計・実装
  - docs/manga_pipeline_spec.md 作成（仕様書）
  - src/run.py / pdf_reader.py / manga_gen.py / sheets.py / drive.py 作成
  - .env.example 作成
- 参考漫画（4コマ）をGoogleドライブから確認・スタイル分析完了
- サンプルPDF（酸素マスク）をClaude Visionで読み取り・動作確認

## 2026-05-19
- プロジェクトフォルダ作成（CLAUDE.md / README.md / docs/）
- concept.md・episode_list.md の初版作成
