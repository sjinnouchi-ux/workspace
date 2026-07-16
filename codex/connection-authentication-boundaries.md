# Codex接続・認証境界の確認手順

Last verified: 2026-07-14 (JST)

## Purpose

Codexの隔離shell、実Windowsユーザー、Apps connector、MCP、ブラウザ、Remote/SSHは、同じPC上でも別の認証・実行境界を持ちます。別経路の失敗を流用して「未接続」と誤判定しないため、本書を共通診断手順とします。

## Status model

接続確認結果は次の3値で記録します。

| State | Meaning |
|---|---|
| `CONNECTED` | 対象機能を所有する正しい境界で、必要なread-only疎通を確認した |
| `DISCONNECTED` | 正しい境界で、未認証、権限不足、または接続解除を確認した |
| `INCONCLUSIVE` | 別user、別host、別profile、別surface、tool未露出、network制限などにより正式判定できない |

`INCONCLUSIVE`を`DISCONNECTED`へ読み替えてはいけません。

## Connection classes

| Class | Examples | Authoritative check | Checks that must not be substituted |
|---|---|---|---|
| SaaS App connector | GitHub App、Google Drive / Docs / Sheets / Slides | 現在のChatGPT/Codex surfaceでpluginとAppが有効か、connector自身のprofileまたは最小read-only tool、provider側identityと対象resource ACL | ローカル`gh`、`gcloud`、`clasp`、`G:`、通常Chromeのログイン状態 |
| Local CLI / desktop sync | `gh` / Git、`gcloud` / ADC、`clasp`、Google Drive for desktop | 実Windowsユーザーと実際のinteractive sessionで各CLI/statusまたは同期clientを確認 | `codexsandboxoffline`でのkeyring、mapped drive、OAuth cacheの失敗 |
| Local or host MCP | Search Console、GA4、custom STDIO/HTTP MCP | 対象Codex host/user/`CODEX_HOME`、MCP enabled、OAuth/env/header、必要なrestart後の`/mcp`またはtool probe | ChatGPT Apps接続、別hostの`config.toml`、別taskのtool一覧 |
| Hosted plugin MCP | pluginに同梱されたremote MCP | plugin/App側のinstall、enable、connector auth、workspace policy | ローカル`codex mcp list`やローカル`config.toml` |
| Browser bridge | built-in Browser、Chrome plugin / extension | 対象browser profile、extension/native host、plugin on、新しいtask | Apps connector、別browser profile、通常Chromeとbuilt-in Browserの相互流用 |
| Remote / SSH | Remote Control、SSH project | 接続先hostのuser、credentials、plugins、MCP、browser、PATH | 操作元PCのCLI、keyring、browser session |
| Skill-only plugin | filesystem skill、instructions-only plugin | installed/enabled、適用scope、新しいtask/session | 外部serviceのOAuth。外部Appを同梱する場合だけconnector境界を追加する |

## Standard diagnostic order

1. 検証対象を上表のclassへ分類する。
2. surface、Codex host、local/remote、task、実行user、`CODEX_HOME`を確定する。
3. plugin/App/MCP/extensionがinstalledかつenabledで、workspace policyまたはRBACに許可されているか確認する。
4. pluginは新しいtask/session、local MCPは必要なrestart後にtoolが露出するか確認する。
5. 所有境界で認証を確認する。connectorはApps、local MCPはMCP Authenticate/`codex mcp login`、CLIは実user、Chromeは同一profile、Remoteはremote hostを使う。
6. 接続identityが対象repository/file/site等のprovider ACLを持つか、最小read-only probeで確認する。
7. 最後にruntimeのsandbox、network、approvalを確認する。shell network failureをconnector failureへ読み替えない。
8. 結果を`CONNECTED`、`DISCONNECTED`、`INCONCLUSIVE`のいずれかで記録する。

## Mandatory safety rules

- `whoami`が`codexsandboxoffline`等の隔離userを示す場合、OS keyring、Windows資格情報、user別OAuth cache、mapped driveの否定結果は`INCONCLUSIVE`とする。
- 隔離userや別hostの失敗だけを理由に`gh auth logout`、connector disconnect、OAuth/token再発行、credential削除、認証JSONのコピーを行わない。
- status確認ではtoken、OAuthコード、認証JSON、cookie、`.env`、生ログを出力しない。
- connectorの接続確認に、同じproviderの別製品CLIを使用しない。Google Drive connectorを`gcloud`や`clasp`で判定しない。
- toolが現在のtaskにない場合は、新しいtask、plugin enable、restart、workspace policyを確認するまで未認証と断定しない。
- App/CLI間やdesktop/CLI/IDE間に仕様差があり得るため、実際のsurfaceとversionを記録する。

