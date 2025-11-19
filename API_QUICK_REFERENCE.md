# Financial Data APIs - Quick Reference Card

Print this page or bookmark for quick lookup while coding.

## 30-Second Decision Guide

| Need | API | Rate Limit | Setup |
|------|-----|-----------|-------|
| Daily quotes | Finnhub | 60/min | 1 API key |
| Minute bars | Alpaca | 200/min | No key |
| 30-year history | Tiingo | 50/hr | 1 API key |
| Backtesting | Alpaca | 200/min | No key |
| Quick test | yfinance | ~2k/hr | No key |

**Best combo**: Finnhub + Alpaca (covers all needs, completely free)

---

## Installation One-Liner

```bash
pip install finnhub-python alpaca-py tiingo pandas numpy && echo "Done!"
```

---

## API Endpoints Cheat Sheet

### Finnhub
```
GET /stock/candles?symbol=AAPL&resolution=D&from=1234567890&to=1234567890
GET /quote?symbol=AAPL
GET /company-basic-financials?symbol=AAPL&metric=all
```

### Alpaca
```
GET /v2/stocks/bars
GET /v2/stocks/{symbol}/quotes/latest
GET /v2/stocks/{symbol}/bars
```

### Tiingo
```
GET /daily/{ticker}
GET /daily/{ticker}/prices
```

---

## Code Snippets (Copy-Paste Ready)

### Get Daily Data - Finnhub
```python
import finnhub
client = finnhub.Client(api_key="YOUR_KEY")
end_time = int(time.time())
start_time = int(time.time()) - (365 * 86400)
data = client.stock_candles('AAPL', 'D', start_time, end_time)
```

### Get Daily Data - Alpaca
```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

client = StockHistoricalDataClient()
request = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Day,
    start=datetime(2023, 1, 1),
    end=datetime(2023, 12, 31)
)
bars = client.get_stock_bars(request)
df = bars.df
```

### Get Minute Data - Alpaca
```python
# Same as above but change timeframe:
timeframe=TimeFrame.Minute  # or TimeFrame(5, TimeFrameUnit.Minute) for 5-min
```

### Get Historical Data - Tiingo
```python
import tiingo
tiingo.conf['api_key'] = 'YOUR_KEY'
df = tiingo.get_dataframe('AAPL', startDate='2020-01-01', endDate='2023-12-31')
```

### Get Real-Time Quote - Finnhub
```python
quote = client.quote('AAPL')
print(f"Price: {quote['c']}, Change: {quote['d']}")
```

### Get Real-Time Quote - FMP
```python
import requests
url = f"https://financialmodelingprep.com/api/v3/quote/AAPL?apikey={API_KEY}"
data = requests.get(url).json()
print(f"Price: {data[0]['price']}")
```

---

## Rate Limit Calculator

**Finnhub**: 60 calls/min
- For N stocks: `sleep(60/N)` seconds between calls
- 10 stocks: sleep 6 seconds
- 100 stocks: sleep 0.6 seconds
- 1000 stocks: batch in 16 groups

**Alpaca**: 200 calls/min
- For N stocks: `sleep(60/200) * N` = `sleep(0.3 * N)`
- 10 stocks: sleep 3 seconds
- 100 stocks: sleep 30 seconds (batch recommended)

**FMP**: 250 calls/day
- Process ~10 stocks/hour maximum
- Batch jobs only, not real-time

---

## Environment Setup Template

```bash
# Create project
mkdir my_stock_app
cd my_stock_app

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'REQS'
finnhub-python==1.5.10
alpaca-py==0.9.0
tiingo==0.21.0
pandas==2.0.0
numpy==1.24.0
python-dotenv==1.0.0
requests==2.31.0
REQS

# Install
pip install -r requirements.txt

# Create .env file (ADD YOUR KEYS HERE)
cat > .env << 'ENV'
FINNHUB_API_KEY=your_key_here
TIINGO_API_KEY=your_key_here
ENV

# Create basic script
cat > main.py << 'PY'
from dotenv import load_dotenv
import os
import finnhub

load_dotenv()
client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
quote = client.quote('AAPL')
print(f"AAPL: ${quote['c']}")
PY

# Run
python main.py
```

---

## Error Handling Patterns

### Rate Limit Error
```python
import time
try:
    data = client.stock_candles('AAPL', 'D', start, end)
except Exception as e:
    if '429' in str(e) or 'rate' in str(e).lower():
        print("Rate limited, waiting...")
        time.sleep(60)
        data = client.stock_candles('AAPL', 'D', start, end)
```

### Retry with Backoff
```python
def retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt  # 1, 2, 4 seconds
            print(f"Attempt {attempt+1} failed. Retry in {wait}s...")
            time.sleep(wait)

data = retry(lambda: client.quote('AAPL'))
```

---

## Data Validation One-Liner

```python
assert (df['high'] >= df['low']).all() and (df['volume'] > 0).all() and not df.isnull().any().any()
```

---

## API Key URLs (Bookmark These)

