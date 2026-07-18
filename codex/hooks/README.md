# Codexターン停止LINE通知 hook

Codex Desktopの主ターンが停止したとき、公式LINEへ最小限の通知を送るWindows実ユーザー向け `Stop` hookです。既存のデスクトップ通知 `notify = ["codex-computer-use.exe", "turn-ended"]` には触れず、`~/.codex/hooks.json` の `Stop` に専用handlerを1件だけ追加します。`SubagentStop` は設定しません。

## 動作とプライバシー

- Python notifierが受け取るhook入力は65,536 bytesまでです。
- `session_id:turn_id` はSHA-256へ変換し、raw IDを送信・保存・出力しません。
- 送信payloadは `schema_version`、ハッシュ化した `event_id`、JSTの `ended_at`、固定の `host_label` だけです。
- transcript、cwd、model、タスク名、prompt、会話内容は読み取りません。
- bearer token、hook入力、HTTP response body、LINE dataはログへ出しません。
- token取得は5秒、HTTP通信は30秒、hook全体は45秒で打ち切ります。失敗時も終了コード0を返すfail-openで、outbox、daemon、自動retryはありません。2026-07-18の実機再検証でHTTP 15秒でも `TimeoutError` となり、直接実行は18.48秒で終了したため、公開サービスを変えずクライアント側だけに余裕を持たせています。
- ログは時刻とallowlist済みstatus、または例外classだけを `~/.codex/logs/codex_turn_line_notify.log` へ記録します。

## 前提と承認境界

対象はhost `NUCBOX_K8_PLUS`、Windows user `jinnouchi`、Google owner `s.jinnouchi@yumekango.com` です。Python、gcloud、専用service accountのimpersonation権限、live済みの家計簿API endpointが必要です。

`DryRun` は書き込みません。`Apply`、Codex Desktopの再起動、hookの信頼操作、live通知は、対象境界をread-only確認した後に別途明示承認を得て実行します。信頼警告は回避せず、下記のhashとhandler情報を確認してから操作します。

## DryRun

PowerShellでrepository rootから実行します。

```powershell
$Installer = Join-Path (git rev-parse --show-toplevel) 'codex\hooks\install_codex_turn_line_hook.ps1'
$CodexUserDir = Join-Path $env:USERPROFILE '.codex'
$PythonCandidates = @(Get-Command python.exe -CommandType Application -All -ErrorAction Stop | Where-Object {
  $_.Source -notlike '*\Microsoft\WindowsApps\python.exe'
})
if ($PythonCandidates.Count -eq 0) { throw 'Runnable Python was not found' }
$PythonPath = [string]$PythonCandidates[0].Source
& $PythonPath --version
if ($LASTEXITCODE -ne 0) { throw 'Selected Python is not runnable' }
$GcloudPath = (Get-Command gcloud.cmd -CommandType Application -ErrorAction Stop).Source

& $Installer -DryRun `
  -CodexUserDir $CodexUserDir `
  -PythonPath $PythonPath `
  -GcloudPath $GcloudPath
```

出力は `hooks change required` と `notifier install required` の真偽だけです。`hooks.json`、`config.toml`、notifier、log directoryを作成・変更しません。

## Apply

明示承認後だけ実行します。

```powershell
& $Installer -Apply `
  -CodexUserDir $CodexUserDir `
  -PythonPath $PythonPath `
  -GcloudPath $GcloudPath
```

`Apply` はnotifierを `~/.codex/hooks/codex_turn_line_notify.py` へ配置し、所有判定に一致する古いhandlerを除外してから、`Stop` handlerを正確に1件追加します。既存 `hooks.json` を変更するときは同じdirectoryへbackupを作り、一時fileからatomicに置換します。2回目の `Apply` はbyte-idempotentです。他event、他handler、`config.toml` と既存 `notify` は保持します。

## Trust review

`Apply` 後、Codex Desktopを再起動または信頼操作する前に、repository版とinstalled版のhash一致を確認します。

