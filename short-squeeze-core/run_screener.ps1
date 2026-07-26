# Short Squeeze Research Screener -- one-command launcher.
#
# RESEARCH TOOL -- NOT A TRADING RECOMMENDATION.
# Read-only. Binds 127.0.0.1 only. No orders, no account data, no credentials printed.
#
#   .\run_screener.ps1                 start and open a browser
#   .\run_screener.ps1 -NoBrowser      start without opening a browser
#   .\run_screener.ps1 -Check          print availability and exit
#   .\run_screener.ps1 -Port 8900      choose the preferred port

[CmdletBinding()]
param(
    [int]$Port = 8787,
    [switch]$NoBrowser,
    [switch]$Check,
    [switch]$VerboseHttp
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host "Project virtual environment not found at $python" -ForegroundColor Red
    Write-Host "Create it first, then re-run this script." -ForegroundColor Red
    exit 1
}

$providerConfig = Join-Path $root '.private\providers.env'
$appArgs = @(
    '-m', 'apps.research_screener',
    '--port', $Port,
    '--provider-config', $providerConfig
)
if ($NoBrowser)   { $appArgs += '--no-browser' }
if ($Check)       { $appArgs += '--check' }
if ($VerboseHttp) { $appArgs += '--verbose' }

# The application lives in apps/, which is importable from the repository root.
Push-Location $root
try {
    # Fail early and clearly if the packages are not importable, rather than mid-request.
    & $python -c "import apps.research_screener, squeeze_core" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "apps.research_screener is not importable from $python" -ForegroundColor Red
        Write-Host "Install the project into the virtual environment: pip install -e ." -ForegroundColor Red
        exit 1
    }

    & $python @appArgs
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
