# Codex引き継ぎ書 v3：どり漫画 管理画面 全面改訂

作成日：2026-07-02
作成者：Claude（設計担当）／実行者：Codex（実装足軽）
対象リポジトリ：https://github.com/sjinnouchi-ux/workspace（main）
**本書は前回の `codex-handoff-webapp.md`（v2）を全面的に置き換える。v2未着手ならv2作業は不要。**

---

## 0. 最重要：作業の進め方（Claude確認ゲート）

- 作業はPhase 0〜4に分割されている。**各Phaseの完了時にClaude確認ゲートがある**
- 確認の方法：Codexは `docs/reports/` に確認依頼MD（例: `2026-07-XX-v3-phase0-review.md`）を作成しpush → 陣内さんがCowork上のClaudeに共有 → **Claudeの承認を得てから次Phaseへ進む**
- 確認依頼MDには「実施内容・変更ファイル一覧・判断に迷った点・次Phaseの予定」を箇条書きで記載すること

## 1. 背景・決定事項（2026-07-02 陣内さん確定）

- スプシ・GAS・Driveの三重管理を廃止し、**Web管理画面＋Supabase DBに一元化**する
- 運用者は陣内さんの妻（Mac・ブックマーク・パスワードログイン・cmd不可）
- 管理画面は**3タブ**：制作／インポート／管理（将来タブ追加可能な構造にする）
- Driveの新ルートフォルダを新設し、過去分は陣内さんが手動移行（移行スクリプト不要）
- 費用は無料枠内で構成（Cloudflare Pages・Supabase Free・Edge Functions・GitHub Actions）

## 2. Claude実施済み（Supabase側・再実行禁止）

プロジェクト：vdntqwtywxyjxelycavx（dori-manga）。以下のmigrationは**適用・検証済み**。

| migration | 内容 |
|-----------|------|
| `drop_folder_status_column` | 冗長カラム削除（v2） |
| `rls_policies_authenticated_read` | 全テーブルselect許可（v2） |
| `import_generation_attempt_rpc_v2` | 画像評価インポートRPC（トランザクション・冪等） |
| `v3_episodes_production_columns` | episodes に post_text / pdf_url / drive_folder_id / drive_folder_url / is_working 追加。**status を「完成・未完成・不採用」の3種に変更**（default 未完成）。app_settings テーブル新設（drive_root_folder_id / drive_root_folder_url） |
| `v3_rls_write_policies_and_rpc` | episodes / panels / prompt_templates / app_settings に authenticated の書き込みポリシー追加。`create_episode_with_panels(p_title)` RPC 新設（episode＋コマ1〜4一括作成・重複拒否） |
| `v3_seed_evaluation_prompts` | prompt_templates に「評価プロンプト_OK / _NG / _CLOSE」3件を初期登録。分析用ビュー `v_ok_prompts` 新設 |

- Authユーザー：`s.jinnouchi@yumekango.com` 作成済み（パスワードは陣内さん管理・**記録禁止**）
- 現データ：generation_attempts 18件 / prompt_lessons 55件 / episodes 1件（未完成）/ panels 4件

## 3. システム構成

```
妻のMac（ブックマーク）
  → 管理画面（Cloudflare Pages / dori-manga/webapp/index.html）
      ├─ ログイン：Supabase Auth（メール固定・パスワード入力のみ）
      ├─ 読み書き：supabase-js（anonキー＋RLS）＋ RPC
      └─ Drive操作：Supabase Edge Functions 経由
            ├─ create-episode-folder（フォルダ自動作成）
            └─ upload-image（画像アップロード＋判定フォルダ振り分け）
                 └─ Googleサービスアカウント（secretsに格納）
GitHub Actions：2日おきkeepalive（失敗＝休止をメール通知）
```

## 4. 仕様

### 4.1 画面仕様（3タブ）

共通：v2の `index.html`（同梱）を土台に拡張。ピンク基調（#D4537E系）。タブは配列定義で増設可能な構造にする。デモ確定版のUI挙動は本章の通り（陣内さん承認済み）。

**制作タブ**
- エピソード一覧（スプシ代替）。列：✅ / タイトル / 状態 / 1〜4コマ案 / 投稿案 / PDF URL。横スクロール可
- セル（コマ案・投稿案・PDF URL）は直接編集し、**フォーカスアウトでDBに自動保存**（panels.scene_text / episodes.post_text / episodes.pdf_url）
- 状態はプルダウン（完成・未完成・不採用）→ episodes.status に即保存
- フィルターボタン：すべて／完成／未完成／不採用（件数表示付き）
- ✅チェック：episodes.is_working を更新（同時に1件のみtrue）。インポートタブの作品初期選択に連動
- 「新しい漫画を作る」→ タイトル入力 → ①RPC `create_episode_with_panels` ②Edge Function `create-episode-folder` を順に呼び、一覧に反映
- CSVインポート／エクスポートボタン（仕様は4.2）