```powershell
$SourceNotifier = Join-Path (git rev-parse --show-toplevel) 'codex\hooks\codex_turn_line_notify.py'
$InstalledNotifier = Join-Path $CodexUserDir 'hooks\codex_turn_line_notify.py'
$SourceHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $SourceNotifier).Hash
$InstalledHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $InstalledNotifier).Hash
if ($SourceHash -cne $InstalledHash) { throw 'Installed notifier hash mismatch' }
"notifier_sha256=$InstalledHash"
```

次のread-only確認はraw hook JSONやcommand全文を表示せず、owned handlerの件数と信頼判断に必要な非秘密leafだけを出します。Codexのcommand-hook schemaでは `command` が必須で、Windowsでは `commandWindows` がoverrideとして使われます。PowerShellはquoted executableを起動するcall operatorが必要なため、installerはportable base commandを `command`、その先頭へ `& ` を付けた値を `commandWindows` に設定します。

```powershell
$Endpoint = 'https://kakeibo-api-570965759130.asia-northeast1.run.app/internal/codex/turn-ended/notify'
$Document = Get-Content -Raw -Encoding UTF8 (Join-Path $CodexUserDir 'hooks.json') | ConvertFrom-Json
$Owned = @($Document.hooks.Stop | ForEach-Object { $_.hooks } | Where-Object {
  $_.commandWindows -is [string] -and
  $_.commandWindows -match '(^|[\\/])codex_turn_line_notify\.py(?:"|\s)' -and
  $_.commandWindows.Contains($Endpoint)
})
if ($Owned.Count -ne 1) { throw "Unexpected owned handler count: $($Owned.Count)" }
if ($Owned[0].command -isnot [string] -or $Owned[0].commandWindows -cne ('& ' + $Owned[0].command)) {
  throw 'Windows override is not the PowerShell call-operator form of the base command'
}
$Tokens = @([regex]::Matches($Owned[0].command, '"[^"]*"|\S+') | ForEach-Object { $_.Value.Trim('"') })
[pscustomobject]@{
  owned_handler_count = $Owned.Count
  type = $Owned[0].type
  timeout = $Owned[0].timeout
  status_message = $Owned[0].statusMessage
  executable_leaf = [IO.Path]::GetFileName($Tokens[0])
  script_leaf = [IO.Path]::GetFileName($Tokens[1])
}
```

期待値はhandler 1件、必須 `command` とそのPowerShell call-operator formである `commandWindows`、`type=command`、`timeout=45`、status message `Sending LINE turn notification`、script leaf `codex_turn_line_notify.py` です。`GcloudPath` はPythonから直接起動できる `gcloud.cmd` に限定します。notifierまたはhandler変更後はhook hashが変わるため、上記確認後に `/hooks` でそのexact hookだけを再承認し、警告を迂回しません。

## Diagnostics

通知結果は秘密情報を含まない最小ログで確認します。

```powershell
Get-Content -Encoding UTF8 (Join-Path $CodexUserDir 'logs\codex_turn_line_notify.log') -Tail 20
```

正常時のstatusは `sent`、`deduplicated`、`no_subscribers` のいずれかです。異常時は例外classだけが記録されます。診断のためにtoken、raw hook JSON、raw ID、response bodyを表示しません。通知障害があってもCodexのターン停止は成功します。

## Removeとrollback

ローカルrollbackは追加した `Stop` handlerだけを除外します。

```powershell
& $Installer -Remove `
  -CodexUserDir $CodexUserDir `
  -PythonPath $PythonPath `
  -GcloudPath $GcloudPath
```

`Remove` はscript filenameとendpointの両方が一致するowned handlerだけを削除し、他event、他handler、`config.toml`、既存 `notify` を保持します。変更時は `hooks.json` のbackupを作成します。installed notifierと最小ログは監査・診断用に残りますが、handlerがないため実行されません。server endpoint、専用service account、IAMを戻す操作はこのlocal installerの範囲外であり、別の明示承認なしに変更しません。

再有効化するときは、改めて `DryRun`、明示承認、`Apply`、hashとhandlerのtrust review、必要なCodex Desktop再起動、1ターンだけのlive確認を行います。
