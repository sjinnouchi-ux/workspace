# Kアラート・テスト版 破棄記録

作成日: 2026-07-09

## 要点

- 過去にKアラートのテスト版が存在した。
- テスト版の詳細なコード、GAS、Google Sheets、Worker、LIFF、LINE設定、作業ログはGit管理から削除する方針に変更した。
- 現行のKアラート開発・運用は、Kアラート本番開発リポジトリを正本とする。

## Git上の扱い

- 旧テスト版の実装ディレクトリは削除済み。
- テスト版の詳細ハンドオフ、実装手順、旧URL、旧ID、旧シート/GAS参照は正本として扱わない。
- 今後Kアラートで作業する場合は、まず `sjinnouchi-ux/k-alert-production` を確認する。

## 外部ファイル

テスト版のGoogle Sheets、Apps Script、Drive上の詳細ハンドオフは破棄対象。
Google Driveコネクタでは、対象のGoogle Sheets、Apps Script、Drive上の詳細ハンドオフの読み取りはできたが削除権限が不足していた。
ローカルGoogle Drive同期フォルダ内の詳細ハンドオフMDと一時確認用リッチメニュー画像は削除済み。

2026-07-09、`s.jinnouchi@yumekango.com` のApps Script画面で、過去テスト版のApps Scriptプロジェクト2件を削除した。うち1件はゴミ箱から完全削除し、Apps Scriptの自分のプロジェクト一覧とゴミ箱に `Kアラート` を含むプロジェクトが残っていないことを確認した。