## GitHub CLI guard

GitHub CLI/Gitの確認には[`scripts/Test-GitHubConnection.ps1`](./scripts/Test-GitHubConnection.ps1)を使用します。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\codex\scripts\Test-GitHubConnection.ps1 -RequireWrite
```

- 隔離userではGitHubへ問い合わせず`INCONCLUSIVE`、exit `2`で停止します。
- 実userでは`gh auth status`を非表示で確認し、loginとrepo permissionだけを出力します。
- tokenは取得・表示しません。

Codexから実user確認が必要な場合は、このscriptだけを対象に承認付き実行し、承認範囲を広げません。

## Google Drive verification

Google Drive pluginはunified Drive connectorを正本として確認します。

1. Google Drive pluginがinstalled/enabledであることを確認する。
2. install/enable直後は新しいtaskを開始する。
3. connectorのprofileまたは最小read-only toolが成功することを確認する。
4. 接続Google identityと対象file/folderのACLを確認する。
5. `G:`等の同期pathは別のlocal desktop clientとして個別確認する。

`G:`が見えないこと、`gcloud`/ADCが未設定であること、Chromeが未ログインであることは、Drive connectorの未接続を意味しません。

## Point-in-time audit: 2026-07-14

秘密情報やprivate contentを出力せず、profileまたは最小read-only probeの成否だけを確認しました。

| Surface | State | Evidence / boundary |
|---|---|---|
| GitHub App connector | `CONNECTED` | connector profileとPR操作が成功 |
| GitHub CLI / Git | `CONNECTED` | 実user `jinnouchi`のkeyring、account `sjinnouchi-ux`、`workspace` ADMINを確認 |
| GitHub CLI from Windows sandbox user | `INCONCLUSIVE` | `codexsandboxoffline`では同じkeyringを正式判定できないことを再現 |
| Git credential helper | `CONNECTED` | 実user側のGitHub専用`credential.https://github.com.helper`を確認。汎用helperだけでは判定しない |
| Google Drive unified connector | `CONNECTED` | connector profile probeが成功。file名・内容は取得していない |
| Google Drive desktop sync path `G:` | `INCONCLUSIVE` | sandbox/承認付きprocessの双方で未観測。connector状態とは無関係で、interactive user sessionで別確認が必要 |
| Google Cloud CLI | `CONNECTED` (host-user CLI) | sandbox userのPATHでは`gcloud`未検出、実userではcommandとactive accountを確認。account文字列・tokenは出力していない |
| Google Application Default Credentials | `INCONCLUSIVE` | credential fileの存在だけは確認したが、有効性・主体・権限は未判定。対象consumerの無害な疎通が必要 |
| Apps Script `clasp` CLI | `DISCONNECTED` (not configured) | sandbox/実userともcommandとuser設定を確認できなかった。必要になるまで再認証やcredential探索は行わない |
| Google Search Console local MCP | `CONNECTED` | 現在のtaskで最小read-only tool probeが成功。site情報は出力していない |
| GA4 local MCP | `INCONCLUSIVE` | 現在のtaskにGA4 toolが露出していない。OAuth失効とは断定せず、host config、enable、restartを確認する |
| Built-in Browser / Chrome plugin | `INCONCLUSIVE` | 現在のtaskにbrowser control toolが露出していない。plugin/extension/profile/new-taskの順で確認する |
| Remote / SSH | `INCONCLUSIVE` | 今回はremote hostを対象にしていない。使用時は接続先hostで再監査する |

## Official references

- [OpenAI: Sandbox](https://learn.chatgpt.com/docs/sandboxing)
- [OpenAI: Windows sandbox](https://learn.chatgpt.com/docs/windows/windows-sandbox)
- [OpenAI: Plugins](https://learn.chatgpt.com/docs/plugins)
- [OpenAI: Apps and connector controls](https://learn.chatgpt.com/docs/enterprise/apps-and-connectors)
- [OpenAI: Model Context Protocol](https://learn.chatgpt.com/docs/extend/mcp)
- [OpenAI: Remote connections](https://learn.chatgpt.com/docs/remote-connections)
- [OpenAI: Authentication](https://learn.chatgpt.com/docs/auth)
- [GitHub CLI: `gh auth setup-git`](https://cli.github.com/manual/gh_auth_setup-git)
