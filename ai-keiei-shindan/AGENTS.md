# AGENTS.md

このディレクトリは「AI経営実装度診断WEBアプリ」のプロジェクトGit領域です。

## 作業開始時

1. ルート `PROJECTS.md` でこのプロジェクト行を確認する。
2. `PROJECT_BRIEF.md`、`DESIGN_LOG.md`、`IMPLEMENTATION_LOG.md` を読む。
3. 仕様は `docs/specs/README.md` に列挙した正本を確認する。
4. 実装前に `ai_keiei_shindan_app_spec.md` と `ai_keiei_shindan_web_impl_spec.md` の両方を読む。片方が未確認なら実装を止めて質問する。

## 実装ルール

- 初回スコープは単一 `index.html`、GAS、Googleスプレッドシート、GitHub Pages公開まで。
- 外部フレームワーク、CDN、新規課金、新規サービス登録は使わない。
- 秘密情報、`.env`、GAS/Googleの実値トークンはGitHub、Markdown、チャットに保存しない。
- Google系作業は `s.jinnouchi@yumekango.com` を使う。
- 結果文言、質問、選択肢、判定仕様はロジック仕様書を正とする。
- 実装完了・検証完了ごとに `IMPLEMENTATION_LOG.md` を更新する。

