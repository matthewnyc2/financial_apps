@echo off
REM Quick Start for Opening Hour Stock Predictor
REM This file handles both setup and running

title Opening Hour Stock Predictor - Quick Start

echo.
echo ================================================================================
echo          Opening Hour Stock Predictor - Quick Start
echo ================================================================================
echo.

REM Check if setup is needed
if not exist venv (
    echo First-time setup detected. Running installation...
    echo.
    call setup.bat
    if errorlevel 1 (
        echo Setup failed. Please check the errors above.
        pause
        exit /b 1
    )
)

REM Check if dependencies are installed
call venv\Scripts\activate.bat
python -c "import pandas" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Running setup...
    call setup.bat
    if errorlevel 1 (
        echo Setup failed. Please check the errors above.
        pause
        exit /b 1
    )
)

REM Run the application
cls
echo.
echo ================================================================================
echo          Opening Hour Stock Predictor - Starting...
echo ================================================================================
echo.

python main_windows.py

REM Deactivate when done
deactivate

pause
