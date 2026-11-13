#requires -Version 5.1

[CmdletBinding()]
param(
    [string]$ExpectedGitHubUser = "sjinnouchi-ux",
    [string]$Repository = "sjinnouchi-ux/workspace",
    [switch]$RequireWrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Complete-Check {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet("CONNECTED", "DISCONNECTED", "INCONCLUSIVE")]
        [string]$State,
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [Parameter(Mandatory = $true)]
        [int]$ExitCode
    )

    Write-Output "[$State] $Message"
    exit $ExitCode
}

$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

if ($identity -match "(?i)\\codexsandbox") {
    Complete-Check -State "INCONCLUSIVE" -Message "identity=$identity is a Codex sandbox user. Re-run this read-only check in the real Windows user context; do not log out or delete credentials." -ExitCode 2
}

$gh = Get-Command gh -ErrorAction SilentlyContinue
if (-not $gh) {
    Complete-Check -State "INCONCLUSIVE" -Message "identity=$identity; GitHub CLI is not available on PATH." -ExitCode 2
}

& $gh.Source auth status --hostname github.com --active *> $null
if ($LASTEXITCODE -ne 0) {
    Complete-Check -State "DISCONNECTED" -Message "identity=$identity; gh authentication failed in the host-user context." -ExitCode 1
}

$loginOutput = & $gh.Source api user --jq ".login" 2>$null
$loginExit = $LASTEXITCODE
$login = [string]($loginOutput | Select-Object -First 1)
$login = $login.Trim()

if ($loginExit -ne 0 -or [string]::IsNullOrWhiteSpace($login)) {
    Complete-Check -State "INCONCLUSIVE" -Message "identity=$identity; gh auth succeeded but the read-only user probe failed." -ExitCode 2
}

if ($login -ne $ExpectedGitHubUser) {
    Complete-Check -State "DISCONNECTED" -Message "identity=$identity; active_account=$login; expected_account=$ExpectedGitHubUser." -ExitCode 1
}

$permissionOutput = & $gh.Source repo view $Repository --json viewerPermission --jq ".viewerPermission" 2>$null
$permissionExit = $LASTEXITCODE
$permission = [string]($permissionOutput | Select-Object -First 1)
$permission = $permission.Trim().ToUpperInvariant()

if ($permissionExit -ne 0 -or [string]::IsNullOrWhiteSpace($permission)) {
    Complete-Check -State "INCONCLUSIVE" -Message "identity=$identity; account=$login; repository=$Repository permission probe failed." -ExitCode 2
}

if ($RequireWrite -and $permission -notin @("ADMIN", "MAINTAIN", "WRITE")) {
    Complete-Check -State "DISCONNECTED" -Message "identity=$identity; account=$login; repository=$Repository; permission=$permission; write access required." -ExitCode 1
}

Complete-Check -State "CONNECTED" -Message "identity=$identity; account=$login; repository=$Repository; permission=$permission; token_not_displayed=true." -ExitCode 0
