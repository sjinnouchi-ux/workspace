$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Installer = Join-Path (Split-Path -Parent $PSScriptRoot) 'install_codex_turn_line_hook.ps1'
$Endpoint = 'https://kakeibo-api-570965759130.asia-northeast1.run.app/internal/codex/turn-ended/notify'
$Audience = 'https://kakeibo-api-570965759130.asia-northeast1.run.app'
$ServiceAccount = 'codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com'
$HostLabel = 'NUCBOX_K8_PLUS'
$script:Passed = 0
$script:Failed = 0

function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw $Message }
}

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "$Message (expected=<$Expected>, actual=<$Actual>)"
    }
}

function Invoke-Test {
    param([string]$Name, [scriptblock]$Body)
    try {
        & $Body
        $script:Passed++
        Write-Host "PASS $Name"
    }
    catch {
        $script:Failed++
        Write-Host "FAIL $Name`: $($_.Exception.Message)"
    }
}

function New-Fixture {
    $Root = Join-Path ([IO.Path]::GetTempPath()) ("codex-hook-installer-test-" + [guid]::NewGuid().ToString('N'))
    [IO.Directory]::CreateDirectory($Root) | Out-Null
    $CodexUserDir = Join-Path $Root 'isolated-codex-user'
    $BinDir = Join-Path $Root 'bin'
    [IO.Directory]::CreateDirectory($BinDir) | Out-Null
    $PythonPath = Join-Path $BinDir 'python.exe'
    $GcloudPath = Join-Path $BinDir 'gcloud.cmd'
    [IO.File]::WriteAllText($PythonPath, 'test executable placeholder')
    [IO.File]::WriteAllText($GcloudPath, 'test executable placeholder')
    return [pscustomobject]@{
        Root = $Root
        CodexUserDir = $CodexUserDir
        PythonPath = $PythonPath
        GcloudPath = $GcloudPath
    }
}

function Invoke-Installer {
    param($Fixture, [string]$Mode)
    $Arguments = @{
        CodexUserDir = $Fixture.CodexUserDir
        PythonPath = $Fixture.PythonPath
        GcloudPath = $Fixture.GcloudPath
    }
    $Arguments[$Mode] = $true
    & $Installer @Arguments | Out-Null
}

function Get-HooksDocument {
    param($Fixture)
    return Get-Content -Raw -Encoding UTF8 (Join-Path $Fixture.CodexUserDir 'hooks.json') | ConvertFrom-Json
}

function Get-AllHandlers {
    param($Document)
    $Handlers = @()
    foreach ($Group in @($Document.hooks.Stop)) {
        $Handlers += @($Group.hooks)
    }
    return @($Handlers)
}

function Test-OwnedHandler {
    param($Handler)
    return ($Handler.type -eq 'command' -and
        $Handler.commandWindows -match '(^|[\\/])codex_turn_line_notify\.py(?:"|\s)' -and
        $Handler.commandWindows.Contains($Endpoint))
}

$OriginalHomeUpper = $env:HOME
$OriginalHomeLower = $env:home
$OriginalCodexHome = $env:CODEX_HOME

