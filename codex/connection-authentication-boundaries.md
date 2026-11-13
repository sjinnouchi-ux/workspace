# 接続・認証境界の確認

PR16の誤判定防止方針を、現行の[承認方針](AGENT_APPROVAL_POLICY.md)と[起動手順](CODEX_DESKTOP_STARTUP.md)へ合わせて採用しました。これは個別サービスの現在の接続成功を示す監査表ではありません。

| 対象 | 確認する境界 | 代用しない確認 |
|---|---|---|
| Apps connector | 現在の接続toolと対象resource・既存権限 | ローカルCLI、別browser、mapped drive |
| ローカルCLI・desktop sync | 実行host/user、PATH、credential owner、対象consumer | sandbox userや別PCでの否定結果 |
| local/host MCP | 当該host/userの設定と現在利用可能なtool | Apps接続や別hostの設定 |
| hosted plugin MCP | 当該plugin/Appの有効状態と接続権限 | ローカルMCP一覧 |
| browser | 使用するbrowser/profileと対象サービスのsession | 別browserやconnectorの成功 |
| Remote/SSH | 接続先host/userとそこで使用する経路 | 操作元PCのcredential・PATH |

## 判断の順序

1. 実際に使うsurface、host、user、credential owner、対象を確定する。
2. 既存の接続と許可された最小read-only操作で確認する。秘密値や認証途中URLを表示しない。
3. 成功はその機能・対象・時点のCONNECTEDとして記録する。正しい境界で未認証・権限不足等を確認した場合だけ、その対象のDISCONNECTEDとする。
4. 別user/host/profile、tool未露出、network/sandbox制約等で判定できなければINCONCLUSIVEとする。未接続やcredential消失へ置き換えない。
5. 追加の本人操作や変更が必要な場合は、実際の要求と根拠に従う。既承認の同じread-only確認を重複承認待ちにしない。

sandbox userでのCLI/keyring/OAuth cache/mapped driveの失敗だけを理由に、logout、disconnect、credential削除、OAuth/token再発行、認証JSONコピーを行いません。許可された通常hostで確認できても、プラットフォームの安全停止や権限拒否を別経路で迂回しません。

toolの追加、再接続、再起動が必要かは実際のsurfaceと利用可能なtoolで確認し、一律に新規chatや再起動を要求しません。スマホ起点browserの既知の扱いは[起動手順](CODEX_DESKTOP_STARTUP.md#mobile-origin-browser-recovery)を参照します。

## 旧PRの扱い

2026-07-14の接続監査は当時の観測です。PR16の旧GitHub確認script、frontend-design、出典・licenseと全15原版の固定参照は[保存索引](../docs/history/workspace-pr-cleanup-2026-11-13/README.md)へ保持しました。旧scriptの現役配置、各PCへのskill install、local設定同期、サービスの再認証は今回行っていません。
