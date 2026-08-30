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

$semanticGaps = [System.Collections.Generic.List[string]]::new()

$forbiddenClaims = @(
    @{ Path = 'PROJECT-STANDARD.md'; Pattern = 'Lifecycle mode:\s*Greenfield'; Message = 'Implemented repositories cannot remain in Greenfield mode.' },
    @{ Path = 'AGENTS.md'; Pattern = 'Lifecycle mode:\s*Greenfield'; Message = 'AGENTS.md lifecycle mode disagrees with the implemented repository.' },
    @{ Path = 'ISSUES.md'; Pattern = 'contains no executable code'; Message = 'ISSUES.md still claims that no executable code exists.' },
    @{ Path = 'ASSESSMENT.md'; Pattern = 'CI.*never (run|executed)'; Message = 'ASSESSMENT.md still claims that CI has never run.' }
)

foreach ($claim in $forbiddenClaims) {
    if ((Test-Path $claim.Path) -and (Select-String -Path $claim.Path -Pattern $claim.Pattern -Quiet)) {
        $semanticGaps.Add($claim.Message)
    }
}

$trackedFiles = git -c core.quotepath=false ls-files
if ($trackedFiles | Where-Object { $_ -match 'MacBook Air' -and (Test-Path -LiteralPath $_) }) {
    $semanticGaps.Add('Tracked machine-name conflict copies must be removed.')
}

$nonUiPython = Get-ChildItem 'src/bookmark_exporter' -Recurse -Filter '*.py' |
    Where-Object {
        $_.FullName -notmatch '[\\/]ui[\\/]' -and $_.Name -ne 'app.py'
    }
$qtImports = $nonUiPython | Select-String -Pattern '^\s*(from|import)\s+PySide6'
if ($qtImports) {
    $semanticGaps.Add('PySide6 is imported below the UI layer.')
}

$authorityConflict = Get-ChildItem -File -Filter '*.md' |
    Select-String -Pattern 'Source of truth for scope/architecture:\s*`prompts/COPILOT-BUILD-PROMPT.md`'
if ($authorityConflict) {
    $semanticGaps.Add('A living document incorrectly treats the build prompt as authoritative scope.')
}

if ($Markdown) {
    '| Responsibility | Authority | Last updated | Status |'
    '|---|---|---|---|'
    $rows | ForEach-Object { "| $($_.Responsibility) | $($_.Authority) | $($_.LastUpdated) | $($_.Status) |" }
    if ($semanticGaps) {
        ''
        'Semantic gaps:'
        $semanticGaps | ForEach-Object { "- $_" }
    }
} else {
    $rows | Format-Table -AutoSize
    $semanticGaps | ForEach-Object { Write-Warning $_ }
}

$gaps = $rows | Where-Object { $_.Status -eq 'MISSING' -or $_.Status -like 'REVIEW*' }
if (($gaps -or $semanticGaps) -and $FailOnGap) { exit 1 }
