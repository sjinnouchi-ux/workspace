# dori-manga DB格納機構 改定案 v2（Web管理画面版）

作成日：2026-07-02
前版からの変更：入口をCLI→**Web管理画面**に変更（奥様のMacからブックマークで利用）
※ 本書はv2時点の設計経緯ドキュメント。最新仕様は codex-handoff-v3.md を正とする。

---

## 1. 前提（2026-07-02 陣内さんヒアリング）

- 画像生成とDB格納の実作業は**奥様のMac**で行われている
- cmd操作は不可 → **パスワードログインのWebページ**をブックマークして使う
- 奥様はこの管理画面を**2日に1度は必ず触る** → keepaliveは画面アクセスで兼ねる
- Driveの1次保存→OK/NG/CLOSEフォルダ振り分けは**現状のままスムーズ**（システム化しない）
- 将来的に、現在未入力のカラム情報を管理画面から奥様が入力できるようにしたい
- 利用頻度は週20回程度

## 2. 全体アーキテクチャ

```
奥様のMac（ブックマーク）
  → 管理Webページ（Cloudflare Pages・無料）
      ├─ ログイン：パスワード1つ入力（裏側はSupabase Auth）
      ├─ 📊 ダッシュボード
      │    ・DB稼働状況（休止していないか）／最終登録日時
      │    ・ページを開くだけでDBに読み取りが走る＝keepalive
      ├─ 📥 インポートフォーム
      │    ・Drive画像URL／コマ番号／OK・NG・CLOSE／JSON貼り付け
      │    ・任意入力：エピソードのテーマ、コマの内容説明 等（未活用カラムを活用）
      │    → Supabase RPC import_generation_attempt（トランザクション・冪等）
      ├─ 📚 履歴一覧：generation_attempts / prompt_lessons の閲覧
      └─ （将来）採用画像マーク・制作進捗の更新

GAS・スプレッドシート「画像格納」シート → 廃止
Drive振り分け → 現状維持（手動）
```

## 3. Cloudflareの料金

- **かからない。** Cloudflare Pagesの無料枠は静的ページ配信が実質無制限、
  サーバー処理（Functions）を使う場合も10万リクエスト/日まで無料
- 週20回の利用は無料枠の0.01%未満

## 4. ログイン方式の設計

- **採用：見た目は共有パスワード1つ、裏側はSupabase Auth**
  - ページにはパスワード入力欄が1つだけ。メールアドレスはページ内に固定埋め込み
  - 入力されたパスワードでSupabase Authにログイン → セッションが保存され、次回以降は自動ログイン
  - RLSと連動し、**ログインしていない人はDBに一切触れない**
  - 追加コスト0円・追加インフラ不要
- **不採用：ページ内にパスワードを埋め込む純粋な簡易方式**
  - 静的ページはソースが誰でも見られるため、埋め込んだ合言葉やキーは実質公開になる

## 5. カラム整理（v2時点の決定）

| カラム | 決定 | 理由 |
|--------|------|------|
| `generation_attempts.folder_status` | **削除済み** | 全18件で`result_status`と完全一致。二重管理はズレの温床 |
| `manga_episodes.theme` | 残す | 任意入力欄として活用 |
| `manga_panels.scene_text` | 残す | コマの内容説明として活用 |
| `manga_panels.target_prompt` | 残す | 将来のプロンプト管理用 |
| `manga_panels.selected_attempt_id` | 残す | 「この画像を採用」機能用 |
| `manga_episodes.status` / `manga_panels.status` | 残す | 制作進捗管理用（v3で3種に変更） |
| `characters.reference_image_url` | 残す | 参考画像表示用 |

## 6. keepaliveの考え方

- 基本は**画面アクセス（2日に1度）で維持**される
- ダッシュボードに稼働状況を見える化
- 保険としてGitHub Actions版keepalive（2日おきping・失敗時メール通知）を標準装備
  - 費用無料（publicリポジトリはActions無制限。このジョブは月1分未満）

## 7. v2で適用済みのSupabase変更

- migration `drop_folder_status_column`
- migration `rls_policies_authenticated_read`
- migration `import_generation_attempt_rpc_v2`（冪等性テスト済み）
- Authユーザー作成：s.jinnouchi@yumekango.com（パスワードは陣内さん管理）
