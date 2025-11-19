# Financial Data APIs - Implementation Guide

## Part 1: Quick Start (5 Minutes)

### Setup 1: Finnhub (Recommended for Most Cases)

```bash
# 1. Install
pip install finnhub-python pandas

# 2. Get API key at https://finnhub.io (free signup)

# 3. Run this script
```

```python
import finnhub
import pandas as pd
from datetime import datetime, timedelta

# Initialize
api_key = 'YOUR_API_KEY_HERE'
client = finnhub.Client(api_key=api_key)

# Get today's quote for Apple
quote = client.quote('AAPL')
print(f"AAPL: ${quote['c']} (change: {quote['d']:.2f})")

# Get 30-day historical data
end_time = int(datetime.now().timestamp())
start_time = int((datetime.now() - timedelta(days=30)).timestamp())

response = client.stock_candles('AAPL', 'D', start_time, end_time)

if response['s'] == 'ok':
    df = pd.DataFrame({
        'date': pd.to_datetime(response['t'], unit='s'),
        'open': response['o'],
        'high': response['h'],
        'low': response['l'],
        'close': response['c'],
        'volume': response['v']
    })
    print("\nLast 5 days of AAPL:")
    print(df.tail())
```

### Setup 2: Alpaca (Best for Minute-Level)

```bash
# 1. Install
pip install alpaca-py pandas

# 2. No API key needed for basic data! (Optional: sign up at alpaca.markets)

# 3. Run this script
```

```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# Initialize (no credentials needed for free tier)
client = StockHistoricalDataClient()

# Get daily data
request = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Day,
    start=datetime(2023, 11, 1),
    end=datetime(2023, 11, 30)
)

bars = client.get_stock_bars(request)
df = bars.df
print("AAPL Daily Data (Nov 2023):")
print(df.head())

# Get minute data (same code, different timeframe)
minute_request = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Minute,
    start=datetime(2023, 11, 17),
    end=datetime(2023, 11, 19)
)

minute_bars = client.get_stock_bars(minute_request)
print("\nAPPL Minute Data:")
print(minute_bars.df.head())
```

### Setup 3: Tiingo (Best for Long Historical Data)

```bash
# 1. Install
pip install tiingo pandas

# 2. Get API key at https://www.tiingo.com (free signup)

# 3. Run this script
```

```python
import tiingo

# Initialize
tiingo.conf['api_key'] = 'YOUR_API_KEY_HERE'

# Get 5 years of historical data
df = tiingo.get_dataframe(
    'AAPL',
    startDate='2018-01-01',
    endDate='2023-12-31'
)

print("AAPL 5-Year Historical Data:")
print(df.head())
print(f"\nData from {df.index[0]} to {df.index[-1]}")
print(f"Total rows: {len(df)}")
```

---

## Part 2: Production-Ready Implementation

### Complete API Manager Class

