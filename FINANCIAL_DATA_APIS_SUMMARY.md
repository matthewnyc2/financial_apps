# Free Financial Data APIs - Quick Reference Summary

## Top 3 Recommended APIs (November 2025)

### 1. Finnhub (BEST OVERALL)
- **Rate Limit**: 60 calls/minute (most generous free tier)
- **Historical Depth**: 1 year per call
- **Intraday**: 1m, 5m, 15m, 30m, 60m available
- **Real-Time**: Yes (2-3 second delay)
- **Uptime**: 99.99% SLA
- **Cost**: Free forever
- **Best For**: Production systems, daily research
- **Python Library**: `finnhub-python`

**Key Code**:
```python
import finnhub
client = finnhub.Client(api_key="YOUR_KEY")
candles = client.stock_candles('AAPL', 'D', start_time, end_time)
quote = client.quote('AAPL')
```

---

### 2. Alpaca (BEST FOR MINUTE-LEVEL)
- **Rate Limit**: 200 calls/minute
- **Historical Depth**: 6+ years
- **Intraday**: 1m, 5m, 15m, 30m, 60m available
- **Real-Time**: IEX only (free tier)
- **Uptime**: Very reliable
- **Cost**: Free (no credit card needed)
- **Best For**: Algorithmic trading, minute-level backtesting
- **Python Library**: `alpaca-py`

**Key Code**:
```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

client = StockHistoricalDataClient()
request = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Minute,
    start=datetime(2023, 1, 1),
    end=datetime(2023, 12, 31)
)
bars = client.get_stock_bars(request)
```

---

### 3. Tiingo (BEST FOR HISTORICAL RESEARCH)
- **Rate Limit**: 50 symbols/hour
- **Historical Depth**: 30+ years
- **Intraday**: Daily only (no minute-level)
- **Real-Time**: No
- **Uptime**: Reliable for research
- **Cost**: Free forever
- **Best For**: Long-term backesting, research
- **Python Library**: `tiingo`

**Key Code**:
```python
import tiingo
tiingo.conf['api_key'] = 'YOUR_KEY'
df = tiingo.get_dataframe('AAPL', startDate='2020-01-01', endDate='2023-12-31')
```

---

## Quick Comparison Matrix

| Feature | Finnhub | Alpaca | Polygon | FMP | yfinance |
|---------|---------|--------|---------|-----|----------|
| Daily OHLCV | ✅ | ✅ | ✅ | ✅ | ✅ |
| Minute-level | ✅ | ✅ | ✅ | ✅ | ✅ |
| Real-time | ✅ | Partial | Paid | ✅ | ❌ |
| Rate Limit | 60/min | 200/min | 5/min | 250/day | ~2k/hr |
| Historical | 1yr/call | 6+ yrs | 2 yrs | 5+ yrs | 15+ yrs |
| Uptime SLA | 99.99% | Excellent | Good | 99.9% | None |
| No API Key? | ❌ | ✅ | ❌ | ❌ | ✅ |
| Cost | Free | Free | Free | Free | Free |
| **Risk Level** | Low | Low | Low | Low | HIGH |

---

## Use Case Recommendations

### For Daily Portfolio Monitoring
Use **Finnhub** (60/min is enough for 100 stocks twice daily)
```python
for symbol in symbols:
    quote = client.quote(symbol)
    # Process...
    time.sleep(1)  # 60/min = 1/sec safe
```

### For Minute-Level Backtesting
Use **Alpaca** (200/min, clean data structure)
```python
request = StockBarsRequest(
    symbol_or_symbols=['AAPL', 'MSFT'],
    timeframe=TimeFrame.Minute,
    start=start_date,
    end=end_date
)
bars = client.get_stock_bars(request)
```

### For 20+ Year Historical Research
Use **Tiingo** (30+ years, high quality)
```python
df = tiingo.get_dataframe('AAPL', startDate='1980-01-01', endDate='2023-12-31')
```

### For Sustainable Daily Bot
Combine **Finnhub** (intraday) + **FMP** (fundamentals) + fallback to **yfinance**
```python
def get_data_with_fallback(symbol):
    try:
        return get_finnhub(symbol)
    except:
        try:
            return get_fmp(symbol)
        except:
            return get_yfinance(symbol)
```

---

## API Endpoints Reference