Invoke-Test 'DryRun performs no writes and does not alter home variables' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'DryRun'
        Assert-True (-not (Test-Path -LiteralPath $Fixture.CodexUserDir)) 'DryRun created CodexUserDir'
        Assert-Equal $OriginalHomeUpper $env:HOME 'DryRun changed HOME'
        Assert-Equal $OriginalHomeLower $env:home 'DryRun changed home'
        Assert-Equal $OriginalCodexHome $env:CODEX_HOME 'DryRun changed CODEX_HOME'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Apply creates the exact Stop handler and installed notifier' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'Apply'
        $Document = Get-HooksDocument $Fixture
        $Handlers = @(Get-AllHandlers $Document | Where-Object { Test-OwnedHandler $_ })
        Assert-Equal 1 $Handlers.Count 'Apply did not create exactly one owned handler'
        $Handler = $Handlers[0]
        Assert-Equal 'command' $Handler.type 'Wrong handler type'
        Assert-Equal 10 $Handler.timeout 'Wrong handler timeout'
        Assert-Equal 'Sending LINE turn notification' $Handler.statusMessage 'Wrong statusMessage'
        $InstalledScript = Join-Path $Fixture.CodexUserDir 'hooks\codex_turn_line_notify.py'
        $LogPath = Join-Path $Fixture.CodexUserDir 'logs\codex_turn_line_notify.log'
        $ExpectedCommand = ('"{0}" "{1}" --endpoint "{2}" --audience "{3}" --service-account "{4}" --host-label "{5}" --gcloud "{6}" --log-path "{7}"' -f
            $Fixture.PythonPath, $InstalledScript, $Endpoint, $Audience, $ServiceAccount, $HostLabel, $Fixture.GcloudPath, $LogPath)
        Assert-Equal $ExpectedCommand $Handler.command 'Wrong required base command'
        Assert-Equal $ExpectedCommand $Handler.commandWindows 'Wrong commandWindows'
        Assert-True (Test-Path -LiteralPath $InstalledScript -PathType Leaf) 'Notifier was not installed'
        Assert-Equal 5 @($Handler.PSObject.Properties.Name).Count 'Handler property count does not match the command-hook schema'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Second Apply is byte-idempotent and leaves no temp or extra backup' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'Apply'
        $HooksPath = Join-Path $Fixture.CodexUserDir 'hooks.json'
        $FirstBytes = [IO.File]::ReadAllBytes($HooksPath)
        $FirstBackups = @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter 'hooks.json.bak.*' -File)
        Invoke-Installer $Fixture 'Apply'
        $SecondBytes = [IO.File]::ReadAllBytes($HooksPath)
        Assert-Equal ([Convert]::ToBase64String($FirstBytes)) ([Convert]::ToBase64String($SecondBytes)) 'Second Apply changed hooks.json bytes'
        $SecondBackups = @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter 'hooks.json.bak.*' -File)
        Assert-Equal $FirstBackups.Count $SecondBackups.Count 'Second Apply created an unnecessary backup'
        Assert-Equal 0 @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter '*.tmp.*' -File -Recurse).Count 'Temporary files remain'
        Assert-Equal 1 @(Get-AllHandlers (Get-HooksDocument $Fixture) | Where-Object { Test-OwnedHandler $_ }).Count 'Second Apply duplicated the handler'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'DryRun reports a stale installed notifier without changing it' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'Apply'
        $InstalledScript = Join-Path $Fixture.CodexUserDir 'hooks\codex_turn_line_notify.py'
        [IO.File]::WriteAllText($InstalledScript, 'stale notifier')
        $BeforeBytes = [IO.File]::ReadAllBytes($InstalledScript)
        $Output = & $Installer -DryRun -CodexUserDir $Fixture.CodexUserDir -PythonPath $Fixture.PythonPath -GcloudPath $Fixture.GcloudPath
        Assert-True (($Output -join "`n") -match 'notifier install required=True') 'DryRun did not report the stale notifier'
        Assert-Equal ([Convert]::ToBase64String($BeforeBytes)) ([Convert]::ToBase64String([IO.File]::ReadAllBytes($InstalledScript))) 'DryRun changed the stale notifier'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Apply preserves unrelated hooks and config.toml' {
    $Fixture = New-Fixture
    try {
        [IO.Directory]::CreateDirectory($Fixture.CodexUserDir) | Out-Null
        $ConfigPath = Join-Path $Fixture.CodexUserDir 'config.toml'
        $ConfigBytes = [Text.Encoding]::UTF8.GetBytes('notify = ["keep.exe", "turn-ended"]')
        [IO.File]::WriteAllBytes($ConfigPath, $ConfigBytes)
        $Existing = @'
{
  "description": "preserve me",
  "customTopLevel": { "enabled": true },
  "hooks": {
    "PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "commandWindows": "keep-pre.cmd" }] }],
    "Stop": [
      { "matcher": "special", "hooks": [
        { "type": "command", "commandWindows": "keep-stop.cmd" },
        { "type": "command", "commandWindows": "C:\\x\\not_codex_turn_line_notify.py --endpoint https://kakeibo-api-570965759130.asia-northeast1.run.app/internal/codex/turn-ended/notify" },
        { "type": "command", "commandWindows": "C:\\x\\codex_turn_line_notify.py --endpoint https://example.invalid/internal/codex/turn-ended/notify" }
      ] }
    ]
  }
}
'@
        [IO.File]::WriteAllText((Join-Path $Fixture.CodexUserDir 'hooks.json'), $Existing, [Text.UTF8Encoding]::new($false))
        Invoke-Installer $Fixture 'Apply'
        $Document = Get-HooksDocument $Fixture
        Assert-Equal 'preserve me' $Document.description 'Top-level description was not preserved'
        Assert-True ([bool]$Document.customTopLevel.enabled) 'Custom top-level data was not preserved'
        Assert-Equal 'keep-pre.cmd' $Document.hooks.PreToolUse[0].hooks[0].commandWindows 'Other event was changed'
        $Commands = @(Get-AllHandlers $Document | ForEach-Object { $_.commandWindows })
        Assert-True ($Commands -contains 'keep-stop.cmd') 'Unrelated Stop handler was removed'
        Assert-True (@($Commands | Where-Object { $_ -like '*not_codex_turn_line_notify.py*' }).Count -eq 1) 'Similar filename handler was removed'
        Assert-True (@($Commands | Where-Object { $_ -like '*example.invalid*' }).Count -eq 1) 'Different endpoint handler was removed'
        Assert-Equal ([Convert]::ToBase64String($ConfigBytes)) ([Convert]::ToBase64String([IO.File]::ReadAllBytes($ConfigPath))) 'config.toml was modified'
        Assert-Equal 1 @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter 'hooks.json.bak.*' -File).Count 'Apply did not create exactly one backup for an existing changed hooks.json'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Remove deletes only the owned handler and preserves config.toml' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'Apply'
        $HooksPath = Join-Path $Fixture.CodexUserDir 'hooks.json'
        $Document = Get-HooksDocument $Fixture
        $Document.hooks.Stop += [pscustomobject]@{
            matcher = 'keep'
            hooks = @([pscustomobject]@{ type = 'command'; commandWindows = 'keep-after-remove.cmd' })
        }
        [IO.File]::WriteAllText($HooksPath, ($Document | ConvertTo-Json -Depth 32), [Text.UTF8Encoding]::new($false))
        $ConfigPath = Join-Path $Fixture.CodexUserDir 'config.toml'
        $ConfigBytes = [Text.Encoding]::UTF8.GetBytes('notify = ["keep.exe", "turn-ended"]')
        [IO.File]::WriteAllBytes($ConfigPath, $ConfigBytes)
        Invoke-Installer $Fixture 'Remove'
        $After = Get-HooksDocument $Fixture
        Assert-Equal 0 @(Get-AllHandlers $After | Where-Object { Test-OwnedHandler $_ }).Count 'Owned handler remains after Remove'
        Assert-True (@(Get-AllHandlers $After | ForEach-Object { $_.commandWindows }) -contains 'keep-after-remove.cmd') 'Remove deleted an unrelated handler'
        Assert-Equal ([Convert]::ToBase64String($ConfigBytes)) ([Convert]::ToBase64String([IO.File]::ReadAllBytes($ConfigPath))) 'Remove modified config.toml'
        Assert-Equal 1 @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter 'hooks.json.bak.*' -File).Count 'Remove did not create exactly one backup'
        Assert-Equal 0 @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter '*.tmp.*' -File -Recurse).Count 'Remove left a temporary file'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Remove without an owned handler is a no-op' {
    $Fixture = New-Fixture
    try {
        Invoke-Installer $Fixture 'Remove'
        Assert-True (-not (Test-Path -LiteralPath $Fixture.CodexUserDir)) 'Remove created CodexUserDir when nothing was owned'

        [IO.Directory]::CreateDirectory($Fixture.CodexUserDir) | Out-Null
        $HooksPath = Join-Path $Fixture.CodexUserDir 'hooks.json'
        $ExistingBytes = [Text.Encoding]::UTF8.GetBytes('{"hooks":{"Stop":[{"hooks":[{"type":"command","commandWindows":"keep.cmd"}]}]}}')
        [IO.File]::WriteAllBytes($HooksPath, $ExistingBytes)
        Invoke-Installer $Fixture 'Remove'
        Assert-Equal ([Convert]::ToBase64String($ExistingBytes)) ([Convert]::ToBase64String([IO.File]::ReadAllBytes($HooksPath))) 'Remove rewrote a file without an owned handler'
        Assert-Equal 0 @(Get-ChildItem -LiteralPath $Fixture.CodexUserDir -Filter 'hooks.json.bak.*' -File).Count 'No-op Remove created a backup'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Modes are mutually exclusive' {
    $Fixture = New-Fixture
    try {
        $Rejected = $false
        try {
            & $Installer -DryRun -Apply -CodexUserDir $Fixture.CodexUserDir -PythonPath $Fixture.PythonPath -GcloudPath $Fixture.GcloudPath | Out-Null
        }
        catch { $Rejected = $true }
        Assert-True $Rejected 'Installer accepted multiple modes'
        Assert-True (-not (Test-Path -LiteralPath $Fixture.CodexUserDir)) 'Rejected mode combination performed writes'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'PowerShell gcloud wrappers are rejected' {
    $Fixture = New-Fixture
    try {
        $PowerShellWrapper = Join-Path (Split-Path -Parent $Fixture.GcloudPath) 'gcloud.ps1'
        [IO.File]::WriteAllText($PowerShellWrapper, 'Write-Output unsafe-for-direct-subprocess')
        $Rejected = $false
        try {
            & $Installer -DryRun -CodexUserDir $Fixture.CodexUserDir -PythonPath $Fixture.PythonPath -GcloudPath $PowerShellWrapper | Out-Null
        }
        catch { $Rejected = $true }
        Assert-True $Rejected 'Installer accepted gcloud.ps1 for direct Python subprocess execution'
        Assert-True (-not (Test-Path -LiteralPath $Fixture.CodexUserDir)) 'Rejected gcloud wrapper performed writes'
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Invoke-Test 'Filesystem roots are rejected in every mode' {
    $Fixture = New-Fixture
    try {
        $Root = [IO.Path]::GetPathRoot($Fixture.Root)
        foreach ($Mode in @('DryRun', 'Apply', 'Remove')) {
            $Rejected = $false
            try {
                $Arguments = @{ CodexUserDir = $Root; PythonPath = $Fixture.PythonPath; GcloudPath = $Fixture.GcloudPath }
                $Arguments[$Mode] = $true
                & $Installer @Arguments | Out-Null
            }
            catch { $Rejected = $true }
            Assert-True $Rejected "$Mode accepted a filesystem root"
        }
    }
    finally { Remove-Item -LiteralPath $Fixture.Root -Recurse -Force }
}

Assert-Equal $OriginalHomeUpper $env:HOME 'Test suite changed HOME'
Assert-Equal $OriginalHomeLower $env:home 'Test suite changed home'
Assert-Equal $OriginalCodexHome $env:CODEX_HOME 'Test suite changed CODEX_HOME'
Write-Host "RESULT passed=$script:Passed failed=$script:Failed"
if ($script:Failed -ne 0) { exit 1 }