**インポートタブ**
- 上部：評価プロンプトコピーボタン3種（OK/NG/CLOSE）。押下時にDBの prompt_templates（評価プロンプト_OK/_NG/_CLOSE）から**最新を取得して**クリップボードにコピー
- フォーム：作品（is_working=trueが初期選択）／コマ番号（1〜4）／判定（OK/NG/CLOSE）／画像ファイル選択（`<input type="file" accept="image/*">`）／ChatGPT JSON貼り付け
- 登録処理：①クライアント検証（JSONパース・判定不一致confirm）②Edge Function `upload-image` で画像を判定フォルダへアップロード ③RPC `import_generation_attempt` にJSON＋image_url/drive_file_id/panel_number/episode_titleを渡す ④duplicate応答時は警告表示（画像は残るが実害なしと表示）
- 登録後：履歴・集計を再読込

**管理タブ**
- システム状態：Supabase疎通（selectが通るか）／最終DB登録日時／keepalive案内
- **Drive親フォルダ：app_settings の drive_root_folder_url をリンク表示**（クリックでDriveが開く）。初期設定用の入力欄＋保存ボタンも設置（root URL/IDを登録できるように）
- 集計：作品数／完成／未完成／不採用／画像評価数／改善ルール数
- 評価プロンプト登録：OK/NG/CLOSE の3欄（textarea＋保存）→ prompt_templates を update
- CSVテンプレートダウンロードボタン

### 4.2 CSV仕様

- 列：`タイトル,状態,1コマ案,2コマ案,3コマ案,4コマ案,投稿案,PDF URL`
- エクスポート／テンプレートとも **UTF-8 BOM付き・CRLF・全フィールド引用符囲み**（スプシ/Excel両対応）
- インポートは**スプシの「CSVダウンロード」出力を正とし**、RFC4180準拠でパース（引用符内のカンマ・改行・""エスケープ対応。自前実装かPapaparse CDN利用）
- **状態列は4値：`新規作成` / `完成` / `未完成` / `不採用`**（2026-07-02 陣内さん確定）
  - `新規作成`：episode新規登録（`create_episode_with_panels`）＋ **Driveフォルダ自動作成**（`create-episode-folder`）。DB上のstatusは「未完成」で登録。**既存タイトルと一致した場合はスキップして報告**（タイプミスによる重複作成防止）
  - `完成`/`未完成`/`不採用`：既存タイトルの**更新のみ**。タイトルが見つからない場合はスキップして報告（誤記で勝手にフォルダが生えるのを防止）
  - 空欄・その他の値：スキップして報告
- テンプレートの記入例行は状態=`新規作成`とする（初期移行の主用途のため）
- 取込結果サマリ（新規作成n件〔フォルダ作成済み〕・更新n件・スキップn件＋理由）を画面表示
- 新規作成が複数行ある場合、フォルダ作成は1件ずつ順次実行し、進捗を画面表示（Edge Functionの連続呼び出し）

### 4.3 Edge Functions仕様（Deno / supabase/functions/）

共通：JWT検証あり（authenticatedユーザーのみ）。サービスアカウントJSONは `supabase secrets set GOOGLE_SERVICE_ACCOUNT_JSON=...` で格納。Google認証はjose（esm.sh）でJWT署名→OAuthトークン取得。ルートフォルダIDは app_settings から取得。

**create-episode-folder**
- POST `{ episode_id, title }`
- 処理：ルート直下に `<title>/` と子フォルダ `OK/ NG/ CLOSE/ 完成/` を作成 → episodes.drive_folder_id / drive_folder_url を更新
- 応答：`{ status, folder_id, folder_url }`。同名フォルダ既存時は再利用（エラーにしない）

**upload-image**
- POST `{ episode_id, result_status, file_name, content_base64 }`
- 処理：episodeのフォルダ配下の判定サブフォルダ（OK/NG/CLOSE）へアップロード
- 応答：`{ status, file_id, web_view_link }`
- 制限：base64膨張を考慮し**10MB超の画像はクライアント側で弾いて案内**を表示

### 4.4 DBスキーマ現況（v3適用後の要点）

- manga_episodes：title / theme / status(完成・未完成・不採用) / post_text / pdf_url / drive_folder_id / drive_folder_url / is_working
- manga_panels：episode_id / panel_number(1-4) / scene_text（=コマ案）/ target_prompt / selected_attempt_id / status
- generation_attempts：panel_id / attempt_number / image_url / drive_file_id / file_name / result_status / final_generation_prompt / evaluation_summary / evaluation_json
- prompt_templates：評価プロンプト3種を含む / prompt_lessons / characters / app_settings(key-value) / view: v_ok_prompts（Cowork/Codex定期分析用）

## 5. Codex作業工程

