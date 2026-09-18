@echo off
REM ============================================================
REM  HREA RAG - one-click launcher for Windows.
REM  Double-click this file. It sets everything up the first
REM  time, then just starts the app on later runs.
REM ============================================================
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo.
  echo Python is not installed or not on PATH.
  echo Install Python 3.9+ from https://www.python.org/downloads/
  echo  (tick "Add python.exe to PATH" during install^), then run this again.
  echo.
  pause
  exit /b 1
)

if not exist ".venv" (
  echo Creating virtual environment...
  python -m venv .venv
)
call ".venv\Scripts\activate.bat"

if not exist ".venv\.installed" (
  echo Installing dependencies (first run only, may take a few minutes^)...
  python -m pip install --quiet --upgrade pip
  python -m pip install --quiet -r requirements.txt
  if errorlevel 1 (
    echo Dependency installation failed. See messages above.
    pause
    exit /b 1
  )
  type nul > ".venv\.installed"
)

echo.
echo Starting HREA RAG... your browser will open at http://127.0.0.1:5000
echo Close this window (or press Ctrl+C) to stop the app.
echo.
python app.py
pause
