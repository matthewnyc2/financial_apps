@echo off
REM Windows Launcher for Opening Hour Stock Predictor

REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Clear screen for clean display
cls

REM Set console to UTF-8 for better character display
chcp 65001 >nul 2>&1

REM Run the Windows-optimized application
python main_windows.py

REM Deactivate when done
deactivate

REM Pause to see any error messages
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