**Phase 0：リポジトリ整理・ドキュメント配置**
1. 本書を `dori-manga/docs/handoff/codex-handoff-v3.md` に配置。旧 `codex-handoff-webapp.md` が配置済みなら同フォルダに `_superseded` を付けて残す
2. 同梱の `supabase-keepalive.yml` → `.github/workflows/`、`db-import-redesign-v2.md`・`webapp-setup.md` → `dori-manga/docs/supabase/`
3. 旧GAS `dori-manga/gas/` → `dori-manga/gas/_retired/` へ git mv
4. `dori-manga/docs/work_log.md` に本改訂の経緯を追記（2. の実施済みmigration一覧を含める）
5. GitHub Secret `SUPABASE_ANON_KEY` 登録（gh CLI可なら実行、不可なら人間タスクに回す）＋ keepalive手動実行で緑✅確認
6. commit → push
→ **✅ Claude確認①：リポジトリ構成とwork_logのレビュー**

**Phase 1：Edge Functions実装（コードのみ・デプロイしない）**
1. `dori-manga/supabase/functions/create-episode-folder/index.ts` と `upload-image/index.ts` を4.3の仕様で実装
2. エラー応答は日本語メッセージで統一（画面にそのまま表示するため）
3. commit → push
→ **✅ Claude確認②：コードレビュー（認証・秘密情報の扱い・Drive APIの呼び方）**

**Phase 2：Drive連携の疎通（人間タスク含む）**
1. 【人間】GCPでサービスアカウント作成 → Drive API有効化 → キーJSON取得
2. 【済】親フォルダは作成・登録済み（2026-07-02 Claude実施）：
   - ID `11UK7BKd-pcWW7eQSDghbkJxjxJa34Dbz` を app_settings に登録済み
   - 【人間】サービスアカウント作成後、そのメールアドレスに**編集者権限で共有**すること
   - 【人間】リンク共有（リンクを知っている全員が編集可）になっている場合は、サービスアカウント共有後に**制限付きへ戻す**（セキュリティ上の推奨）
3. 【Codex】`supabase functions deploy` ＋ `supabase secrets set`（Supabaseアクセストークンは人間が用意）
4. 【Codex】curlでJWT付き疎通テスト（テストフォルダ作成→削除）
→ **✅ Claude確認③：疎通結果と作成されたフォルダ構造のレビュー**

**Phase 3：webapp v3実装**
1. `dori-manga/webapp/index.html` を4.1の仕様で全面改訂（同梱のv2版を土台に。定数：SUPABASE_URL / anonキー / LOGIN_EMAIL=s.jinnouchi@yumekango.com は流用）
2. 単一HTMLファイル構成を維持（ビルド工程を作らない）
3. commit → push
→ **✅ Claude確認④：コードレビュー（保存タイミング・CSVパーサー・二重登録防止）**

**Phase 4：デプロイ・検収**
1. Cloudflare Pagesへデプロイ（wrangler。初回は `npx wrangler pages project create dori-manga-admin`）
2. 7章の検収チェックリストを実施し、結果を `docs/reports/` にMDで記録
3. work_log更新 → push
→ **✅ Claude確認⑤：最終検収。承認後、陣内さんの移行作業（6章）へ**

## 6. 人間（陣内さん）の残作業

- Phase 2のGCP設定・サービスアカウントへの親フォルダ共有（手順の詳細はPhase 2でCodexが具体化）
- 過去作の一括登録：管理タブのテンプレート → スプシで記入 → CSVインポート（状態=新規作成）
- 過去画像の新Driveフォルダへの手動移動
- 旧GASの後片付け（スプシメニューからトリガー停止、スクリプトプロパティのservice_roleキー削除）
- 奥様へのURL・パスワード共有と操作説明

## 7. 検収チェックリスト

1. ログイン→3タブが表示される
2. 制作：セル編集→リロードしても保持（DB保存確認）／状態変更とフィルター連動／✅→インポートタブ初期選択連動
3. 新規作成→Driveに「親フォルダ/タイトル/OK・NG・CLOSE・完成」が生成され、一覧にフォルダリンクが付く
4. CSV：テンプレDL→スプシ記入→CSV出力→インポートで「新規作成」行のepisode登録＋Driveフォルダ自動生成、「完成/未完成/不採用」行の更新、未知タイトルのスキップ報告が正しく動く（セル内改行含むケースで確認）
5. インポート：プロンプトコピー3種が動作／画像選択→登録で判定フォルダに画像が入りDBに1件登録／同一コマ×試行回数の再登録でduplicate警告
6. 管理：稼働状況・集計・**親フォルダURLリンク**・プロンプト編集保存→コピーボタンに反映
7. keepalive：Actions手動実行が緑✅

## 8. 禁止・注意事項

- Supabaseのmigrationは適用済み。**SQLの再実行・スキーマ変更をしない**（変更が必要と判断したら確認依頼MDでClaudeに相談）
- service_roleキー・サービスアカウントJSON・ログインパスワードを**コード・ログ・チャットに書かない**（secrets/環境のみ）
- anonキー（sb_publishable_...）は公開前提のため埋め込み可
- 単一HTML構成・無料枠構成を崩さない（ビルドツール・有料サービスの導入はClaude相談事項）
