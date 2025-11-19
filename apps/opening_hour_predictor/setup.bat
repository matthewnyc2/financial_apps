@echo off
REM Windows Setup Script for Opening Hour Stock Predictor
REM Run this file to set up the application on Windows

echo ================================================================================
echo          Opening Hour Stock Predictor - Windows Setup
echo ================================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [1/5] Python found:
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)
echo.

REM Activate virtual environment and install dependencies
echo [3/5] Installing Python packages...
echo This may take several minutes...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo WARNING: Some packages may have failed to install
    echo The application may still work with reduced functionality
)
echo.

REM Create .env file if it doesn't exist
echo [4/5] Setting up configuration...
if not exist .env (
    echo Creating .env file for API keys...
    (
        echo # API Keys for Opening Hour Stock Predictor
        echo # Optional - yfinance works without any keys
        echo.
        echo # Finnhub - Free tier: 60 requests/minute
        echo # Get key at: https://finnhub.io/register
        echo FINNHUB_API_KEY=
        echo.
        echo # Alpha Vantage - Free tier: 500 requests/day
        echo # Get key at: https://www.alphavantage.co/support/#api-key
        echo ALPHA_VANTAGE_KEY=
        echo.
        echo # Alpaca - Free paper trading
        echo # Get keys at: https://alpaca.markets/
        echo ALPACA_API_KEY=
        echo ALPACA_SECRET_KEY=
        echo.
        echo # Database ^(Optional^)
        echo DB_USER=postgres
        echo DB_PASSWORD=
        echo.
        echo # Redis ^(Optional^)
        echo REDIS_PASSWORD=
    ) > .env
    echo .env file created. You can add API keys later.
) else (
    echo .env file already exists.
)
echo.

REM Create data directories
echo [5/5] Creating directories...
if not exist data mkdir data
if not exist data\stocks mkdir data\stocks
if not exist data\cache mkdir data\cache
if not exist logs mkdir logs
if not exist models mkdir models
if not exist models\saved mkdir models\saved
echo Directories created.
echo.

echo ================================================================================
echo                         Setup Complete!
echo ================================================================================
echo.
echo To run the application:
echo   1. Run: run.bat
echo   2. Or manually: venv\Scripts\activate.bat then python main.py
echo.
echo Optional Setup:
echo   - Add API keys to .env file for more data sources
echo   - Install Redis for caching (optional but recommended)
echo   - See README.md for full documentation
echo.
echo ================================================================================
echo.
pause
