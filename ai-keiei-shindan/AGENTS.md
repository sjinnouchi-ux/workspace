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

## GitHub Actions・検証コストの共通ルール

- 途中の確認は変更範囲に絞り、重い全体テストは統合前に行う。
- 文書・作業記録だけの変更では、原則として重いテストを起動しない。
- 同じコードで成功済みの検証は、新しい変更や失敗調査の必要がなければ繰り返さない。
- テストを省略した場合は、理由と統合前に必要な検証を明記する。
- DB変更は、スキーマ・権限・データ整合性への影響に応じた検証を残す。
- 定期監視・休止防止・本番配備は、テスト削減と混同して停止しない。
- 予算・課金上限は、利用者の明示指示なしに変更しない。

作業開始時に[共通方針](https://github.com/sjinnouchi-ux/workspace/blob/main/codex/GITHUB_ACTIONS_POLICY.md)も読む。必須チェック・既存の承認ルールは維持する。検証済み結果を再利用する場合は対象commit・検証範囲・結果を確認し、今回の変更に適用できることを示す。
