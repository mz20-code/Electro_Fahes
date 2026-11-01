@echo off
setlocal
title TechVerse - Electronics and Solar
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0Website"
if not exist app.py (
  echo Website folder not found. Extract the entire ZIP before starting.
  pause
  exit /b 1
)
if exist .venv\Scripts\python.exe goto install
py -3 --version >nul 2>&1
if not errorlevel 1 (
  py -3 -m venv .venv
) else (
  python --version >nul 2>&1
  if errorlevel 1 (
    echo Install Python 3 from python.org and enable Add Python to PATH.
    pause
    exit /b 1
  )
  python -m venv .venv
)
if errorlevel 1 goto failed
:install
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo TechVerse is starting at http://127.0.0.1:5000
echo Keep this window open while using the website. Press Ctrl+C to stop.
echo.
".venv\Scripts\python.exe" run.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo.
echo TechVerse could not start. Read the error above.
echo For a Python or dependency issue, rename Website\.venv and run this file again.
pause
exit /b 1
