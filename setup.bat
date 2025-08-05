@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   Photoshop Automation - First Time Setup
echo ============================================

:: 1. Check Python availability
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.10.x manually before continuing.
    echo Download: https://www.python.org/downloads/release/python-31012/
    pause
    exit /b
)

:: 2. Check Python version
for /f "tokens=2 delims== " %%A in ('python --version') do (
    set "ver=%%A"
)
echo Detected Python version: %ver%
echo.

echo Checking for venv...
IF EXIST venv (
    echo [OK] Virtual environment already exists.
) ELSE (
    echo Creating virtual environment...
    python -m venv venv
)

:: 3. Activate venv
call venv\Scripts\activate

:: 4. Check if requirements installed
IF EXIST "venv\Lib\site-packages\mediapipe" (
    echo [OK] Dependencies already installed.
) ELSE (
    echo Installing dependencies from requirements.txt...
    pip install --upgrade pip
    pip install -r requirements.txt
)

echo.
echo ============================================
echo Launching Photoshop Automation Tool...
echo ============================================
python gui\interface.py
pause
