[CmdletBinding(DefaultParameterSetName = 'DryRun')]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'DryRun')]
    [switch]$DryRun,

    [Parameter(Mandatory = $true, ParameterSetName = 'Apply')]
    [switch]$Apply,

    [Parameter(Mandatory = $true, ParameterSetName = 'Remove')]
    [switch]$Remove,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$CodexUserDir,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$PythonPath,

    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$GcloudPath,

    [string]$Endpoint = 'https://kakeibo-api-570965759130.asia-northeast1.run.app/internal/codex/turn-ended/notify',
    [string]$Audience = 'https://kakeibo-api-570965759130.asia-northeast1.run.app',
    [string]$ServiceAccount = 'codex-turn-notifier@kakeibo-liff-prod.iam.gserviceaccount.com',
    [string]$HostLabel = 'NUCBOX_K8_PLUS'
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$NotifierFileName = 'codex_turn_line_notify.py'
$SourceNotifier = Join-Path $PSScriptRoot $NotifierFileName
$FullCodexUserDir = [IO.Path]::GetFullPath($CodexUserDir)
$FileSystemRoot = [IO.Path]::GetPathRoot($FullCodexUserDir)

if ($FullCodexUserDir.TrimEnd([char[]]@('\', '/')) -eq $FileSystemRoot.TrimEnd([char[]]@('\', '/'))) {
    throw 'CodexUserDir must not be a filesystem root.'
}
if (-not [IO.Path]::IsPathRooted($PythonPath) -or -not (Test-Path -LiteralPath $PythonPath -PathType Leaf)) {
    throw 'PythonPath must be an existing absolute file path.'
}
if (-not [IO.Path]::IsPathRooted($GcloudPath) -or -not (Test-Path -LiteralPath $GcloudPath -PathType Leaf)) {
    throw 'GcloudPath must be an existing absolute file path.'
}
if ([IO.Path]::GetFileName($GcloudPath) -ine 'gcloud.cmd') {
    throw 'GcloudPath must resolve to gcloud.cmd for direct Python subprocess execution.'
}
if (-not (Test-Path -LiteralPath $SourceNotifier -PathType Leaf)) {
    throw 'The notifier source file is missing beside the installer.'
}

$HooksPath = Join-Path $FullCodexUserDir 'hooks.json'
$InstalledHooksDir = Join-Path $FullCodexUserDir 'hooks'
$InstalledNotifier = Join-Path $InstalledHooksDir $NotifierFileName
$LogDir = Join-Path $FullCodexUserDir 'logs'
$LogPath = Join-Path $LogDir 'codex_turn_line_notify.log'

function Get-CommandTokens {
    param([string]$CommandLine)
    $Tokens = @()
    foreach ($Match in [regex]::Matches($CommandLine, '"[^"]*"|\S+')) {
        $Tokens += $Match.Value.Trim('"')
    }
    return @($Tokens)
}

function Test-OwnedHandler {
    param($Handler)
    if ($null -eq $Handler) { return $false }
    $CommandProperty = $Handler.PSObject.Properties['commandWindows']
    if ($null -eq $CommandProperty -or $CommandProperty.Value -isnot [string]) { return $false }
    $Tokens = @(Get-CommandTokens $CommandProperty.Value)
    $HasScript = $false
    $HasEndpoint = $false
    foreach ($Token in $Tokens) {
        if ([IO.Path]::GetFileName($Token) -ceq $NotifierFileName) { $HasScript = $true }
        if ($Token -ceq $Endpoint) { $HasEndpoint = $true }
    }
    return ($HasScript -and $HasEndpoint)
}

function Read-HooksDocument {
    if (-not (Test-Path -LiteralPath $HooksPath -PathType Leaf)) {
        return [pscustomobject][ordered]@{ hooks = [pscustomobject][ordered]@{} }
    }
    $Raw = [IO.File]::ReadAllText($HooksPath, [Text.Encoding]::UTF8)
    if ([string]::IsNullOrWhiteSpace($Raw)) {
        throw 'Existing hooks.json is empty.'
    }
    $Document = $Raw | ConvertFrom-Json
    if ($null -eq $Document -or $Document -isnot [pscustomobject]) {
        throw 'Existing hooks.json must contain a JSON object.'
    }
    if ($null -eq $Document.PSObject.Properties['hooks']) {
        $Document | Add-Member -NotePropertyName hooks -NotePropertyValue ([pscustomobject][ordered]@{})
    }
    elseif ($null -eq $Document.hooks -or $Document.hooks -isnot [pscustomobject]) {
        throw 'Existing hooks.json hooks property must be a JSON object.'
    }
    return $Document
}

function Remove-OwnedHandlers {
    param($Document)
    $StopProperty = $Document.hooks.PSObject.Properties['Stop']
    if ($null -eq $StopProperty) { return $false }

    $Changed = $false
    $PreservedGroups = @()
    foreach ($Group in @($StopProperty.Value)) {
        if ($null -eq $Group -or $Group -isnot [pscustomobject]) {
            $PreservedGroups += $Group
            continue
        }
        $GroupHooksProperty = $Group.PSObject.Properties['hooks']
        if ($null -eq $GroupHooksProperty) {
            $PreservedGroups += $Group
            continue
        }
        $PreservedHandlers = @()
        foreach ($Handler in @($GroupHooksProperty.Value)) {
            if (Test-OwnedHandler $Handler) {
                $Changed = $true
            }
            else {
                $PreservedHandlers += $Handler
            }
        }
        if ($PreservedHandlers.Count -gt 0) {
            $GroupHooksProperty.Value = @($PreservedHandlers)
            $PreservedGroups += $Group
        }
        elseif (@($GroupHooksProperty.Value).Count -eq 0) {
            $PreservedGroups += $Group
        }
    }

    if ($PreservedGroups.Count -gt 0) {
        $StopProperty.Value = @($PreservedGroups)
    }
    else {
        $Document.hooks.PSObject.Properties.Remove('Stop')
    }
    return $Changed
}

function New-OwnedHandlerGroup {
    $CommandWindows = ('"{0}" "{1}" --endpoint "{2}" --audience "{3}" --service-account "{4}" --host-label "{5}" --gcloud "{6}" --log-path "{7}"' -f
        [IO.Path]::GetFullPath($PythonPath),
        $InstalledNotifier,
        $Endpoint,
        $Audience,
        $ServiceAccount,
        $HostLabel,
        [IO.Path]::GetFullPath($GcloudPath),
        $LogPath)
    $Handler = [pscustomobject][ordered]@{
        type = 'command'
        timeout = 10
        statusMessage = 'Sending LINE turn notification'
        command = $CommandWindows
        commandWindows = $CommandWindows
    }
    return [pscustomobject][ordered]@{ hooks = @($Handler) }
}

function Add-OwnedHandler {
    param($Document)
    $OwnedGroup = New-OwnedHandlerGroup
    $StopProperty = $Document.hooks.PSObject.Properties['Stop']
    if ($null -eq $StopProperty) {
        $Document.hooks | Add-Member -NotePropertyName Stop -NotePropertyValue @($OwnedGroup)
    }
    else {
        $StopProperty.Value = @($StopProperty.Value) + @($OwnedGroup)
    }
}

function Get-FileHashHex {
    param([string]$Path)
    $Sha256 = [Security.Cryptography.SHA256]::Create()
    try {
        $Stream = [IO.File]::OpenRead($Path)
        try { return ([BitConverter]::ToString($Sha256.ComputeHash($Stream))).Replace('-', '') }
        finally { $Stream.Dispose() }
    }
    finally { $Sha256.Dispose() }
}

function Install-NotifierAtomically {
    [IO.Directory]::CreateDirectory($InstalledHooksDir) | Out-Null
    [IO.Directory]::CreateDirectory($LogDir) | Out-Null
    if ((Test-Path -LiteralPath $InstalledNotifier -PathType Leaf) -and
        (Get-FileHashHex $SourceNotifier) -ceq (Get-FileHashHex $InstalledNotifier)) {
        return
    }
    $TemporaryPath = Join-Path $InstalledHooksDir ('.' + $NotifierFileName + '.tmp.' + [guid]::NewGuid().ToString('N'))
    try {
        [IO.File]::Copy($SourceNotifier, $TemporaryPath, $false)
        if (Test-Path -LiteralPath $InstalledNotifier -PathType Leaf) {
            [IO.File]::Replace($TemporaryPath, $InstalledNotifier, $null)
        }
        else {
            [IO.File]::Move($TemporaryPath, $InstalledNotifier)
        }
    }
    finally {
        if (Test-Path -LiteralPath $TemporaryPath) { Remove-Item -LiteralPath $TemporaryPath -Force }
    }
}

function Write-HooksAtomically {
    param([string]$Content)
    [IO.Directory]::CreateDirectory($FullCodexUserDir) | Out-Null
    $TemporaryPath = Join-Path $FullCodexUserDir ('.hooks.json.tmp.' + [guid]::NewGuid().ToString('N'))
    try {
        [IO.File]::WriteAllText($TemporaryPath, $Content, [Text.UTF8Encoding]::new($false))
        if (Test-Path -LiteralPath $HooksPath -PathType Leaf) {
            $BackupPath = $HooksPath + '.bak.' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ') + '.' + [guid]::NewGuid().ToString('N')
            [IO.File]::Replace($TemporaryPath, $HooksPath, $BackupPath)
        }
        else {
            [IO.File]::Move($TemporaryPath, $HooksPath)
        }
    }
    finally {
        if (Test-Path -LiteralPath $TemporaryPath) { Remove-Item -LiteralPath $TemporaryPath -Force }
    }
}

$Document = Read-HooksDocument
$OwnedHandlerRemoved = Remove-OwnedHandlers $Document
if ($Apply -or $DryRun) { Add-OwnedHandler $Document }

$DesiredJson = ($Document | ConvertTo-Json -Depth 100) + [Environment]::NewLine
$CurrentJson = if (Test-Path -LiteralPath $HooksPath -PathType Leaf) {
    [IO.File]::ReadAllText($HooksPath, [Text.Encoding]::UTF8)
} else { $null }
$HooksChangeRequired = if ($Remove) { $OwnedHandlerRemoved } else { $DesiredJson -cne $CurrentJson }
$NotifierInstallRequired = (-not (Test-Path -LiteralPath $InstalledNotifier -PathType Leaf)) -or
    ((Get-FileHashHex $SourceNotifier) -cne (Get-FileHashHex $InstalledNotifier))

if ($DryRun) {
    Write-Output ("DryRun: hooks change required={0}; notifier install required={1}" -f
        $HooksChangeRequired,
        $NotifierInstallRequired)
    return
}

if ($Apply) {
    Install-NotifierAtomically
}
if ($HooksChangeRequired) {
    Write-HooksAtomically $DesiredJson
}

Write-Output ("{0}: hooks change applied={1}" -f $PSCmdlet.ParameterSetName, $HooksChangeRequired)