```python
import finnhub
import alpaca
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import pandas as pd
import time
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinancialDataManager:
    """
    Manages stock data fetching from multiple free APIs
    with intelligent fallback and rate limiting
    """
    
    def __init__(self, finnhub_key=None):
        self.finnhub_client = None
        self.alpaca_client = StockHistoricalDataClient()
        
        if finnhub_key:
            self.finnhub_client = finnhub.Client(api_key=finnhub_key)
        
        # Rate limiting: (calls, per_seconds)
        self.rate_limits = {
            'finnhub': (60, 60),      # 60 per minute
            'alpaca': (200, 60),      # 200 per minute
        }
        self.last_call = {}
    
    def _rate_limit_check(self, api_name):
        """Enforce rate limits"""
        if api_name not in self.rate_limits:
            return
        
        calls_allowed, per_seconds = self.rate_limits[api_name]
        if api_name not in self.last_call:
            self.last_call[api_name] = []
        
        now = time.time()
        # Remove old calls outside the window
        self.last_call[api_name] = [
            t for t in self.last_call[api_name] 
            if now - t < per_seconds
        ]
        
        if len(self.last_call[api_name]) >= calls_allowed:
            sleep_time = per_seconds - (now - self.last_call[api_name][0])
            logger.warning(f"Rate limit approaching for {api_name}. Sleeping {sleep_time}s")
            time.sleep(sleep_time + 0.1)
        
        self.last_call[api_name].append(now)
    
    def get_daily_data_finnhub(self, symbol, days=365):
        """Get daily OHLCV data from Finnhub"""
        if not self.finnhub_client:
            raise ValueError("Finnhub API key not configured")
        
        self._rate_limit_check('finnhub')
        
        end_time = int(datetime.now().timestamp())
        start_time = int((datetime.now() - timedelta(days=days)).timestamp())
        
        try:
            response = self.finnhub_client.stock_candles(symbol, 'D', start_time, end_time)
            
            if response['s'] == 'ok':
                df = pd.DataFrame({
                    'date': pd.to_datetime(response['t'], unit='s'),
                    'open': response['o'],
                    'high': response['h'],
                    'low': response['l'],
                    'close': response['c'],
                    'volume': response['v']
                })
                return df.sort_values('date')
        except Exception as e:
            logger.error(f"Finnhub error for {symbol}: {e}")
        
        return None
    
    def get_daily_data_alpaca(self, symbol, days=365):
        """Get daily OHLCV data from Alpaca"""
        self._rate_limit_check('alpaca')
        
        try:
            request = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Day,
                start=datetime.now() - timedelta(days=days),
                end=datetime.now()
            )
            
            bars = self.alpaca_client.get_stock_bars(request)
            return bars.df.reset_index()
        except Exception as e:
            logger.error(f"Alpaca error for {symbol}: {e}")
        
        return None
    
    def get_minute_data_alpaca(self, symbol, days=7):
        """Get minute-level OHLCV data from Alpaca"""
        self._rate_limit_check('alpaca')
        
        try:
            request = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(days=days),
                end=datetime.now()
            )
            
            bars = self.alpaca_client.get_stock_bars(request)
            return bars.df.reset_index()
        except Exception as e:
            logger.error(f"Alpaca minute data error for {symbol}: {e}")
        
        return None
    
    def get_daily_data_with_fallback(self, symbol, days=365):
        """
        Try multiple APIs in sequence for maximum reliability
        """
        # Try Finnhub first
        if self.finnhub_client:
            logger.info(f"Fetching {symbol} from Finnhub...")
            data = self.get_daily_data_finnhub(symbol, days)
            if data is not None and len(data) > 0:
                logger.info(f"Successfully fetched {symbol} from Finnhub ({len(data)} rows)")
                return data, 'finnhub'
        
        # Fall back to Alpaca
        logger.info(f"Fetching {symbol} from Alpaca...")
        data = self.get_daily_data_alpaca(symbol, days)
        if data is not None and len(data) > 0:
            logger.info(f"Successfully fetched {symbol} from Alpaca ({len(data)} rows)")
            return data, 'alpaca'
        
        logger.error(f"Failed to fetch data for {symbol}")
        return None, None
    
    def get_batch_data(self, symbols, days=365):
        """Fetch data for multiple symbols with rate limiting"""
        results = {}
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Processing {symbol} ({i+1}/{len(symbols)})")
            data, source = self.get_daily_data_with_fallback(symbol, days)
            results[symbol] = {
                'data': data,
                'source': source,
                'success': data is not None
            }
            
            # Small delay between requests
            if i < len(symbols) - 1:
                time.sleep(0.5)
        
        return results
    
    def validate_ohlcv(self, df):
        """Validate OHLCV data integrity"""
        issues = []
        
        if (df['high'] < df['low']).any():
            issues.append("High < Low found")
        if (df['high'] < df['close']).any():
            issues.append("High < Close found")
        if (df['low'] > df['close']).any():
            issues.append("Low > Close found")
        if (df['volume'] <= 0).any():
            issues.append("Zero or negative volume")
        if df.isnull().any().any():
            issues.append("Missing data found")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }

# Usage Example
if __name__ == '__main__':
    # Initialize manager
    manager = FinancialDataManager(finnhub_key='YOUR_KEY')
    
    # Get data for multiple stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    
    print("Fetching stock data...")
    results = manager.get_batch_data(symbols, days=30)
    
    # Display results
    for symbol, result in results.items():
        if result['success']:
            validation = manager.validate_ohlcv(result['data'])
            print(f"{symbol}: {len(result['data'])} rows from {result['source']} - Valid: {validation['valid']}")
        else:
            print(f"{symbol}: FAILED")
```

---

## Part 3: Specific Use Cases

### Use Case 1: Daily Stock Screener

```python
import finnhub
import pandas as pd
from datetime import datetime

def daily_stock_screener(api_key, symbols):
    """
    Screen stocks based on daily performance
    """
    client = finnhub.Client(api_key=api_key)
    results = []
    
    for symbol in symbols:
        try:
            quote = client.quote(symbol)
            
            results.append({
                'symbol': symbol,
                'price': quote['c'],
                'change': quote['d'],
                'change_pct': quote['dp'],
                'high_52w': quote.get('h52', None),
                'low_52w': quote.get('l52', None),
                'volume': quote.get('v', None)
            })
            
            time.sleep(1)  # Rate limit friendly (60/min)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    
    df = pd.DataFrame(results)
    
    # Filter gainers > 2%
    gainers = df[df['change_pct'] > 2.0].sort_values('change_pct', ascending=False)
    
    # Filter losers < -2%
    losers = df[df['change_pct'] < -2.0].sort_values('change_pct')
    
    print("Top Gainers:")
    print(gainers[['symbol', 'price', 'change_pct']].to_string())
    
    print("\nTop Losers:")
    print(losers[['symbol', 'price', 'change_pct']].to_string())
    
    return df

# Usage
# results = daily_stock_screener('YOUR_KEY', ['AAPL', 'MSFT', 'GOOGL', 'TSLA', ...])
```

### Use Case 2: Minute-Level Backtest

