"""
Data Acquisition Module
Handles multi-source stock data downloading with caching, rate limiting, and error handling.
"""

import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from functools import lru_cache
import redis
import pickle
import yfinance as yf
from dataclasses import dataclass
import os
import requests
from io import StringIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class DataSourceConfig:
    """Configuration for data sources"""
    name: str
    enabled: bool
    priority: int
    rate_limit: int  # requests per minute
    api_key: Optional[str] = None


class MultiSourceDataAcquirer:
    """
    High-performance data acquisition from multiple sources.
    Implements async downloading, caching, and fallback mechanisms.
    """

    def __init__(self, config: dict):
        self.config = config
        self.redis_client = None
        self.request_times = {}

        # Initialize Redis if available
        try:
            self.redis_client = redis.Redis(
                host=config.get('redis', {}).get('host', 'localhost'),
                port=config.get('redis', {}).get('port', 6379),
                decode_responses=False
            )
            self.redis_client.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Caching disabled.")
            self.redis_client = None

        # Load API keys
        self.api_keys = self._load_api_keys()

    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from environment or .env file"""
        keys = {}

        # Try to load from .env file
        env_file = self.config.get('data', {}).get('api_keys_file', '.env')
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        keys[key.strip()] = value.strip()

        # Override with environment variables
        for key in ['FINNHUB_API_KEY', 'ALPACA_API_KEY', 'ALPHA_VANTAGE_KEY']:
            if key in os.environ:
                keys[key] = os.environ[key]

        return keys

    # ==================== CACHING ====================

    def _get_cache_key(self, symbol: str, start_date: str, end_date: str, interval: str) -> str:
        """Generate cache key"""
        return f"stock:{symbol}:{start_date}:{end_date}:{interval}"

    def _get_from_cache(self, cache_key: str) -> Optional[pd.DataFrame]:
        """Get data from Redis cache"""
        if not self.redis_client:
            return None

        try:
            data = self.redis_client.get(cache_key)
            if data:
                logger.info(f"Cache hit: {cache_key}")
                return pickle.loads(data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        return None

    def _save_to_cache(self, cache_key: str, df: pd.DataFrame, ttl: int = 3600):
        """Save data to Redis cache"""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                cache_key,
                ttl,
                pickle.dumps(df)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")

    # ==================== DATA SOURCE: YFINANCE ====================

    def _fetch_yfinance(self, symbol: str, start_date: str, end_date: str, interval: str = '5m') -> pd.DataFrame:
        """Fetch data from yfinance (free, unlimited)"""
        try:
            ticker = yf.Ticker(symbol)

            # yfinance interval mapping
            yf_interval = interval.replace('min', 'm')

            # Download data
            df = ticker.history(start=start_date, end=end_date, interval=yf_interval)

            if df.empty:
                raise ValueError(f"No data returned for {symbol}")

            # Standardize column names
            df.columns = [col.lower() for col in df.columns]

            # Ensure required columns
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_cols):
                raise ValueError(f"Missing required columns for {symbol}")

            logger.info(f"yfinance: Successfully fetched {symbol} ({len(df)} rows)")
            return df

        except Exception as e:
            logger.error(f"yfinance error for {symbol}: {e}")
            raise

    # ==================== DATA SOURCE: FINNHUB ====================

    async def _fetch_finnhub_async(self, session: aiohttp.ClientSession, symbol: str,
                                   start_timestamp: int, end_timestamp: int, interval: str) -> pd.DataFrame:
        """Fetch data from Finnhub API (async)"""
        api_key = self.api_keys.get('FINNHUB_API_KEY')
        if not api_key:
            raise ValueError("FINNHUB_API_KEY not found")

        # Finnhub resolution mapping
        resolution_map = {'1min': '1', '5min': '5', '15min': '15', '30min': '30', '60min': '60'}
        resolution = resolution_map.get(interval, '5')

        url = f"https://finnhub.io/api/v1/stock/candle"
        params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': start_timestamp,
            'to': end_timestamp,
            'token': api_key
        }

        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            resp.raise_for_status()
            data = await resp.json()

            if data.get('s') != 'ok':
                raise ValueError(f"Finnhub error for {symbol}: {data.get('s')}")

            # Convert to DataFrame
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(data['t'], unit='s'),
                'open': data['o'],
                'high': data['h'],
                'low': data['l'],
                'close': data['c'],
                'volume': data['v']
            })

            df.set_index('timestamp', inplace=True)
            logger.info(f"Finnhub: Successfully fetched {symbol} ({len(df)} rows)")
            return df

    # ==================== RATE LIMITING ====================

    async def _rate_limit_wait(self, source: str, rate_limit: int):
        """Implement rate limiting"""
        now = asyncio.get_event_loop().time()

        # Initialize tracking for this source
        if source not in self.request_times:
            self.request_times[source] = []

        # Remove requests older than 60 seconds
        self.request_times[source] = [
            t for t in self.request_times[source]
            if now - t < 60
        ]

        # Check if we've hit the rate limit
        if len(self.request_times[source]) >= rate_limit:
            sleep_time = 60 - (now - self.request_times[source][0])
            if sleep_time > 0:
                logger.info(f"Rate limit reached for {source}, waiting {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)

        # Record this request
        self.request_times[source].append(now)

    # ==================== MULTI-SOURCE DOWNLOAD WITH FALLBACK ====================

    def download_stock(self, symbol: str, start_date: str, end_date: str, interval: str = '5m') -> pd.DataFrame:
        """
        Download stock data with automatic fallback between sources.
        Priority: Cache → Finnhub → yfinance
        """
        # Check cache first
        cache_key = self._get_cache_key(symbol, start_date, end_date, interval)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Try sources in priority order
        sources = self.config.get('data', {}).get('sources', ['yfinance'])

        for source in sources:
            try:
                if source == 'yfinance':
                    df = self._fetch_yfinance(symbol, start_date, end_date, interval)
                elif source == 'finnhub':
                    # Convert dates to timestamps for Finnhub
                    start_ts = int(pd.Timestamp(start_date).timestamp())
                    end_ts = int(pd.Timestamp(end_date).timestamp())

                    # Use asyncio for single fetch
                    async def fetch():
                        async with aiohttp.ClientSession() as session:
                            await self._rate_limit_wait('finnhub', 60)
                            return await self._fetch_finnhub_async(session, symbol, start_ts, end_ts, interval)

                    df = asyncio.run(fetch())
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue

                # Cache successful result
                ttl = self.config.get('data', {}).get('cache_ttl', 3600)
                self._save_to_cache(cache_key, df, ttl)

                return df

            except Exception as e:
                logger.warning(f"Failed to fetch {symbol} from {source}: {e}")
                continue

        raise ValueError(f"All sources failed for {symbol}")

    # ==================== BATCH DOWNLOAD (MULTI-THREADED) ====================

    def download_multiple_stocks(self, symbols: List[str], start_date: str, end_date: str,
                                 interval: str = '5m', max_workers: int = 50) -> Dict[str, pd.DataFrame]:
        """
        Download multiple stocks using thread pool.
        Returns dict of {symbol: DataFrame}
        """
        logger.info(f"Downloading {len(symbols)} stocks with {max_workers} workers...")

        results = {}
        failed = []

        def fetch_one(symbol):
            try:
                df = self.download_stock(symbol, start_date, end_date, interval)
                return symbol, df, None
            except Exception as e:
                return symbol, None, str(e)

        # Use ThreadPoolExecutor for parallel downloads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(fetch_one, symbol) for symbol in symbols]

            # Collect results
            for future in futures:
                symbol, df, error = future.result()
                if df is not None:
                    results[symbol] = df
                else:
                    failed.append((symbol, error))

        logger.info(f"Successfully downloaded: {len(results)}/{len(symbols)}")
        if failed:
            logger.warning(f"Failed: {len(failed)} stocks")
            for symbol, error in failed[:5]:  # Show first 5 failures
                logger.warning(f"  {symbol}: {error}")

        return results

    # ==================== NEWS DATA ====================

    def fetch_news(self, symbol: str, days_back: int = 7) -> List[Dict]:
        """Fetch news for a symbol (fallback to yfinance)"""
        try:
            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return []

            # Filter by date
            cutoff = datetime.now() - timedelta(days=days_back)
            recent_news = [
                {
                    'title': item.get('title', ''),
                    'publisher': item.get('publisher', ''),
                    'link': item.get('link', ''),
                    'published': datetime.fromtimestamp(item.get('providerPublishTime', 0))
                }
                for item in news
                if datetime.fromtimestamp(item.get('providerPublishTime', 0)) >= cutoff
            ]

            logger.info(f"Fetched {len(recent_news)} news articles for {symbol}")
            return recent_news

        except Exception as e:
            logger.error(f"News fetch error for {symbol}: {e}")
            return []

    # ==================== PRE-MARKET DATA ====================

    def get_premarket_data(self, symbol: str) -> Optional[Dict]:
        """Get pre-market trading data"""
        try:
            ticker = yf.Ticker(symbol)

            # Get today's pre-market data
            today = datetime.now().date()
            premarket = ticker.history(period='1d', interval='1m', prepost=True)

            # Filter for pre-market hours (4:00 AM - 9:30 AM ET)
            if premarket.empty:
                return None

            # Calculate pre-market metrics
            premarket_open = premarket['Open'].iloc[0]
            premarket_high = premarket['High'].max()
            premarket_low = premarket['Low'].min()
            premarket_close = premarket['Close'].iloc[-1]
            premarket_volume = premarket['Volume'].sum()

            return {
                'open': premarket_open,
                'high': premarket_high,
                'low': premarket_low,
                'close': premarket_close,
                'volume': int(premarket_volume),
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Pre-market data error for {symbol}: {e}")
            return None


# ==================== UTILITY FUNCTIONS ====================

def get_sp500_symbols() -> List[str]:
    """Get list of S&P 500 symbols"""
    try:
        # Download S&P 500 list from Wikipedia
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

        # Add headers to avoid 403 Forbidden error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Use requests to fetch with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML tables (use StringIO to avoid FutureWarning)
        tables = pd.read_html(StringIO(response.text))
        df = tables[1]  # S&P 500 table is the second table (index 1)
        symbols = df['Symbol'].tolist()

        # Clean symbols (replace . with -)
        symbols = [s.replace('.', '-') for s in symbols]

        logger.info(f"Fetched {len(symbols)} S&P 500 symbols")
        return symbols

    except Exception as e:
        logger.error(f"Error fetching S&P 500 list: {e}")
        # Fallback to common symbols
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'V', 'JPM']


def get_nasdaq100_symbols() -> List[str]:
    """Get list of NASDAQ-100 symbols"""
    try:
        url = 'https://en.wikipedia.org/wiki/Nasdaq-100'

        # Add headers to avoid 403 Forbidden error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Use requests to fetch with headers
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML tables (use StringIO to avoid FutureWarning)
        tables = pd.read_html(StringIO(response.text))
        df = tables[4]  # NASDAQ-100 components table
        symbols = df['Ticker'].tolist()

        logger.info(f"Fetched {len(symbols)} NASDAQ-100 symbols")
        return symbols

    except Exception as e:
        logger.error(f"Error fetching NASDAQ-100 list: {e}")
        return []


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Example configuration
    config = {
        'data': {
            'sources': ['yfinance'],  # Can add 'finnhub', 'alpaca'
            'cache_ttl': 3600,
            'max_download_workers': 50
        },
        'redis': {
            'host': 'localhost',
            'port': 6379
        }
    }

    # Initialize acquirer
    acquirer = MultiSourceDataAcquirer(config)

    # Download single stock
    print("\n=== Single Stock Download ===")
    df = acquirer.download_stock('AAPL', '2024-01-01', '2024-12-31', '5m')
    print(f"AAPL: {len(df)} rows")
    print(df.head())

    # Download multiple stocks
    print("\n=== Multiple Stocks Download ===")
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA']
    results = acquirer.download_multiple_stocks(symbols, '2024-01-01', '2024-12-31', '5m', max_workers=5)

    for symbol, df in results.items():
        print(f"{symbol}: {len(df)} rows")

    # Fetch news
    print("\n=== News Fetch ===")
    news = acquirer.fetch_news('AAPL', days_back=7)
    for article in news[:3]:
        print(f"- {article['title']} ({article['published']})")

    # Get S&P 500 symbols
    print("\n=== S&P 500 Symbols ===")
    sp500 = get_sp500_symbols()
    print(f"Total symbols: {len(sp500)}")
    print(f"First 10: {sp500[:10]}")
