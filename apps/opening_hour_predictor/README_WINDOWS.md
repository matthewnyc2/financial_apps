# Opening Hour Stock Predictor - Windows Installation Guide

## Quick Start for Windows Users

### Method 1: One-Click Installer (Recommended)

1. **Download or navigate to the folder**:
   ```
   cd C:\Users\YourName\financial_apps\apps\opening_hour_predictor
   ```

2. **Double-click `quickstart.bat`**
   - This will automatically set up everything and run the application
   - First run will install all dependencies (may take 5-10 minutes)
   - Subsequent runs will start immediately

### Method 2: Manual Installation

#### Prerequisites

1. **Install Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/
   - **IMPORTANT**: During installation, check "Add Python to PATH"
   - Verify installation:
     ```cmd
     python --version
     ```

2. **Install Git (Optional)**
   - Download from: https://git-scm.com/download/win
   - Only needed if cloning from GitHub

#### Installation Steps

1. **Open Command Prompt**:
   - Press `Win + R`
   - Type `cmd` and press Enter

2. **Navigate to the application folder**:
   ```cmd
   cd C:\path\to\financial_apps\apps\opening_hour_predictor
   ```

3. **Run the setup script**:
   ```cmd
   setup.bat
   ```

   This will:
   - Create a virtual environment
   - Install all Python packages
   - Create necessary directories
   - Set up configuration files

4. **Run the application**:
   ```cmd
   run.bat
   ```

## What Each File Does

| File | Description |
|------|-------------|
| `quickstart.bat` | One-click installer and launcher |
| `setup.bat` | Installation script (first-time setup) |
| `run.bat` | Application launcher (after setup) |
| `main_windows.py` | Windows-optimized Python application |
| `requirements.txt` | List of Python packages needed |
| `config/config.yaml` | Configuration settings |
| `.env` | API keys (created by setup.bat) |

## Windows-Specific Features

### Colored Terminal Output
The Windows version includes colored output for better readability:
- **Green** = Gainers, Success messages
- **Red** = Losers, Errors
- **Yellow** = Warnings, Input prompts
- **Cyan** = Headers, Information
- **White** = Data, Results

### UTF-8 Support
The application automatically sets your console to UTF-8 for proper character display.

### Console Title
The Windows title bar shows "Opening Hour Stock Predictor" when running.

### Clean Screen Clearing
Uses Windows `cls` command for clean screen transitions.

## Troubleshooting

### Error: "Python is not recognized..."

**Problem**: Python is not in your system PATH.

**Solution**:
1. Reinstall Python and check "Add Python to PATH"
2. Or manually add Python to PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click Edit
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python310`
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python310\Scripts`

### Error: "pip install failed"

**Problem**: Some packages failed to install.

**Solution 1** - Update pip:
```cmd
python -m pip install --upgrade pip
```

**Solution 2** - Install Visual C++ Build Tools:
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- Required for packages like TA-Lib

**Solution 3** - Install TA-Lib manually:
1. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Choose file matching your Python version (e.g., `TA_Lib-0.4.24-cp310-cp310-win_amd64.whl` for Python 3.10 64-bit)
3. Install with: `pip install path\to\downloaded\file.whl`

### Error: "Module not found"

**Problem**: Dependencies not installed in virtual environment.

**Solution**:
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Error: "Permission denied"

**Problem**: Antivirus or Windows security blocking execution.

**Solution**:
1. Run Command Prompt as Administrator
2. Or add exception in Windows Defender for this folder

### Application runs but shows errors downloading data

**Problem**: Network/firewall blocking API access.

**Solution**:
1. Check your internet connection
2. Disable VPN temporarily
3. Check Windows Firewall settings
4. Try using only yfinance (no API key needed)

### Redis not available warning

**Problem**: Redis is not installed (optional).

**Solution**: This is just a warning. The app works without Redis, but caching improves performance.

To install Redis on Windows (optional):
1. Download from: https://github.com/microsoftarchive/redis/releases
2. Or use WSL (Windows Subsystem for Linux)
3. Or ignore - app works fine without it

## Optional: Install Redis for Better Performance

Redis provides caching which speeds up repeated queries.

### Option 1: Windows Native Redis
1. Download from: https://github.com/tporadowski/redis/releases
2. Extract to `C:\Redis`
3. Run `redis-server.exe`

### Option 2: Windows Subsystem for Linux (WSL)
```bash
wsl
sudo apt-get install redis-server
redis-server
```

### Option 3: Skip Redis
The application works fine without Redis. You'll just see a warning message.

## Getting API Keys (Optional)

The application works with **yfinance by default** (no API keys needed). For more data sources:

### Finnhub (Free: 60 requests/minute)
1. Go to: https://finnhub.io/register
2. Sign up for free account
3. Copy your API key
4. Add to `.env` file:
   ```
   FINNHUB_API_KEY=your_key_here
   ```