```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import pandas as pd

def simple_moving_average_strategy(symbol, fast=20, slow=50):
    """
    Simple moving average crossover backtest
    """
    client = StockHistoricalDataClient()
    
    # Get minute data
    request = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Minute,
        start=datetime(2023, 1, 1),
        end=datetime(2023, 12, 31)
    )
    
    bars = client.get_stock_bars(request)
    df = bars.df.reset_index()
    df = df.sort_values('timestamp')
    
    # Calculate moving averages
    df['fast_ma'] = df['close'].rolling(window=fast).mean()
    df['slow_ma'] = df['close'].rolling(window=slow).mean()
    
    # Generate signals (1=BUY, -1=SELL, 0=HOLD)
    df['signal'] = 0
    df.loc[df['fast_ma'] > df['slow_ma'], 'signal'] = 1  # BUY
    df.loc[df['fast_ma'] < df['slow_ma'], 'signal'] = -1  # SELL
    
    # Calculate returns
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['signal'].shift(1) * df['returns']
    
    # Calculate metrics
    total_return = (1 + df['strategy_returns']).prod() - 1
    sharpe_ratio = df['strategy_returns'].mean() / df['strategy_returns'].std() * (252 ** 0.5)
    max_drawdown = (df['strategy_returns'].cumsum()).min()
    
    print(f"{symbol} Backtest Results ({fast}/{slow} MA):")
    print(f"Total Return: {total_return:.2%}")
    print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    print(f"Max Drawdown: {max_drawdown:.2%}")
    
    return df

# Usage
# results = simple_moving_average_strategy('AAPL', fast=20, slow=50)
```

### Use Case 3: Long-Term Historical Analysis

```python
import tiingo
import pandas as pd
from datetime import datetime

def analyze_long_term_trends(api_key, symbol):
    """
    Analyze 20+ years of stock data for long-term trends
    """
    tiingo.conf['api_key'] = api_key
    
    # Get entire history (can go back 30+ years)
    df = tiingo.get_dataframe(
        symbol,
        startDate='1990-01-01',
        endDate=datetime.now().strftime('%Y-%m-%d')
    )
    
    # Calculate metrics
    df['returns'] = df['close'].pct_change()
    df['log_returns'] = np.log(df['close'] / df['close'].shift(1))
    
    # Yearly returns
    yearly = df.groupby(df.index.year).apply(
        lambda x: (x['close'].iloc[-1] / x['close'].iloc[0] - 1) * 100
    )
    
    # Calculate volatility by decade
    df['decade'] = df.index.year // 10 * 10
    volatility_by_decade = df.groupby('decade')['returns'].std() * np.sqrt(252)
    
    print(f"{symbol} Long-Term Analysis:")
    print(f"Total Period: {df.index[0].date()} to {df.index[-1].date()}")
    print(f"Total Return: {(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.1f}%")
    print(f"Annual Volatility: {df['returns'].std() * np.sqrt(252):.2%}")
    print(f"Best Year: {yearly.max():.1f}% ({yearly.idxmax()})")
    print(f"Worst Year: {yearly.min():.1f}% ({yearly.idxmin()})")
    
    return df

# Usage
# df = analyze_long_term_trends('YOUR_KEY', 'AAPL')
```

---

## Part 4: Error Handling & Recovery

```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, backoff=2):
    """Decorator for API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    
                    wait_time = backoff ** attempt
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    time.sleep(wait_time)
        
        return wrapper
    return decorator

# Usage
@retry_on_failure(max_retries=3, backoff=2)
def fetch_data(symbol):
    # Your API call here
    return client.quote(symbol)
```

---

## Part 5: Environment Setup

```bash
# Create virtual environment
python -m venv venv_finance
source venv_finance/bin/activate  # On Windows: venv_finance\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**requirements.txt**:
```
finnhub-python==1.5.10
alpaca-py==0.9.0
tiingo==0.21.0
pandas==2.0.0
numpy==1.24.0
python-dotenv==1.0.0
requests==2.31.0
```

---

## Part 6: Configuration Management

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')
    TIINGO_API_KEY = os.getenv('TIINGO_API_KEY')
    
    # Rate limits (calls per minute)
    FINNHUB_RATE_LIMIT = 60
    ALPACA_RATE_LIMIT = 200
    
    # Data ranges
    DEFAULT_LOOKBACK_DAYS = 365
    MINUTE_DATA_LOOKBACK_DAYS = 7
    HISTORICAL_LOOKBACK_DAYS = 20 * 365  # 20 years

# Usage in main script
from config import Config

finnhub_key = Config.FINNHUB_API_KEY
if not finnhub_key:
    raise ValueError("FINNHUB_API_KEY not set in .env")
```

**.env** (create this file, don't commit to git):
```
FINNHUB_API_KEY=your_key_here
TIINGO_API_KEY=your_key_here
```

---

## Summary

1. Start with Finnhub for most daily monitoring tasks
2. Use Alpaca for minute-level backtesting
3. Use Tiingo for long-term historical research
4. Implement fallback mechanisms
5. Respect rate limits
6. Validate data before using
7. Monitor uptime and reliability

Total free monthly cost: $0 (while respecting rate limits)
