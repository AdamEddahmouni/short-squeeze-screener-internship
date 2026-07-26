# Short Squeeze Research Screener - Continuous Server Launcher
# Run this script to start the server in a dedicated window that stays alive

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Short Squeeze Research Screener" -ForegroundColor Yellow
Write-Host " Starting server on http://127.0.0.1:8787" -ForegroundColor Green
Write-Host " DO NOT CLOSE THIS WINDOW" -ForegroundColor Red
Write-Host " Press Ctrl+C to stop" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

& .\.venv\Scripts\python.exe -m apps.research_screener --no-browser

Write-Host ""
Write-Host "Server stopped." -ForegroundColor Yellow
pause