### Alpha Vantage (Free: 500 requests/day)
1. Go to: https://www.alphavantage.co/support/#api-key
2. Get free API key
3. Add to `.env` file:
   ```
   ALPHA_VANTAGE_KEY=your_key_here
   ```

### Alpaca (Free paper trading)
1. Go to: https://alpaca.markets/
2. Sign up for free
3. Get API keys from dashboard
4. Add to `.env` file:
   ```
   ALPACA_API_KEY=your_key_here
   ALPACA_SECRET_KEY=your_secret_here
   ```

## Usage Examples

### Example 1: Quick Test (10 stocks)
```cmd
run.bat
```
- Select option `5` from menu
- Analyzes 10 stocks in ~30 seconds
- Good for testing

### Example 2: Full Analysis (S&P 500)
```cmd
run.bat
```
- Select option `4` from menu
- Analyzes 500 stocks in ~3-5 minutes
- Generates full predictions

### Example 3: Analyze Single Stock
```cmd
run.bat
```
- Select option `3` from menu
- Enter symbol (e.g., `AAPL`)
- See all technical indicators

## Windows Command Line Tips

### Copy Text from Command Prompt
- Right-click → Mark
- Select text
- Press Enter to copy

### Paste into Command Prompt
- Right-click → Paste

### Increase Command Prompt Window Size
- Right-click title bar → Properties → Layout
- Increase Screen Buffer Size and Window Size

### Use Windows Terminal (Better Experience)
1. Install from Microsoft Store: "Windows Terminal"
2. Run `run.bat` from Windows Terminal for better colors

## Performance Tips

### Make it Faster
1. **Use SSD**: Store application on SSD drive
2. **More Cores**: Set in `config/config.yaml`:
   ```yaml
   analysis:
     max_compute_workers: 8  # Match your CPU cores
   ```
3. **Install Redis**: Speeds up repeated queries
4. **Limit Stock Universe**: Start with fewer stocks for testing

### Typical Performance (Windows 10/11)
- **10 stocks**: 20-30 seconds
- **50 stocks**: 1-2 minutes
- **500 stocks (S&P 500)**: 3-5 minutes

Performance varies based on:
- Internet speed (data download)
- CPU cores (analysis)
- RAM available
- API rate limits

## Updating the Application

### Update Python Packages
```cmd
venv\Scripts\activate
pip install --upgrade -r requirements.txt
```

### Update Application Code
If you got this from Git:
```cmd
git pull origin main
```

## Uninstalling

1. Delete the virtual environment:
   ```cmd
   rmdir /s /q venv
   ```

2. Delete downloaded data (optional):
   ```cmd
   rmdir /s /q data
   ```

3. Delete the entire folder if desired

## System Requirements

### Minimum
- **OS**: Windows 10 or later
- **Python**: 3.10+
- **RAM**: 4GB
- **Disk**: 2GB free space
- **Internet**: Required for data download

### Recommended
- **OS**: Windows 11
- **Python**: 3.11+
- **RAM**: 8GB+
- **Disk**: 5GB free space (SSD)
- **CPU**: 4+ cores
- **Internet**: Broadband (10+ Mbps)

## Support

### Common Issues
See [Troubleshooting](#troubleshooting) section above.

### Additional Help
1. Check main README.md for detailed documentation
2. See ARCHITECTURE.md for system design
3. Review config/config.yaml for all settings

## Next Steps After Installation

1. **Run Quick Test**: Option 5 (10 stocks, ~30 seconds)
2. **Verify Results**: Check CSV files in folder
3. **Try Single Stock**: Option 3, analyze AAPL or MSFT
4. **Run Full Analysis**: Option 4 when ready
5. **Review Settings**: Option 7 to see configuration
6. **Optimize**: Adjust config/config.yaml for your needs

## Keyboard Shortcuts

- **Ctrl+C**: Stop running operation
- **Ctrl+Z then Enter**: Force quit (if frozen)
- **Up Arrow**: Recall previous command
- **Tab**: Auto-complete file names

## Windows-Specific Notes

### Antivirus
Some antivirus software may flag Python scripts. This is a false positive. Add exception if needed.

### Long Path Names
Windows has a 260-character path limit. Install in a short path like:
```
C:\Trading\opening_hour_predictor
```

### File Associations
If `.py` files open in editor instead of running:
```cmd
assoc .py=Python.File
ftype Python.File="C:\Python310\python.exe" "%1" %*
```

### Running at Startup (Optional)
1. Press `Win + R`
2. Type `shell:startup`
3. Create shortcut to `run.bat` in this folder

---

**Enjoy using Opening Hour Stock Predictor on Windows!**