### Finnhub Endpoints (Most Used)
```
GET /stock/candles  # OHLCV data
GET /quote          # Real-time quotes
GET /company-basic-financials  # Company data
```

### Alpaca Endpoints (Most Used)
```
GET /v2/stocks/bars  # Historical bars/candles
GET /v2/stocks/quotes  # Real-time quotes
GET /v2/stocks/{symbol}/bars  # Single symbol bars
```

### FMP Endpoints (Most Used)
```
GET /historical-price-full/{symbol}  # Daily OHLCV
GET /historical-chart/{interval}/{symbol}  # Intraday
GET /quote/{symbol}  # Real-time quotes
```

---

## Rate Limit Strategy

### Safe Approach (Won't Hit Limits)
```python
import time

# For Finnhub: 60 calls/min = 1 per second is safe
for symbol in symbols:
    data = client.stock_candles(symbol, 'D', start, end)
    time.sleep(1)  # 1 second delay

# For Alpaca: 200 calls/min = 5 per second is safe
# Can batch 10 symbols and sleep 2 seconds

# For FMP: 250/day = ~10 calls per hour max
# Process symbols in daily batches
```

### Rate Limit Detection & Handling
```python
def api_call_with_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = (2 ** attempt) * 60  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(5)
```

---

## Common Pitfalls & Solutions

### Pitfall 1: yfinance IP Bans
**Problem**: Gets 999 HTTP errors and IP blocked
**Solution**: Don't use for production. Use Finnhub or Alpaca instead.

### Pitfall 2: Hitting Finnhub 1-Year Limit
**Problem**: Only get 1 year of data per call
**Solution**: 
```python
for year in range(start_year, end_year + 1):
    data = client.stock_candles(symbol, 'D', year_start, year_end)
    all_data.append(data)
    time.sleep(1)
```

### Pitfall 3: FMP 250 Daily Calls
**Problem**: Not enough for large-scale monitoring
**Solution**: Use for daily batch job, not real-time

### Pitfall 4: Polygon 5/min Too Slow
**Problem**: Can't fetch data fast enough
**Solution**: Use Finnhub (60/min) or Alpaca (200/min) instead

---

## Data Validation Checklist

Always validate OHLCV data before use:
```python
def validate_ohlcv(df):
    assert (df['high'] >= df['low']).all(), "High < Low found"
    assert (df['high'] >= df['close']).all(), "High < Close found"
    assert (df['low'] <= df['close']).all(), "Low > Close found"
    assert (df['volume'] > 0).all(), "Zero volume found"
    assert not df.isnull().any().any(), "Missing data found"
    assert not df.index.duplicated().any(), "Duplicate timestamps"
    return True
```

---

## Installation Commands

```bash
# Install all major free APIs
pip install yfinance finnhub-python alpaca-py polygon-python tiingo requests pandas

# Or individual
pip install finnhub-python   # Recommended
pip install alpaca-py        # Recommended
pip install tiingo          # Recommended
pip install yfinance        # Quick testing only
```

---

## 2025 Recommendation Summary

For **production systems**: Use **Finnhub** (99.99% uptime, 60/min free)
For **minute-level data**: Use **Alpaca** (200/min, clean SDK)
For **historical research**: Use **Tiingo** (30+ years, high quality)
For **alternatives**: Polygon ($29+), FMP (250/day), yfinance (testing only)

**Avoid**: Using single API without fallback - combine at least 2

---

## API Status (Nov 2025)

- Finnhub: ✅ Active, Reliable
- Alpaca: ✅ Active, Reliable
- Tiingo: ✅ Active, Reliable
- Polygon: ✅ Rebranded to Massive.com Oct 2025, backwards compatible
- FMP: ✅ Active
- yfinance: ⚠️ Community-maintained, fragile
- Alpha Vantage: ⚠️ Very restrictive free tier
- EODHD: ✅ Active but limited free tier
- IEX Cloud: ❌ Shut down August 2024 (cautionary tale)

---

## Key Takeaway

No single free API is perfect. Build your system with:
1. **Primary API**: Finnhub (reliable, generous rate limit)
2. **Secondary API**: Alpaca (minute-level data, no API key needed)
3. **Tertiary API**: yfinance (fallback for simple testing)
4. **Error handling**: Exponential backoff, retry logic
5. **Validation**: Check data for OHLC consistency before use

This hybrid approach ensures reliability while staying completely free.
