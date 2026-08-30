#Requires -Version 7.0
[CmdletBinding()]
param(
    [string]$ConfigPath = '.docs-authority.json',
    [switch]$FailOnGap,
    [switch]$Markdown
)

if (-not (Test-Path $ConfigPath)) {
    Write-Error "Authority map not found at $ConfigPath. This repository is not compliant."
    exit 1
}

$config = Get-Content $ConfigPath -Raw | ConvertFrom-Json
$maxDrift = if ($config.maxDriftDays) { [int]$config.maxDriftDays } else { 30 }

function Get-LastCommitDate {
    param([string]$Path)
    $iso = git log -1 --format=%cI -- $Path 2>$null
    if ([string]::IsNullOrWhiteSpace($iso)) { return $null }
    return [datetime]::Parse($iso)
}

$sourceDate = $config.sourcePaths |
    ForEach-Object { Get-LastCommitDate -Path $_ } |
    Where-Object { $_ } |
    Sort-Object -Descending |
    Select-Object -First 1

$rows = foreach ($name in $config.responsibilities.PSObject.Properties.Name) {
    $entry     = $config.responsibilities.$name
    $authority = $entry.authority
    $class     = $entry.class

    if ($authority -in @('Not required at this tier', 'External tracker')) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'N/A'; LastUpdated = '' }
        continue
    }

    if (-not (Test-Path $authority)) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'MISSING'; LastUpdated = '' }
        continue
    }

    $docDate = Get-LastCommitDate -Path $authority
    $updated = if ($docDate) { $docDate.ToString('yyyy-MM-dd') } else { 'uncommitted' }

    # Contractual and governance documents are frozen by design; drift is expected.
    if ($class -ne 'living' -or -not $sourceDate -or -not $docDate) {
        [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = 'Current'; LastUpdated = $updated }
        continue
    }

    $drift  = [int]($sourceDate - $docDate).TotalDays
    $status = if ($drift -gt $maxDrift) { "REVIEW (${drift}d)" } else { 'Current' }

    [pscustomobject]@{ Responsibility = $name; Authority = $authority; Status = $status; LastUpdated = $updated }
}

if ($Markdown) {
    '| Responsibility | Authority | Last updated | Status |'
    '|---|---|---|---|'
    $rows | ForEach-Object { "| $($_.Responsibility) | $($_.Authority) | $($_.LastUpdated) | $($_.Status) |" }
} else {
    $rows | Format-Table -AutoSize
}

$gaps = $rows | Where-Object { $_.Status -eq 'MISSING' -or $_.Status -like 'REVIEW*' }
if ($gaps -and $FailOnGap) { exit 1 }