| API | Get Key | Documentation | Status |
|-----|---------|---------------|--------|
| Finnhub | https://finnhub.io | https://finnhub.io/docs | ✅ Active |
| Alpaca | https://alpaca.markets | https://alpaca.markets/docs | ✅ Active |
| Tiingo | https://www.tiingo.com | https://www.tiingo.com/docs | ✅ Active |
| FMP | https://site.financialmodelingprep.com | https://site.financialmodelingprep.com/developer/docs | ✅ Active |
| yfinance | None | https://github.com/ranaroussi/yfinance | ⚠️ Fragile |

---

## Common Gotchas

### Finnhub 1-Year Limit
```python
# Get multiple years by looping
for year in range(2020, 2024):
    start = int(datetime(year, 1, 1).timestamp())
    end = int(datetime(year, 12, 31).timestamp())
    data = client.stock_candles('AAPL', 'D', start, end)
    # Process...
    time.sleep(1)
```

### Alpaca No Index Symbols
```python
# This works:
bars = client.get_stock_bars(StockBarsRequest(...))
df = bars.df.reset_index()

# Not this (for some versions):
df = bars.df  # May have MultiIndex
```

### yfinance Blocking
```python
# Don't use in production!
# If you must, add headers:
import yfinance as yf
yf.download('AAPL', headers={'User-Agent': 'Mozilla/5.0'})
```

### FMP 250/Day Limit
```python
# Track usage
call_count = 0
for symbol in symbols:
    if call_count >= 250:
        print("Daily limit reached, stopping")
        break
    data = get_fmp_data(symbol)
    call_count += 1
```

---

## Performance Tips

1. **Batch requests when possible**
   ```python
   # Good: 1 call for 10 stocks
   bars = client.get_stock_bars(
       StockBarsRequest(symbol_or_symbols=['AAPL', 'MSFT', ...], ...)
   )
   
   # Bad: 10 calls for 10 stocks
   for symbol in stocks:
       bars = client.get_stock_bars(...)
   ```

2. **Cache results locally**
   ```python
   import pickle
   if os.path.exists('cache.pkl'):
       with open('cache.pkl', 'rb') as f:
           data = pickle.load(f)
   else:
       data = fetch_data()
       with open('cache.pkl', 'wb') as f:
           pickle.dump(data, f)
   ```

3. **Use pandas efficiently**
   ```python
   # Don't:
   for i in range(len(df)):
       df.loc[i, 'ma'] = df.loc[:i, 'close'].mean()
   
   # Do:
   df['ma'] = df['close'].rolling(window=20).mean()
   ```

---

## Debugging Checklist

- [ ] API key correct and not expired?
- [ ] Rate limit exceeded? (check response code)
- [ ] Date format correct? (YYYY-MM-DD or UNIX timestamp)
- [ ] Symbol valid? (check against NASDAQ/NYSE list)
- [ ] Internet connection active?
- [ ] API endpoint correct?
- [ ] Required vs optional parameters?
- [ ] Time zone issues? (most data is EST/EDT)
- [ ] Market hours? (data may not update during/before market hours)
- [ ] Test with single symbol first before batch

---

## Quick Status Check

```python
# Check if APIs are up
import requests
import finnhub

# Finnhub
try:
    client = finnhub.Client(api_key="test")
    print("Finnhub: Responding")
except Exception as e:
    print(f"Finnhub: {e}")

# Alpaca
try:
    from alpaca.data.historical import StockHistoricalDataClient
    print("Alpaca: Available")
except:
    print("Alpaca: Not available")

# Tiingo
try:
    import tiingo
    print("Tiingo: Available")
except:
    print("Tiingo: Not available")
```

---

## Useful Aliases (Add to ~/.bashrc or ~/.zshrc)

```bash
# Install financial libraries
alias pip-finance='pip install finnhub-python alpaca-py tiingo pandas numpy'

# Quick Python finance test
alias test-finance='python -c "import finnhub; print(\"Finnhub: OK\"); import alpaca; print(\"Alpaca: OK\")"'

# View documentation
alias finance-docs='echo "Finnhub: https://finnhub.io/docs; Alpaca: https://alpaca.markets/docs"'
```

---

## Recommended Learning Path

1. **Day 1**: Get API keys, run quick start examples (30 min)
2. **Day 2**: Build daily stock screener (1 hour)
3. **Day 3**: Build minute-level backtest (2 hours)
4. **Day 4**: Add error handling and rate limiting (1 hour)
5. **Day 5**: Deploy to cloud or schedule daily runs (2 hours)

---

## Free Tier Cost Summary

| API | Cost | Rate Limit | Best For |
|-----|------|-----------|----------|
| Finnhub | Free | 60/min | Daily monitoring |
| Alpaca | Free | 200/min | Backtesting |
| Tiingo | Free | 50/hr | Historical research |
| FMP | Free | 250/day | Batch jobs |
| yfinance | Free | ~2k/hr | Quick tests |
| **Total Monthly Cost** | **$0** | - | **Everything** |

---

**Quick Reminder**: Finnhub + Alpaca combo covers 95% of needs for free!

Last updated: November 19, 2025
