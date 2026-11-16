# デスクトップ直下のPDFを「PDF格納」へ移動します。
[CmdletBinding()]
param(
    [string]$DesktopPath = [Environment]::GetFolderPath('DesktopDirectory'),
    [switch]$NoPause
)

$ErrorActionPreference = 'Stop'
$exitCode = 0
try {
    if ([string]::IsNullOrWhiteSpace($DesktopPath) -or
        -not (Test-Path -LiteralPath $DesktopPath -PathType Container)) {
        throw 'デスクトップの保存先が見つかりません。'
    }
    $sourcePath = (Get-Item -LiteralPath $DesktopPath).FullName
    $destinationPath = Join-Path $sourcePath 'PDF格納'
    if (-not (Test-Path -LiteralPath $destinationPath)) {
        New-Item -ItemType Directory -Path $destinationPath | Out-Null
    }
    if (-not (Test-Path -LiteralPath $destinationPath -PathType Container)) {
        throw '「PDF格納」がフォルダではありません。'
    }

    $pdfFiles = @(Get-ChildItem -LiteralPath $sourcePath -Filter '*.pdf' -File)
    $movedCount = 0
    $failedCount = 0
    foreach ($pdfFile in $pdfFiles) {
        try {
            $targetPath = Join-Path $destinationPath $pdfFile.Name
            $suffix = 1
            while (Test-Path -LiteralPath $targetPath) {
                $targetName = '{0} ({1}){2}' -f $pdfFile.BaseName, $suffix, $pdfFile.Extension
                $targetPath = Join-Path $destinationPath $targetName
                $suffix++
            }
            # 上書きしない移動。移動先に競合が発生した場合は元ファイルを残します。
            [System.IO.File]::Move($pdfFile.FullName, $targetPath)
            $movedCount++
        }
        catch {
            $failedCount++
            Write-Host ('移動できませんでした: {0}' -f $pdfFile.Name) -ForegroundColor Yellow
        }
    }
    Write-Host ''
    Write-Host ('完了: PDF {0} 件を「PDF格納」へ移動しました。' -f $movedCount)
    if ($failedCount -gt 0) {
        Write-Host ('移動できなかった {0} 件はデスクトップに残っています。' -f $failedCount) -ForegroundColor Yellow
        $exitCode = 1
    }
    elseif ($pdfFiles.Count -eq 0) {
        Write-Host 'デスクトップ直下にPDFはありません。'
    }
}
catch {
    Write-Host ('処理を開始できませんでした: {0}' -f $_.Exception.Message) -ForegroundColor Red
    $exitCode = 1
}
if (-not $NoPause) {
    Write-Host ''
    [void](Read-Host 'Enterキーで閉じます')
}
exit $exitCode
