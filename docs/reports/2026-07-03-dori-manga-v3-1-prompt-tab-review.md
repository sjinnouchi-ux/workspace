# どり漫画DB 管理画面 v3.1 プロンプトタブ確認依頼

作成日: 2026-07-03

Claude設計書 `codex-handoff-v3-1-prompt-tab.md` に基づき、プロンプトタブ追加を実装しました。

## 対象

- 本番URL: https://dori-manga-admin.pages.dev/?v=prompt-tab-final
- マニュアルPDF: https://dori-manga-admin.pages.dev/dori-manga-admin-manual.pdf?v=prompt-tab-final
- Cloudflare Pages project: `dori-manga-admin`

## 実装内容

- 4タブ構成へ変更
  - 制作
  - インポート
  - プロンプト
  - 管理
- `prompt_gallery` 一覧表示
  - `created_at` 降順
  - 件数表示
  - タイトル部分一致検索
- プロンプト登録フォーム
  - タイトル必須
  - プロンプト必須
  - 参考画像任意
  - 画像選択時プレビュー
- 画像処理
  - 長辺1280pxへブラウザ側リサイズ
  - JPEG品質0.8
  - 5MB超過時は品質0.6で再試行
  - 保存パスはUUIDベース `{uuid}.jpg`
  - Storage bucket `prompt-gallery` へアップロード
  - public URLを `image_url` に保存
- 一覧カード操作
  - 画像クリックで拡大/戻す
  - コピー
  - タイトル・プロンプトの直接編集と自動保存
  - confirm後の削除
  - DB削除後、Storage画像も削除

## マニュアル更新

- `dori-manga/docs/manuals/dori-manga-admin-user-manual.md` に「プロンプトタブ」章を追加。
- 以下を困ったときへ追記。
  - Supabase疎通NG時は聡さんに連絡
  - 画像は10MBまで
  - プロンプトタブ画像は自動縮小
  - パスワード忘れは聡さんがリセット
  - Drive振り分けは自動
- `dori-manga/webapp/dori-manga-admin-manual.pdf` を再生成。

## 検証結果

- `index.html` インラインJavaScript構文チェック: 成功
- Supabase `prompt_gallery` REST読み取り: status `200`
- 本番URL HTTP: status `200`
- 本番PDF HTTP: status `200` / `application/pdf`
- 本番ブラウザ:
  - ログイン済み状態で4タブ表示を確認
  - プロンプトフォーム表示を確認
  - マニュアルリンク表示を確認
  - コンソールエラー0件
- ブラウザ実操作:
  - 画像なし登録: 成功
  - カード表示: 成功
  - タイトル・プロンプト編集保存: 成功
  - タイトル検索: 成功
  - テストデータ削除: API補助で残数0確認
- 画像あり相当:
  - Storage `prompt-gallery` upload: `200`
  - DB insert: `201`
  - DB delete: `204`
  - Storage delete: `200`
  - DB残数: `0`

## 注意点

- 自動ブラウザ操作ではクリップボード書き込みがブラウザ権限で拒否されました。実装は既存 `copyText()` と同じ導線で、HTTPS本番・人間クリック前提です。
- ブラウザ操作APIではファイル選択の自動投入が制限されるため、画像あり登録はStorage/API疎通で代替確認しました。

## 変更ファイル

- `dori-manga/webapp/index.html`
- `dori-manga/docs/manuals/dori-manga-admin-user-manual.md`
- `dori-manga/webapp/dori-manga-admin-manual.pdf`
- `dori-manga/docs/work_log.md`
- `docs/reports/2026-07-03-dori-manga-v3-1-prompt-tab-review.md`

## Claude確認依頼

- 仕様3章・4章の実装漏れがないか
- コピー導線が既存 `copyText()` 再利用で妥当か
- 画像あり登録の自動検証制約とAPI代替確認で受け入れ可能か
- v3.1として追加対応すべき残件があるか
