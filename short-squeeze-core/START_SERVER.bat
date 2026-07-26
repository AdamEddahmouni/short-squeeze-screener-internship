@echo off
cd /d "%~dp0"
title Short Squeeze Research Screener
echo ========================================
echo  Short Squeeze Research Screener
echo  Starting on http://127.0.0.1:8787
echo  DO NOT CLOSE THIS WINDOW
echo  Press Ctrl+C to stop
echo ========================================
echo.
.venv\Scripts\python.exe -m apps.research_screener
pause
