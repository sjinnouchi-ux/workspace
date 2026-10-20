# market-pilot退役（2026-10-21）

利用者は再開しないこと、GitHub repoと専用Supabaseの削除を明示。DBが他用途に転用されていないか先に確認する条件付き。

## 専用DB確認

旧専用project refはcoeepfbfvtkwgtnmzwtz。管理ターミナルの[2026-07-06削除記録](https://github.com/sjinnouchi-ux/mgmt-terminal/blob/main/docs/reports/2026-07-06-phase1-environment-setup-log.md)に同refの削除成功が記録されている。今回も旧refのdashboardは組織一覧へ戻り、Yumekango組織に残るprojectはmgmt-terminalとreusable-supabaseの2件だった。後者は会議議事録系統であり削除対象ではない。

旧DBは既に存在しないため内容の再閲覧はできない。未確認の現存DBを専用DBと推測して削除しない。GitHubの同ref検索7件もmarket自身と過去管理記録のみで、現在の他用途DBへの転用は確認されなかった。Supabaseの追加削除操作は不要・未実施。

## GitHub

削除前main: 7f81ff0c0866ded01f1ff50e61df2faebb0dbe7d。コードと14テーブルのschemaはいずれも市場データ・シグナル・注文・risk管理用途。別プロジェクトへの転用は検出せず。repoは非archive状態、所有者のadmin権限を確認。CLI削除はdelete_repo scope不足で403となり未実行。ブラウザで同repoの削除最終画面まで準備済み。ブラウザ操作規則の恒久削除時確認を待っており、repoはまだ存在する。その後、利用者の実行直前承認を受領して削除ボタンを実行したが、GitHubのConfirm access（本人の認証コード入力）が要求された。本人認証待ちで削除成功は未確認。認証後に結果を追記する。

他PCの旧cron等は全数確認しておらず、全外部resourceの消去完了とはしない。今回対象は利用者指定のrepoと旧専用Supabaseに限定する。
