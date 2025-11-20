# Comprehensive Cryptocurrency Historical Data Sources for Quantitative Trading

This document provides a comprehensive overview of historical cryptocurrency data sources suitable for pre-market quantitative trading, including exchange APIs, data aggregators, specialized providers, on-chain data sources, and DeFi protocol data.

---

## Table of Contents

1. [Exchange APIs](#1-exchange-apis)
2. [Data Aggregators](#2-data-aggregators)
3. [Specialized Institutional-Grade Providers](#3-specialized-institutional-grade-providers)
4. [On-Chain Data Providers](#4-on-chain-data-providers)
5. [DeFi Protocol Data Sources](#5-defi-protocol-data-sources)
6. [Comparison Matrix](#comparison-matrix)
7. [Best Practices](#best-practices)

---

## 1. Exchange APIs

### 1.1 Binance

**URL:** https://www.binance.com/en/binance-api

**Data Coverage:**
- 350+ cryptocurrencies
- Spot, Futures, Margin, Options markets
- Historical data available from 2017
- All major trading pairs

**Data Granularity:**
- Real-time tick data
- Kline/Candlestick: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M

**Data Fields:**
- OHLCV (Open, High, Low, Close, Volume)
- Trades (price, quantity, timestamp, buyer/seller maker)
- Order book depth (bids/asks)
- 24hr ticker statistics
- Funding rates (futures)
- Open interest

**Access Methods:**
- REST API
- WebSocket streams (real-time)
- Historical data download (CSV)

**Cost:**
- Free tier with rate limits
- VIP tiers (0-9) with higher limits based on trading volume
- Rate limits: 1200 requests/minute (weight-based)

**Data Quality:**
- Excellent - largest exchange by volume
- High reliability and uptime
- Comprehensive historical depth

**Historical Depth:**
- Full historical data since 2017
- Tick-by-tick data retention varies by market

**Code Example:**

```python
# Using python-binance library
from binance.client import Client
import pandas as pd
from datetime import datetime

# Initialize client (no API key needed for public data)
client = Client()

# Get historical klines (candlestick data)
klines = client.get_historical_klines(
    "BTCUSDT",
    Client.KLINE_INTERVAL_1HOUR,
    "1 Jan, 2020",
    "1 Jan, 2024"
)

# Convert to DataFrame
df = pd.DataFrame(klines, columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_volume', 'trades', 'taker_buy_base',
    'taker_buy_quote', 'ignore'
])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Get recent trades
trades = client.get_recent_trades(symbol='BTCUSDT', limit=1000)

# WebSocket for real-time data
from binance.streams import ThreadedWebsocketManager

def handle_socket_message(msg):
    print(f"Price: {msg['p']}, Quantity: {msg['q']}")

twm = ThreadedWebsocketManager()
twm.start()
twm.start_trade_socket(callback=handle_socket_message, symbol='BTCUSDT')
```

---

### 1.2 Coinbase Advanced Trade (formerly Pro)

**URL:** https://docs.cloud.coinbase.com/advanced-trade-api/docs

**Data Coverage:**
- 200+ cryptocurrencies
- Spot markets primarily
- Historical data from 2015
- Major fiat pairs (USD, EUR, GBP)

**Data Granularity:**
- Real-time tick data
- Candles: 1m, 5m, 15m, 1h, 6h, 1d

**Data Fields:**
- OHLCV
- Trades (price, size, side, timestamp)
- Level 2 order book (top 50 bids/asks)
- Level 3 order book (full order book, real-time only)

**Access Methods:**
- REST API
- WebSocket Feed
- FIX API (institutional)

**Cost:**
- Free tier available
- Rate limits: 10 requests/second (public), 15 requests/second (private)
- Higher limits for institutional clients

**Data Quality:**
- Excellent - regulated US exchange
- High institutional quality
- Reliable and audited

**Historical Depth:**
- Full historical data since 2015
- Granular candle data up to 300 data points per request

**Code Example:**

```python
# Using coinbase-advanced-py library
from coinbase.rest import RESTClient
import json

# Initialize client
client = RESTClient(api_key="YOUR_API_KEY", api_secret="YOUR_API_SECRET")

# Get historical candles
candles = client.get_candles(
    product_id="BTC-USD",
    start="2023-01-01T00:00:00Z",
    end="2023-12-31T23:59:59Z",
    granularity="ONE_HOUR"
)

# Get product ticker
ticker = client.get_product(product_id="BTC-USD")
print(json.dumps(ticker, indent=2))

# WebSocket example
from coinbase.websocket import WSClient

def on_message(msg):
    print(json.dumps(msg, indent=2))

ws = WSClient(on_message=on_message)
ws.subscribe(
    product_ids=["BTC-USD"],
    channels=["ticker", "level2"]
)
ws.run_forever()
```

---

### 1.3 Kraken

**URL:** https://docs.kraken.com/rest/

**Data Coverage:**
- 200+ cryptocurrencies
- Spot and Futures markets
- Historical data from 2013
- Strong EUR and fiat pairs

**Data Granularity:**
- Real-time tick data
- OHLC: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 15d

**Data Fields:**
- OHLCV with VWAP
- Trades (price, volume, time, buy/sell, market/limit)
- Order book (bids/asks with depth)
- Spread data
- Ticker information

**Access Methods:**
- REST API
- WebSocket API

**Cost:**
- Free tier available
- Rate limits tiered by verification level
- Base: 15 requests/minute, Intermediate: 20/min

**Data Quality:**
- Excellent - one of oldest exchanges
- High reliability
- Strong European presence

**Historical Depth:**
- Historical data since 2013
- Complete OHLC history available

**Code Example:**

```python
# Using krakenex library
import krakenex
import pandas as pd
from pykrakenapi import KrakenAPI

# Initialize client
api = krakenex.API()
k = KrakenAPI(api)

# Get OHLC data
ohlc, last = k.get_ohlc_data("XXBTZUSD", interval=60)  # 60 min intervals
print(ohlc.head())

# Get recent trades
trades, last = k.get_recent_trades("XXBTZUSD")
print(trades.head())

# Get order book
book = k.get_order_book("XXBTZUSD", count=100)
print(book)

# WebSocket example
import asyncio
from kraken.websockets import KrakenWebsockets

async def main():
    async with KrakenWebsockets() as session:
        await session.subscribe(
            subscription={"name": "trade"},
            pair=["XBT/USD"]
        )
        async for message in session:
            print(message)

asyncio.run(main())
```

---

## 2. Data Aggregators

### 2.1 CoinGecko API

**URL:** https://www.coingecko.com/en/api

**Data Coverage:**
- 17,000+ cryptocurrencies
- 1,000+ exchanges integrated
- 2+ million tokens
- NFT collection data
- Global market coverage

**Data Granularity:**
- Daily historical prices
- Hourly data (paid tiers)
- Real-time prices

**Data Fields:**
- OHLCV
- Market cap
- Trading volume
- Total supply, circulating supply
- Price changes (1h, 24h, 7d, 30d, 1y)
- All-time high/low
- Developer stats, community stats
- Exchange volumes

**Access Methods:**
- REST API (JSON)
- 60+ endpoints

**Cost:**
- Demo Plan: Free, 30 calls/minute
- Analyst: $129/month, 500 calls/minute, hourly data
- Pro Analyst: $499/month, 1000 calls/minute
- Enterprise: Custom pricing

**Data Quality:**
- Very good - independent aggregator
- Cross-exchange data normalization
- Regular audits and verification

**Historical Depth:**
- Daily data from coin inception
- Some coins have data back to 2013
- Hourly data varies by plan

**Code Example:**

```python
# Using pycoingecko library
from pycoingecko import CoinGeckoAPI
import pandas as pd

# Initialize client
cg = CoinGeckoAPI()

# Get coin market data
bitcoin = cg.get_coin_by_id(id='bitcoin')
print(f"Current Price: ${bitcoin['market_data']['current_price']['usd']}")

# Get historical market data
btc_history = cg.get_coin_market_chart_by_id(
    id='bitcoin',
    vs_currency='usd',
    days='365'  # or 'max' for all available data
)

# Convert to DataFrame
prices_df = pd.DataFrame(btc_history['prices'], columns=['timestamp', 'price'])
prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')

# Get OHLC data
ohlc = cg.get_coin_ohlc_by_id(id='bitcoin', vs_currency='usd', days=90)
ohlc_df = pd.DataFrame(ohlc, columns=['timestamp', 'open', 'high', 'low', 'close'])

# Get market data for multiple coins
markets = cg.get_coins_markets(
    vs_currency='usd',
    order='market_cap_desc',
    per_page=100,
    page=1,
    sparkline=True,
    price_change_percentage='1h,24h,7d'
)

# Get exchange data
exchanges = cg.get_exchanges_list()
exchange_volume = cg.get_exchanges_by_id('binance')
```

---

### 2.2 CoinMarketCap API

**URL:** https://coinmarketcap.com/api/

**Data Coverage:**
- 10,000+ cryptocurrencies
- 790+ exchanges
- Historical data from 2013
- Global metrics

**Data Granularity:**
- Daily historical data
- Hourly data (paid plans)
- 1-minute intervals (enterprise)

**Data Fields:**
- OHLCV
- Market cap rankings
- Trading volume (24h, 7d, 30d)
- Percent changes
- Dominance metrics
- Exchange rankings
- Global metrics

**Access Methods:**
- REST API (JSON)
- Comprehensive endpoint library

**Cost:**
- Basic: Free, 10,000 calls/month, 9 endpoints
- Hobbyist: $29/month, 40,000 calls/month
- Startup: $79/month, 120,000 calls/month, historical data
- Standard: $299/month, 500,000 calls/month
- Professional: $999/month, 3M calls/month
- Enterprise: Custom

**Data Quality:**
- Excellent - industry standard
- Rigorous listing requirements
- Transparent methodologies

**Historical Depth:**
- Daily data since 2013
- Historical snapshots available
- Quote archives

**Code Example:**

```python
# Using python-coinmarketcap library
from coinmarketcapapi import CoinMarketCapAPI
import pandas as pd

# Initialize client
cmc = CoinMarketCapAPI('YOUR_API_KEY')

# Get latest listings
listings = cmc.cryptocurrency_listings_latest(limit=100)

# Get cryptocurrency quotes
quotes = cmc.cryptocurrency_quotes_latest(symbol='BTC,ETH,BNB')
btc_price = quotes.data['BTC']['quote']['USD']['price']

# Get historical data (requires paid plan)
historical = cmc.cryptocurrency_quotes_historical(
    symbol='BTC',
    time_start='2023-01-01',
    time_end='2023-12-31',
    interval='daily'
)

# Get OHLCV data (requires Standard plan or higher)
ohlcv = cmc.cryptocurrency_ohlcv_historical(
    symbol='BTC',
    time_start='2023-01-01',
    time_end='2023-12-31',
    interval='daily'
)

# Get global metrics
global_metrics = cmc.global_metrics_quotes_latest()
print(f"Total Market Cap: ${global_metrics.data['quote']['USD']['total_market_cap']}")

# Get exchange info
exchange_info = cmc.exchange_info(id=270)  # Binance
exchange_map = cmc.exchange_map(listing_status='active')
```

---

### 2.3 CryptoCompare

**URL:** https://min-api.cryptocompare.com/

**Data Coverage:**
- 5,700+ cryptocurrencies
- 260,000+ trading pairs
- 170+ exchanges
- Historical data from 2015

**Data Granularity:**
- Tick-level trade data (enterprise)
- Minute: 1m, 5m, 15m, 30m
- Hourly
- Daily

**Data Fields:**
- OHLCV
- Trades (tick data)
- Order book snapshots
- Volume data
- Social stats
- News sentiment

**Access Methods:**
- REST API
- WebSocket API
- Streaming API

**Cost:**
- Free: Limited calls, 7 days minute history, full daily history
- Tier 1-3: Commercial plans with extended data
- Enterprise: Custom, up to 1 year of minute data, tick-level access

**Data Quality:**
- Very good - comprehensive coverage
- Multiple data sources per pair
- Quality scoring system

**Historical Depth:**
- Daily data since 2015
- Minute data: 7 days (free), up to 1 year (enterprise)
- Tick data available for enterprise

**Code Example:**

```python
# Using cryptocompare library
import cryptocompare
import pandas as pd
from datetime import datetime

# Set API key
cryptocompare.cryptocompare._set_api_key_parameter('YOUR_API_KEY')

# Get current price
price = cryptocompare.get_price('BTC', currency='USD')
print(f"BTC Price: ${price['BTC']['USD']}")

# Get historical daily data
btc_daily = cryptocompare.get_historical_price_day(
    'BTC',
    currency='USD',
    limit=365,
    toTs=datetime(2024, 1, 1)
)
df_daily = pd.DataFrame(btc_daily)

# Get historical hourly data
btc_hourly = cryptocompare.get_historical_price_hour(
    'BTC',
    currency='USD',
    limit=168  # 1 week
)
df_hourly = pd.DataFrame(btc_hourly)

# Get historical minute data
btc_minute = cryptocompare.get_historical_price_minute(
    'BTC',
    currency='USD',
    limit=1440  # 1 day
)

# Get multiple coin prices
coins = ['BTC', 'ETH', 'BNB', 'SOL']
prices = cryptocompare.get_price(coins, currency='USD', full=True)

# Get exchange volume
exchange_volume = cryptocompare.get_exchanges()
```

---

## 3. Specialized Institutional-Grade Providers

### 3.1 CoinAPI

**URL:** https://www.coinapi.io/

**Data Coverage:**
- 400+ exchanges
- Spot, derivatives, options
- 350,000+ trading pairs
- 10+ years historical data

**Data Granularity:**
- Tick-by-tick (nanosecond precision)
- Aggregated OHLCV: 1s, 1m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 7d, 30d

**Data Fields:**
- OHLCV
- Trades (price, size, side, timestamp with nanosecond precision)
- Order book (full depth, snapshots, L1/L2/L3)
- Quotes (best bid/ask)
- Exchange rates
- Index data

**Access Methods:**
- REST API
- WebSocket API
- FIX API
- Flat files (CSV/Parquet)
- Cloud storage integration (S3, Snowflake)

**Cost:**
- Free: 100 requests/day, limited history
- Startup: $79/month, 10,000 req/day
- Streamer: $249/month, 100,000 req/day
- Professional: $499/month, 1M req/day
- Enterprise: Custom pricing for institutional needs

**Data Quality:**
- Excellent - institutional grade
- Normalized across exchanges
- Comprehensive validation
- SLA guarantees

**Historical Depth:**
- 10+ years for major exchanges
- Tick-by-tick data from exchange inception
- Complete order book history

**Code Example:**

```python
# Using CoinAPI Python SDK
import requests
import pandas as pd
from datetime import datetime, timedelta

API_KEY = 'YOUR_API_KEY'
headers = {'X-CoinAPI-Key': API_KEY}

# Get OHLCV data
symbol_id = 'BINANCE_SPOT_BTC_USDT'
period_id = '1HRS'
time_start = '2023-01-01T00:00:00'
time_end = '2023-12-31T23:59:59'

url = f'https://rest.coinapi.io/v1/ohlcv/{symbol_id}/history'
params = {
    'period_id': period_id,
    'time_start': time_start,
    'time_end': time_end,
    'limit': 10000
}

response = requests.get(url, headers=headers, params=params)
ohlcv_data = response.json()
df = pd.DataFrame(ohlcv_data)

# Get trades data
url = f'https://rest.coinapi.io/v1/trades/{symbol_id}/history'
params = {
    'time_start': time_start,
    'limit': 10000
}
trades_response = requests.get(url, headers=headers, params=params)
trades_data = trades_response.json()

# Get order book snapshot
url = f'https://rest.coinapi.io/v1/orderbooks/{symbol_id}/current'
orderbook = requests.get(url, headers=headers).json()

# Get quotes (best bid/ask)
url = f'https://rest.coinapi.io/v1/quotes/{symbol_id}/current'
quote = requests.get(url, headers=headers).json()

# WebSocket streaming
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Trade: {data}")

def on_error(ws, error):
    print(f"Error: {error}")

ws_url = "wss://ws.coinapi.io/v1/"
ws = websocket.WebSocketApp(
    ws_url,
    on_message=on_message,
    on_error=on_error,
    header={'X-CoinAPI-Key': API_KEY}
)

# Subscribe to trades
hello_msg = {
    "type": "hello",
    "apikey": API_KEY,
    "heartbeat": True,
    "subscribe_data_type": ["trade"],
    "subscribe_filter_symbol_id": ["BINANCE_SPOT_BTC_USDT$"]
}
```

---

### 3.2 Tardis.dev

**URL:** https://tardis.dev/

**Data Coverage:**
- 30+ major exchanges
- Spot and derivatives markets
- BitMEX, Deribit, Binance, OKX, Huobi, Bitfinex, Kraken, Bitstamp, Coinbase, Bybit, etc.
- All trading pairs on supported exchanges

**Data Granularity:**
- Tick-by-tick order book updates (L2/L3)
- Individual trades
- Order book snapshots
- Liquidations, funding rates (derivatives)

**Data Fields:**
- L2/L3 order book incremental updates
- Order book snapshots
- Trades (price, size, side, timestamp)
- Quotes
- Funding rates
- Open interest
- Liquidations
- Options chains

**Access Methods:**
- Python client library
- Node.js client library
- CSV downloads (daily updates)
- REST API
- Real-time streaming

**Cost:**
- Free tier: Sample data, limited access
- Basic: $50/month, 1 exchange, 1 month history
- Pro: $250/month, 5 exchanges, 6 months history
- Enterprise: Custom, all exchanges, full history

**Data Quality:**
- Excellent - tick-perfect data
- Raw exchange-native format
- Normalized formats available
- Order book reconstruction capability

**Historical Depth:**
- Hundreds of terabytes of data
- Historical data from exchange listing
- Complete tick history for all supported exchanges
- Daily CSV updates

**Code Example:**

```python
# Using tardis-dev Python library
from tardis_dev import datasets, get_exchange_details
import pandas as pd
from datetime import date

# Download historical data
datasets.download(
    exchange="binance-futures",
    data_types=["trades", "incremental_book_L2", "quotes"],
    from_date=date(2023, 1, 1),
    to_date=date(2023, 1, 31),
    symbols=["BTCUSDT", "ETHUSDT"],
    api_key="YOUR_API_KEY",
    download_dir="./data"
)

# Replay historical data with order book reconstruction
from tardis_dev import replay

def on_message(message):
    if message['type'] == 'book_change':
        print(f"Order book update: {message}")
    elif message['type'] == 'trade':
        print(f"Trade: {message}")

replay(
    exchange="binance-futures",
    from_date=date(2023, 1, 1),
    to_date=date(2023, 1, 2),
    symbols=["BTCUSDT"],
    data_types=["book_change", "trade"],
    api_key="YOUR_API_KEY",
    callback=on_message
)

# Stream real-time data with order book
from tardis_dev import stream

async def process_messages():
    messages = stream(
        exchange="binance-futures",
        symbols=["BTCUSDT"],
        data_types=["book_change", "trade"],
        api_key="YOUR_API_KEY"
    )

    async for message in messages:
        print(message)

# Use order book class
from tardis_dev import OrderBook

order_book = OrderBook("binance-futures", "BTCUSDT")

for message in replay(...):
    order_book.update(message)
    snapshot = order_book.snapshot()
    print(f"Best bid: {snapshot['bids'][0]}, Best ask: {snapshot['asks'][0]}")
```

---

### 3.3 Kaiko

**URL:** https://www.kaiko.com/

**Data Coverage:**
- 100+ exchanges
- Spot and derivatives
- 10,000+ instruments
- Global coverage

**Data Granularity:**
- Tick-level trades
- Order book snapshots (L1/L2)
- Aggregated OHLCV: 1m, 5m, 15m, 30m, 1h, 4h, 1d

**Data Fields:**
- Trades (price, size, side, timestamp)
- Order book (L1: best bid/ask, L2: full depth)
- OHLCV
- VWAP
- Reference rates
- Indices

**Access Methods:**
- REST API
- WebSocket streaming
- CSV downloads
- Snowflake data share
- S3 delivery

**Cost:**
- Enterprise pricing (contact for quote)
- Estimated $9,500 - $55,000 annually
- Average ~$28,500/year
- Tiered ticker packs (Small, Medium, Large, Full)

**Data Quality:**
- Excellent - institutional standard
- Used by major financial institutions
- Comprehensive data validation
- Regulatory-grade quality

**Historical Depth:**
- Complete historical data from 2014
- Tick-level history available
- Full order book snapshots

**Code Example:**

```python
# Using Kaiko API
import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
headers = {'X-Api-Key': API_KEY}
base_url = 'https://us.market-api.kaiko.io/v2'

# Get trades data
endpoint = '/data/trades.v1/exchanges/binance/spot/btc-usdt/trades'
params = {
    'start_time': '2023-01-01T00:00:00Z',
    'end_time': '2023-01-31T23:59:59Z',
    'page_size': 1000
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
trades = response.json()

# Get OHLCV data
endpoint = '/data/trades.v1/exchanges/binance/spot/btc-usdt/aggregations/ohlcv'
params = {
    'start_time': '2023-01-01T00:00:00Z',
    'end_time': '2023-12-31T23:59:59Z',
    'interval': '1h'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
ohlcv = response.json()
df = pd.DataFrame(ohlcv['data'])

# Get order book snapshots
endpoint = '/data/order_book_snapshots.v1/exchanges/binance/spot/btc-usdt/snapshots'
params = {
    'start_time': '2023-01-01T00:00:00Z',
    'interval': '1m'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
orderbook = response.json()

# Get reference rate
endpoint = '/data/analytics.v1/reference-rates/btc-usd'
params = {
    'start_time': '2023-01-01T00:00:00Z',
    'interval': '1h'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
ref_rate = response.json()
```

---

### 3.4 Polygon.io (now Massive.com)

**URL:** https://polygon.io/ (redirects to https://massive.com/)

**Data Coverage:**
- Major cryptocurrencies
- Sourced from Coinbase, Bitfinex, Bitstamp, Kraken
- (Note: Binance no longer active source since 2021)
- Spot markets

**Data Granularity:**
- Real-time tick data
- Aggregates: 1m, 5m, 15m, 30m, 1h, 4h, 1d

**Data Fields:**
- OHLCV
- Trades
- Real-time prices
- Reference data

**Access Methods:**
- REST API
- WebSocket streams
- Flat files

**Cost:**
- Basic: Free (5 API calls/minute, end-of-day data)
- Starter plans: From $25/month
- Stocks + Crypto: $249/month (includes forex)
- 20% discount for annual plans

**Data Quality:**
- Good - reliable institutional data
- Regulated and audited
- Multi-asset platform

**Historical Depth:**
- Historical data varies by subscription
- Real-time and historical depending on tier

**Code Example:**

```python
# Using polygon-api-client
from polygon import RESTClient
import pandas as pd
from datetime import datetime

# Initialize client
client = RESTClient(api_key="YOUR_API_KEY")

# Get aggregates (bars)
aggs = client.get_aggs(
    ticker="X:BTCUSD",
    multiplier=1,
    timespan="hour",
    from_="2023-01-01",
    to="2023-12-31"
)

df = pd.DataFrame([{
    'timestamp': a.timestamp,
    'open': a.open,
    'high': a.high,
    'low': a.low,
    'close': a.close,
    'volume': a.volume
} for a in aggs])

# Get trades
trades = client.list_trades(
    ticker="X:BTCUSD",
    timestamp_gte="2023-01-01",
    limit=50000
)

# Get ticker details
ticker_details = client.get_ticker_details("X:BTCUSD")

# Get last trade
last_trade = client.get_last_crypto_trade(from_="BTC", to="USD")
print(f"Last Price: ${last_trade.price}")

# WebSocket streaming
from polygon.websocket import WebSocketClient

def handle_msg(msgs):
    for msg in msgs:
        print(msg)

ws_client = WebSocketClient(api_key="YOUR_API_KEY", market="crypto")
ws_client.subscribe("XT.BTC-USD", "XA.BTC-USD")  # Trades and aggregates
ws_client.run(handle_msg)
```

---

### 3.5 Amberdata

**URL:** https://www.amberdata.io/

**Data Coverage:**
- 100+ exchanges
- Spot, futures, options, swaps
- DeFi protocols
- On-chain data

**Data Granularity:**
- Tick-level order books
- Nanosecond timestamps
- OHLCV: Minute, hour, day
- VWAP data

**Data Fields:**
- Trades (tick-level)
- Order book (L1/L2/L3)
- OHLCV
- VWAP
- Funding rates
- Open interest
- Liquidations
- On-chain metrics

**Access Methods:**
- REST API
- WebSocket streaming
- S3 data delivery
- Historical bulk downloads

**Cost:**
- Enterprise pricing (contact for quote)
- Custom packages based on needs
- Institutional focus

**Data Quality:**
- Excellent - institutional grade
- High frequency, low latency
- Historical data back to 2012 (some exchanges)
- DeFi data from blockchain genesis

**Historical Depth:**
- Historical data back to 2012 for select exchanges
- DEX data from genesis block
- Complete tick history

**Code Example:**

```python
# Using Amberdata API
import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
headers = {'x-api-key': API_KEY}
base_url = 'https://web3api.io/api/v2'

# Get spot prices (OHLCV)
endpoint = '/market/spot/ohlcv/btc/latest'
params = {
    'exchange': 'binance',
    'timeInterval': 'hours',
    'timeFormat': 'iso'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
ohlcv = response.json()

# Get historical OHLCV
endpoint = '/market/spot/ohlcv/btc/historical'
params = {
    'exchange': 'binance',
    'pair': 'btc_usdt',
    'startDate': '2023-01-01',
    'endDate': '2023-12-31',
    'timeInterval': 'hours'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
hist_data = response.json()

# Get order book
endpoint = '/market/spot/exchanges/binance/pairs/btc_usdt/order-book'
response = requests.get(base_url + endpoint, headers=headers)
orderbook = response.json()

# Get trades
endpoint = '/market/spot/exchanges/binance/pairs/btc_usdt/trades'
params = {'startDate': '2023-01-01', 'endDate': '2023-01-02'}
response = requests.get(base_url + endpoint, headers=headers, params=params)
trades = response.json()

# Get VWAP
endpoint = '/market/spot/vwap/btc'
params = {
    'exchange': 'binance',
    'timeInterval': 'hours',
    'startDate': '2023-01-01'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
vwap = response.json()
```

---

## 4. On-Chain Data Providers

### 4.1 Glassnode

**URL:** https://glassnode.com/

**Data Coverage:**
- Bitcoin, Ethereum, and 20+ other chains
- On-chain metrics
- Exchange flow data
- DeFi metrics
- Network health indicators

**Data Granularity:**
- Block-level data
- Hourly aggregates
- Daily aggregates
- Real-time for select metrics

**Data Fields:**
- Transaction volumes
- Active addresses
- Exchange flows (deposits/withdrawals)
- UTXO age distribution
- Realized cap, MVRV ratio
- Network value metrics
- Miner data
- Stablecoin metrics
- DeFi TVL

**Access Methods:**
- REST API
- Python SDK
- CSV exports
- Web platform

**Cost:**
- Free tier: Limited metrics
- Advanced: $29/month
- Professional: $799/month
- Enterprise: Custom pricing
- API access on Professional tier and above

**Data Quality:**
- Excellent - industry-leading on-chain analytics
- Proprietary metrics
- Institutional-grade research

**Historical Depth:**
- Data from blockchain genesis
- Bitcoin data from 2009
- Ethereum data from 2015

**Code Example:**

```python
# Using Glassnode API
import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
base_url = 'https://api.glassnode.com/v1/metrics'

def get_metric(metric_path, asset='BTC', params=None):
    url = f"{base_url}/{metric_path}"
    default_params = {
        'a': asset,
        'api_key': API_KEY,
        'i': '24h',  # interval: 24h, 1h, 10m
        's': '2023-01-01',  # start date
        'u': '2023-12-31'   # end date
    }
    if params:
        default_params.update(params)

    response = requests.get(url, params=default_params)
    return response.json()

# Active addresses
active_addresses = get_metric('addresses/active_count')
df_active = pd.DataFrame(active_addresses)

# Exchange flow
exchange_inflow = get_metric('transactions/transfers_volume_exchanges_in')
exchange_outflow = get_metric('transactions/transfers_volume_exchanges_out')

# Network value to transaction ratio (NVT)
nvt_ratio = get_metric('indicators/nvt')

# SOPR (Spent Output Profit Ratio)
sopr = get_metric('indicators/sopr')

# Realized cap HODL waves
hodl_waves = get_metric('supply/hodl_waves')

# Mining metrics
hash_rate = get_metric('mining/hash_rate_mean')
difficulty = get_metric('mining/difficulty_latest')

# Market indicators
mvrv = get_metric('indicators/mvrv')
realized_price = get_metric('indicators/realized_price')

# DeFi metrics (for ETH)
tvl = get_metric('defi/total_value_locked', asset='ETH')

# Exchange balances
exchange_balance = get_metric('distribution/balance_exchanges')

# Convert to DataFrame for analysis
df = pd.DataFrame(active_addresses)
df['timestamp'] = pd.to_datetime(df['t'], unit='s')
df['value'] = df['v']
df = df[['timestamp', 'value']]
```

---

### 4.2 CryptoQuant

**URL:** https://cryptoquant.com/

**Data Coverage:**
- Bitcoin, Ethereum, 40+ chains
- Exchange data
- On-chain metrics
- Miner data
- Stablecoin analytics

**Data Granularity:**
- Block-level
- Hourly
- Daily

**Data Fields:**
- Exchange reserves
- Exchange flows (inflow/outflow)
- Miner flows
- Whale transactions
- Network data (hash rate, difficulty)
- Stablecoin metrics
- Futures data
- Options data

**Access Methods:**
- REST API
- Python library
- Web platform
- Data exports

**Cost:**
- Free tier: Basic charts
- Starter: $49/month
- Professional: $199/month
- Premium: $799/month
- API access varies by tier

**Data Quality:**
- Excellent - trusted by institutions
- Real-time exchange data
- Comprehensive on-chain coverage

**Historical Depth:**
- Bitcoin data from 2009
- Ethereum data from 2015
- Historical data from blockchain genesis

**Code Example:**

```python
# Using CryptoQuant API
import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
headers = {'Authorization': f'Bearer {API_KEY}'}
base_url = 'https://api.cryptoquant.com/v1'

# Get exchange reserve
endpoint = '/btc/exchange-flows/reserve'
params = {
    'exchange': 'binance',
    'window': 'day',
    'from': '2023-01-01',
    'to': '2023-12-31'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
reserve_data = response.json()

# Get exchange inflow
endpoint = '/btc/exchange-flows/inflow'
response = requests.get(base_url + endpoint, headers=headers, params=params)
inflow_data = response.json()

# Get exchange outflow
endpoint = '/btc/exchange-flows/outflow'
response = requests.get(base_url + endpoint, headers=headers, params=params)
outflow_data = response.json()

# Get miner flows
endpoint = '/btc/miner-flows/all-miner-to-exchange'
response = requests.get(base_url + endpoint, headers=headers, params=params)
miner_flows = response.json()

# Get network data
endpoint = '/btc/network-data/hash-rate'
response = requests.get(base_url + endpoint, headers=headers, params=params)
hash_rate = response.json()

# Get futures data
endpoint = '/btc/market-data/funding-rates'
params = {
    'exchange': 'binance',
    'window': 'hour',
    'from': '2023-01-01'
}
response = requests.get(base_url + endpoint, headers=headers, params=params)
funding_rates = response.json()

# Process data
df = pd.DataFrame(reserve_data['result']['data'])
df['datetime'] = pd.to_datetime(df['datetime'])
df.set_index('datetime', inplace=True)
```

---

### 4.3 Dune Analytics

**URL:** https://dune.com/

**Data Coverage:**
- Ethereum, Polygon, Optimism, Arbitrum, BSC, Gnosis, Avalanche, etc.
- DeFi protocols
- NFT marketplaces
- DAO data
- Smart contract interactions

**Data Granularity:**
- Block-level
- Transaction-level
- Custom aggregations via SQL

**Data Fields:**
- All blockchain data (transactions, logs, traces)
- Decoded smart contract calls
- Token transfers (ERC20, ERC721, ERC1155)
- Custom metrics via SQL queries
- DEX trades
- Lending protocols
- Staking data

**Access Methods:**
- Web platform (SQL editor)
- API (query results)
- CSV exports
- Embeddable dashboards

**Cost:**
- Free tier: Public queries, limited compute
- Plus: $39/month, private queries, more compute
- Premium: $399/month, priority execution
- Enterprise: Custom pricing, dedicated resources

**Data Quality:**
- Excellent - direct blockchain data
- Community-verified queries
- Transparent methodology

**Historical Depth:**
- Full blockchain history from genesis
- Ethereum data from 2015

**Code Example:**

```python
# Using Dune Analytics API
import requests
import pandas as pd
import time

API_KEY = 'YOUR_API_KEY'
headers = {'X-Dune-API-Key': API_KEY}
base_url = 'https://api.dune.com/api/v1'

# Execute a query
query_id = 123456  # Your saved query ID
endpoint = f'/query/{query_id}/execute'
response = requests.post(base_url + endpoint, headers=headers)
execution_id = response.json()['execution_id']

# Check execution status
status_endpoint = f'/execution/{execution_id}/status'
while True:
    status_response = requests.get(base_url + status_endpoint, headers=headers)
    state = status_response.json()['state']
    if state == 'QUERY_STATE_COMPLETED':
        break
    time.sleep(2)

# Get results
results_endpoint = f'/execution/{execution_id}/results'
results = requests.get(base_url + results_endpoint, headers=headers)
data = results.json()
df = pd.DataFrame(data['result']['rows'])

# Example query you might run on Dune (in SQL):
"""
-- Get Uniswap V3 ETH/USDC pool daily volume
SELECT
    date_trunc('day', block_time) as date,
    SUM(amount0) as eth_volume,
    SUM(amount1) as usdc_volume,
    COUNT(*) as num_swaps
FROM uniswap_v3_ethereum.Pair_evt_Swap
WHERE contract_address = '0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8'
    AND block_time >= '2023-01-01'
GROUP BY 1
ORDER BY 1
"""

# Alternative: Using Dune Client library
from dune_client.client import DuneClient
from dune_client.query import QueryBase

dune = DuneClient(API_KEY)

# Execute query
query = QueryBase(query_id=query_id)
results = dune.run_query(query)

# Get dataframe
df = results.get_rows()
```

---

### 4.4 The Graph Protocol

**URL:** https://thegraph.com/

**Data Coverage:**
- Ethereum, Polygon, Arbitrum, Optimism, Avalanche, BSC, Gnosis, Celo, and more
- 3,000+ subgraphs (APIs)
- Major DeFi protocols (Uniswap, Aave, Compound, etc.)
- NFT platforms
- Custom smart contracts

**Data Granularity:**
- Event-level (smart contract events)
- Block-level
- Real-time indexing

**Data Fields:**
- Custom data defined by subgraphs
- Smart contract events
- Entity relationships
- Token data
- User interactions
- Protocol-specific metrics

**Access Methods:**
- GraphQL API
- Decentralized query network
- Hosted service (being deprecated)
- Subgraph studio

**Cost:**
- Query fees (paid in GRT tokens)
- ~$0.00001 - $0.0001 per query
- Free tier available on hosted service
- Decentralized network pricing varies

**Data Quality:**
- Excellent - decentralized indexing
- Community-maintained subgraphs
- Protocol-level guarantees

**Historical Depth:**
- Data from smart contract deployment
- Complete historical event data

**Code Example:**

```python
# Using The Graph with GraphQL queries
import requests
import pandas as pd

# Uniswap V3 subgraph endpoint
SUBGRAPH_URL = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3'

def query_subgraph(query):
    response = requests.post(SUBGRAPH_URL, json={'query': query})
    return response.json()

# Query Uniswap V3 pool data
query = """
{
  pools(first: 10, orderBy: totalValueLockedUSD, orderDirection: desc) {
    id
    token0 {
      symbol
      name
    }
    token1 {
      symbol
      name
    }
    totalValueLockedUSD
    volumeUSD
    feeTier
  }
}
"""
result = query_subgraph(query)
pools_df = pd.DataFrame(result['data']['pools'])

# Query historical swaps
query = """
{
  swaps(
    first: 1000
    orderBy: timestamp
    orderDirection: desc
    where: {
      pool: "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
      timestamp_gt: 1672531200
    }
  ) {
    id
    timestamp
    amount0
    amount1
    amountUSD
    sqrtPriceX96
    tick
  }
}
"""
result = query_subgraph(query)
swaps_df = pd.DataFrame(result['data']['swaps'])
swaps_df['timestamp'] = pd.to_datetime(swaps_df['timestamp'], unit='s')

# Query pool day data for time series
query = """
{
  poolDayDatas(
    first: 365
    orderBy: date
    orderDirection: desc
    where: {
      pool: "0x8ad599c3a0ff1de082011efddc58f1908eb6e6d8"
    }
  ) {
    date
    volumeUSD
    tvlUSD
    feesUSD
    high
    low
    open
    close
  }
}
"""
result = query_subgraph(query)
day_data_df = pd.DataFrame(result['data']['poolDayDatas'])

# Using Python GraphQL client
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

transport = RequestsHTTPTransport(url=SUBGRAPH_URL)
client = Client(transport=transport, fetch_schema_from_transport=True)

query = gql("""
    query GetTokens {
        tokens(first: 100, orderBy: totalValueLockedUSD, orderDirection: desc) {
            id
            symbol
            name
            decimals
            totalValueLockedUSD
            volume
            txCount
        }
    }
""")

result = client.execute(query)
tokens_df = pd.DataFrame(result['tokens'])
```

---

## 5. DeFi Protocol Data Sources

### 5.1 GeckoTerminal (by CoinGecko)

**URL:** https://www.geckoterminal.com/

**Data Coverage:**
- 21+ million tokens on-chain
- 200+ chains
- 1,400+ DEXs
- Uniswap, SushiSwap, PancakeSwap, Curve, Balancer, etc.

**Data Granularity:**
- Real-time prices
- OHLCV: 1m, 5m, 15m, 1h, 4h, 1d

**Data Fields:**
- Token prices
- Liquidity pool data
- Trading volume
- Pool reserves
- Price changes (5m, 1h, 6h, 24h)
- Market cap
- FDV (fully diluted valuation)

**Access Methods:**
- REST API
- Web platform

**Cost:**
- Free API access
- Rate limits apply

**Data Quality:**
- Good - comprehensive DEX coverage
- Real-time on-chain data
- Multi-chain support

**Historical Depth:**
- OHLCV data varies by pool
- Generally from pool creation

**Code Example:**

```python
# Using GeckoTerminal API
import requests
import pandas as pd

base_url = 'https://api.geckoterminal.com/api/v2'

# Get trending pools on a network
network = 'eth'
endpoint = f'/networks/{network}/trending_pools'
response = requests.get(base_url + endpoint)
trending = response.json()

# Get specific pool data
pool_address = '0x88e6a0c2ddd26feeb64f039a2c41296fcb3f5640'  # USDC/ETH on Uniswap V3
endpoint = f'/networks/{network}/pools/{pool_address}'
response = requests.get(base_url + endpoint)
pool_data = response.json()

# Get OHLCV data for a pool
endpoint = f'/networks/{network}/pools/{pool_address}/ohlcv/hour'
params = {
    'aggregate': '1',  # 1 hour
    'before_timestamp': '1704067200',
    'limit': 1000
}
response = requests.get(base_url + endpoint, params=params)
ohlcv = response.json()

# Convert to DataFrame
ohlcv_list = ohlcv['data']['attributes']['ohlcv_list']
df = pd.DataFrame(ohlcv_list, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Get top pools by network
endpoint = f'/networks/{network}/pools'
params = {'page': 1}
response = requests.get(base_url + endpoint, params=params)
pools = response.json()

# Get new pools
endpoint = f'/networks/{network}/new_pools'
response = requests.get(base_url + endpoint)
new_pools = response.json()

# Search for a token
search_query = 'PEPE'
endpoint = '/search/pools'
params = {'query': search_query}
response = requests.get(base_url + endpoint, params=params)
search_results = response.json()

# Get multiple networks info
endpoint = '/networks'
params = {'page': 1}
response = requests.get(base_url + endpoint, params=params)
networks = response.json()
```

---

### 5.2 Bitquery

**URL:** https://bitquery.io/

**Data Coverage:**
- 40+ blockchains
- DEX trades (Uniswap, PancakeSwap, SushiSwap, QuickSwap, etc.)
- NFT marketplaces
- Mempool data
- Smart money tracking

**Data Granularity:**
- Block-level
- Transaction-level
- Real-time streaming
- Custom aggregations

**Data Fields:**
- DEX trades (price, amount, buyer, seller)
- Token transfers
- Smart contract calls
- Balance changes
- Liquidity pool data
- NFT transfers and sales

**Access Methods:**
- GraphQL API
- WebSocket streaming
- Cloud IDE
- SQL-like queries

**Cost:**
- Free tier: 10,000 points/month
- Developer: $99/month, 100K points
- Startup: $299/month, 500K points
- Business: $999/month, 3M points
- Enterprise: Custom

**Data Quality:**
- Excellent - direct blockchain indexing
- Real-time data
- Historical archives

**Historical Depth:**
- Full blockchain history
- Data from genesis block for each chain

**Code Example:**

```python
# Using Bitquery GraphQL API
import requests
import pandas as pd

API_KEY = 'YOUR_API_KEY'
headers = {'X-API-KEY': API_KEY}
url = 'https://graphql.bitquery.io'

# Query Uniswap V2 trades
query = """
{
  ethereum(network: ethereum) {
    dexTrades(
      options: {limit: 1000, desc: "block.timestamp.time"}
      date: {since: "2023-01-01", till: "2023-12-31"}
      exchangeName: {in: ["Uniswap", "Uniswap v2"]}
      baseCurrency: {is: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"}
      quoteCurrency: {is: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}
    ) {
      block {
        timestamp {
          time
        }
        height
      }
      transaction {
        hash
      }
      baseCurrency {
        symbol
        address
      }
      quoteCurrency {
        symbol
        address
      }
      tradeAmount(in: USD)
      baseAmount
      quoteAmount
      price
      side
    }
  }
}
"""

response = requests.post(url, json={'query': query}, headers=headers)
data = response.json()
trades_df = pd.DataFrame(data['data']['ethereum']['dexTrades'])

# Query token transfers
query = """
{
  ethereum(network: ethereum) {
    transfers(
      date: {since: "2023-01-01"}
      currency: {is: "0xdac17f958d2ee523a2206206994597c13d831ec7"}
      amount: {gt: 1000000}
      options: {limit: 100, desc: "block.timestamp.time"}
    ) {
      block {
        timestamp {
          time
        }
      }
      sender {
        address
      }
      receiver {
        address
      }
      amount
      currency {
        symbol
        name
      }
    }
  }
}
"""

response = requests.post(url, json={'query': query}, headers=headers)
transfers = response.json()

# Query PancakeSwap on BSC
query = """
{
  bsc: ethereum(network: bsc) {
    dexTrades(
      options: {limit: 1000}
      date: {since: "2023-01-01"}
      exchangeName: {is: "Pancake"}
    ) {
      block {
        timestamp {
          time
        }
      }
      baseCurrency {
        symbol
      }
      quoteCurrency {
        symbol
      }
      tradeAmount(in: USD)
      price
    }
  }
}
"""

response = requests.post(url, json={'query': query}, headers=headers)
pancake_trades = response.json()

# Streaming API for real-time data
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"New trade: {data}")

subscription = """
subscription {
  ethereum(network: ethereum) {
    dexTrades(
      exchangeName: {is: "Uniswap v3"}
      baseCurrency: {is: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"}
    ) {
      block {
        timestamp {
          time
        }
      }
      tradeAmount(in: USD)
      price
    }
  }
}
"""

ws_url = "wss://streaming.bitquery.io/graphql"
ws = websocket.WebSocketApp(
    ws_url,
    on_message=on_message,
    header={'X-API-KEY': API_KEY}
)
```

---

### 5.3 DeFi Llama

**URL:** https://defillama.com/

**Data Coverage:**
- 3,000+ DeFi protocols
- 200+ blockchains
- TVL (Total Value Locked)
- Stablecoin data
- DEX volumes
- Yields and APYs

**Data Granularity:**
- Daily snapshots
- Hourly data (some endpoints)
- Real-time TVL

**Data Fields:**
- Protocol TVL
- Chain TVL
- Token prices
- Stablecoin circulating supply
- DEX volumes
- Fees and revenue
- Bridge volumes
- Yields

**Access Methods:**
- REST API (free)
- CSV exports
- Web platform

**Cost:**
- Completely free
- No API key required
- No rate limits (fair use)

**Data Quality:**
- Excellent - community-verified
- Open-source methodology
- Comprehensive protocol coverage

**Historical Depth:**
- TVL data from protocol inception
- Generally 2-3 years of data

**Code Example:**

```python
# Using DeFi Llama API (no auth required)
import requests
import pandas as pd
from datetime import datetime

base_url = 'https://api.llama.fi'

# Get all protocols
protocols = requests.get(f'{base_url}/protocols').json()
protocols_df = pd.DataFrame(protocols)

# Get specific protocol TVL history
protocol_slug = 'uniswap'
tvl_history = requests.get(f'{base_url}/protocol/{protocol_slug}').json()
tvl_df = pd.DataFrame(tvl_history['tvl'])
tvl_df['date'] = pd.to_datetime(tvl_df['date'], unit='s')

# Get current TVL for all chains
chains = requests.get(f'{base_url}/v2/chains').json()
chains_df = pd.DataFrame(chains)

# Get historical chain TVL
chain = 'Ethereum'
chain_tvl = requests.get(f'{base_url}/v2/historicalChainTvl/{chain}').json()
chain_df = pd.DataFrame(chain_tvl)
chain_df['date'] = pd.to_datetime(chain_df['date'], unit='s')

# Get stablecoin data
stablecoins = requests.get(f'{base_url}/stablecoins?includePrices=true').json()
stable_df = pd.DataFrame(stablecoins['peggedAssets'])

# Get stablecoin historical mcap
stablecoin_id = 1  # USDT
stable_history = requests.get(f'{base_url}/stablecoin/{stablecoin_id}').json()

# Get DEX volumes
dex_volumes = requests.get('https://api.llama.fi/overview/dexs').json()
dex_df = pd.DataFrame(dex_volumes['protocols'])

# Get specific DEX historical volume
dex_slug = 'uniswap'
dex_history = requests.get(f'https://api.llama.fi/summary/dexs/{dex_slug}').json()

# Get fees and revenue
fees = requests.get('https://api.llama.fi/overview/fees').json()
fees_df = pd.DataFrame(fees['protocols'])

# Get yields
pools = requests.get('https://yields.llama.fi/pools').json()
pools_df = pd.DataFrame(pools['data'])

# Filter high APY pools
high_apy = pools_df[pools_df['apy'] > 10].sort_values('apy', ascending=False)

# Get bridge volumes
bridges = requests.get('https://bridges.llama.fi/bridges?includeChains=true').json()
bridges_df = pd.DataFrame(bridges['bridges'])

# Get token prices (CoinGecko IDs)
coins = 'ethereum,bitcoin,binancecoin'
prices = requests.get(f'{base_url}/prices/current/coingecko:{coins}').json()
```

---

### 5.4 CryptoDataDownload

**URL:** https://www.cryptodatadownload.com/

**Data Coverage:**
- 20+ exchanges
- Spot and futures markets
- Major cryptocurrency pairs
- Bitcoin and Ethereum on-chain data

**Data Granularity:**
- Tick-level data (premium)
- 1-minute OHLCV
- Hourly, Daily

**Data Fields:**
- OHLCV
- Volume
- Trade count
- On-chain metrics (BTC, ETH)
- CFTC COT data for crypto futures

**Access Methods:**
- CSV downloads
- REST API
- Bulk downloads

**Cost:**
- Free tier: Minute data for select pairs
- Premium: Tick data, more history, API access
- Pricing varies

**Data Quality:**
- Good - sourced from exchanges
- Regularly updated
- Focus on backtesting data

**Historical Depth:**
- Varies by exchange and pair
- Generally 2-4 years for minute data
- Longer for daily data

**Code Example:**

```python
# CryptoDataDownload provides CSV files for download
# No official API, but files can be programmatically downloaded
import pandas as pd
import requests
from io import StringIO

# Example: Download Binance BTC/USDT minute data
# Note: Check the website for current file URLs
base_url = 'https://www.cryptodatadownload.com/cdd/'

# Download function
def download_crypto_data(exchange, pair, timeframe='minute'):
    # Format varies by exchange, check website for current naming
    # This is an example format
    filename = f'{exchange}_{pair}_{timeframe}.csv'
    url = base_url + filename

    try:
        response = requests.get(url)
        # CryptoDataDownload CSVs have metadata rows at top
        df = pd.read_csv(StringIO(response.text), skiprows=1)
        return df
    except Exception as e:
        print(f"Error downloading: {e}")
        return None

# For actual use, you would typically:
# 1. Navigate to https://www.cryptodatadownload.com/
# 2. Select your exchange (e.g., Binance)
# 3. Download the specific CSV file
# 4. Load it locally

# Load local CSV file
df = pd.read_csv('Binance_BTCUSDT_minute.csv', skiprows=1)
df.columns = df.columns.str.strip()

# Convert timestamp
if 'Unix' in df.columns:
    df['timestamp'] = pd.to_datetime(df['Unix'], unit='ms')
elif 'Date' in df.columns:
    df['timestamp'] = pd.to_datetime(df['Date'])

# Clean and prepare data
df['open'] = pd.to_numeric(df['Open'], errors='coerce')
df['high'] = pd.to_numeric(df['High'], errors='coerce')
df['low'] = pd.to_numeric(df['Low'], errors='coerce')
df['close'] = pd.to_numeric(df['Close'], errors='coerce')
df['volume'] = pd.to_numeric(df['Volume'], errors='coerce')

# Set timestamp as index
df.set_index('timestamp', inplace=True)
df.sort_index(inplace=True)

# Remove any NaN rows
df = df.dropna()

print(f"Data loaded: {len(df)} rows")
print(f"Date range: {df.index.min()} to {df.index.max()}")
```

---

### 5.5 Crypto Lake

**URL:** https://crypto-lake.com/

**Data Coverage:**
- 20+ major exchanges
- Spot and derivatives
- Order book data
- Funding rates, open interest

**Data Granularity:**
- Tick-level trades
- 1-minute OHLCV
- Order book snapshots

**Data Fields:**
- Trades (timestamp, price, size, side)
- Order book depth
- OHLCV
- Funding rates
- Open interest

**Access Methods:**
- Python API
- Parquet files
- S3 storage

**Cost:**
- Free tier: Sample data
- Standard: From €50/month
- Premium: Custom pricing
- Pay-per-use options available

**Data Quality:**
- Excellent - optimized for quant research
- High performance
- Clean, normalized data

**Historical Depth:**
- Full historical data from exchange listing
- Multi-year coverage

**Code Example:**

```python
# Using crypto-lake Python library
from crypto_lake import LakeAPI
import pandas as pd

# Initialize client
lake = LakeAPI(api_key='YOUR_API_KEY')

# List available exchanges
exchanges = lake.list_exchanges()
print(exchanges)

# List available symbols for an exchange
symbols = lake.list_symbols('binance')
print(symbols)

# Download trades data
trades = lake.trades(
    exchange='binance',
    symbol='BTC-USDT',
    start='2023-01-01',
    end='2023-01-31'
)
trades_df = pd.DataFrame(trades)

# Download OHLCV data
ohlcv = lake.ohlcv(
    exchange='binance',
    symbol='BTC-USDT',
    start='2023-01-01',
    end='2023-12-31',
    interval='1m'
)
ohlcv_df = pd.DataFrame(ohlcv)

# Download order book snapshots
orderbook = lake.orderbook(
    exchange='binance',
    symbol='BTC-USDT',
    start='2023-01-01 00:00:00',
    end='2023-01-01 01:00:00',
    depth=10  # top 10 levels
)

# Download funding rates (for perpetual futures)
funding = lake.funding_rates(
    exchange='binance',
    symbol='BTC-USDT-PERP',
    start='2023-01-01',
    end='2023-12-31'
)
funding_df = pd.DataFrame(funding)

# Download open interest
oi = lake.open_interest(
    exchange='binance',
    symbol='BTC-USDT-PERP',
    start='2023-01-01',
    end='2023-12-31'
)

# Optimized features
# Data caching
lake.set_cache_dir('./data_cache')

# Parallel downloads
data = lake.trades(
    exchange='binance',
    symbol='BTC-USDT',
    start='2023-01-01',
    end='2023-12-31',
    parallel=True,
    workers=4
)

# Direct parquet access for faster loading
parquet_path = lake.get_parquet_path(
    exchange='binance',
    symbol='BTC-USDT',
    data_type='trades',
    date='2023-01-01'
)
df = pd.read_parquet(parquet_path)
```

---

## Comparison Matrix

| Provider | Type | Cost (Est.) | Historical Depth | Granularity | Data Quality | Best For |
|----------|------|-------------|------------------|-------------|--------------|----------|
| **Binance** | Exchange | Free | Since 2017 | 1m - 1M | Excellent | High-frequency trading, largest liquidity |
| **Coinbase** | Exchange | Free | Since 2015 | 1m - 1d | Excellent | US-regulated data, institutional |
| **Kraken** | Exchange | Free | Since 2013 | 1m - 15d | Excellent | European markets, long history |
| **CoinGecko** | Aggregator | $0-499/mo | Since 2013 | Daily/Hourly | Very Good | Multi-exchange overview, free tier |
| **CoinMarketCap** | Aggregator | $0-999/mo | Since 2013 | Daily/Hourly | Excellent | Market rankings, comprehensive |
| **CryptoCompare** | Aggregator | Free-Enterprise | Since 2015 | Tick/1m/Daily | Very Good | Cross-exchange, social data |
| **CoinAPI** | Institutional | $79-Custom | 10+ years | Tick/1s-30d | Excellent | Normalized data, tick-level |
| **Tardis.dev** | Institutional | $50-Custom | From genesis | Tick/L2/L3 | Excellent | Order book, algo trading |
| **Kaiko** | Institutional | $9.5K-55K/yr | Since 2014 | Tick/1m-1d | Excellent | Institutional, regulatory |
| **Polygon.io** | Multi-Asset | $0-249/mo | Varies | Tick/1m-1d | Good | Multi-asset (stocks+crypto) |
| **Amberdata** | Institutional | Enterprise | Since 2012 | Tick/1m-1d | Excellent | DeFi + market data, low latency |
| **Glassnode** | On-Chain | $29-Custom | From genesis | Block/Hour/Day | Excellent | On-chain analytics, Bitcoin/ETH |
| **CryptoQuant** | On-Chain | $49-799/mo | From genesis | Block/Hour/Day | Excellent | Exchange flows, miner data |
| **Dune Analytics** | On-Chain | $0-399/mo | From genesis | Block/Tx | Excellent | Custom queries, DeFi research |
| **The Graph** | On-Chain | Pay-per-query | From deployment | Event-level | Excellent | DeFi protocols, smart contracts |
| **GeckoTerminal** | DEX | Free | From pool creation | 1m-1d | Good | DEX data, multi-chain |
| **Bitquery** | DEX/On-Chain | $99-Custom | From genesis | Block/Tx | Excellent | DEX trades, blockchain data |
| **DeFi Llama** | DeFi | Free | 2-3 years | Daily/Hourly | Excellent | Protocol TVL, yields, volumes |
| **CryptoDataDownload** | CSV Provider | Free-Premium | 2-4 years | Tick/1m-Daily | Good | Backtesting, CSV downloads |
| **Crypto Lake** | Institutional | €50-Custom | From listing | Tick/1m | Excellent | Quant research, order books |

---

## Best Practices

### 1. Data Source Selection

**For Different Use Cases:**

- **High-Frequency Trading:** Tardis.dev, CoinAPI, Crypto Lake, Kaiko
- **Multi-Exchange Arbitrage:** CoinAPI, Amberdata, CryptoCompare
- **Long-Term Backtesting:** Exchange APIs (Binance, Coinbase, Kraken), CoinGecko
- **On-Chain Analysis:** Glassnode, CryptoQuant, Dune Analytics
- **DeFi Strategies:** The Graph, Bitquery, DeFi Llama, GeckoTerminal
- **Market Research:** CoinMarketCap, CoinGecko, Messari
- **Low Budget/Startup:** Exchange APIs (free), CoinGecko, DeFi Llama

### 2. Data Quality Considerations

**Always:**
- Validate data from multiple sources for critical decisions
- Check for gaps and missing data
- Verify timestamp accuracy and timezone consistency
- Monitor for outliers and erroneous ticks
- Implement data cleaning pipelines
- Store raw data separately from processed data

**Common Issues:**
- Exchange downtime causing data gaps
- Timestamp misalignment across sources
- Wash trading inflating volumes
- Price manipulation on low-liquidity pairs
- API rate limiting during high volatility

### 3. Data Storage Recommendations

**For Time-Series Data:**
```python
# Use efficient storage formats
import pandas as pd
import pyarrow.parquet as pq

# Parquet format (compressed, columnar)
df.to_parquet('btc_usdt_1m.parquet', compression='snappy')

# Or TimescaleDB for SQL-based storage
# Or InfluxDB for time-series specific storage
# Or Arctic (MongoDB-based) for financial data
```

**Storage Hierarchy:**
1. Raw tick data → S3/Parquet (cold storage)
2. Minute/hourly OHLCV → TimescaleDB (warm storage)
3. Real-time feeds → Redis/InfluxDB (hot storage)

### 4. API Rate Limit Management

```python
import time
from functools import wraps
import requests

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            self.calls = [c for c in self.calls if now - c < self.period]

            if len(self.calls) >= self.max_calls:
                sleep_time = self.period - (now - self.calls[0])
                time.sleep(sleep_time)
                self.calls = []

            self.calls.append(time.time())
            return func(*args, **kwargs)
        return wrapper

# Usage
@RateLimiter(max_calls=10, period=60)  # 10 calls per minute
def fetch_data(url):
    return requests.get(url).json()
```

### 5. Cost Optimization Strategies

1. **Combine Free and Paid Sources:** Use free exchange APIs for real-time, paid services for historical bulk
2. **Cache Aggressively:** Store frequently accessed data locally
3. **Incremental Updates:** Only fetch new data, not full history repeatedly
4. **Batch Requests:** Use bulk endpoints when available
5. **Tiered Approach:** Hot data (recent) from expensive source, cold data from cheaper alternatives

### 6. Data Pipeline Architecture

```
┌─────────────────┐
│  Data Sources   │
│ (APIs/WebSockets)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Ingestion │
│  (Rate Limited) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validation &   │
│  Normalization  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Raw Storage    │
│  (S3/Parquet)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Processing &   │
│  Feature Eng.   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Processed DB   │
│  (TimescaleDB)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Backtesting &  │
│  Live Trading   │
└─────────────────┘
```

### 7. Multi-Source Data Aggregation

```python
import pandas as pd
import numpy as np

class MultiSourceAggregator:
    def __init__(self, sources):
        self.sources = sources  # dict of {name: client}

    def fetch_ohlcv(self, symbol, start, end, interval):
        """Fetch from multiple sources and merge"""
        dfs = []

        for name, client in self.sources.items():
            try:
                df = client.get_ohlcv(symbol, start, end, interval)
                df['source'] = name
                dfs.append(df)
            except Exception as e:
                print(f"Error fetching from {name}: {e}")

        if not dfs:
            return None

        # Combine all sources
        combined = pd.concat(dfs, ignore_index=True)

        # For each timestamp, take median price across sources
        result = combined.groupby('timestamp').agg({
            'open': 'median',
            'high': 'max',
            'low': 'min',
            'close': 'median',
            'volume': 'sum'
        }).reset_index()

        return result

    def detect_anomalies(self, symbol, timestamp):
        """Compare prices across sources to detect anomalies"""
        prices = {}
        for name, client in self.sources.items():
            try:
                price = client.get_price(symbol, timestamp)
                prices[name] = price
            except:
                continue

        if len(prices) < 2:
            return None

        median_price = np.median(list(prices.values()))
        std_dev = np.std(list(prices.values()))

        anomalies = {
            name: price
            for name, price in prices.items()
            if abs(price - median_price) > 2 * std_dev
        }

        return anomalies if anomalies else None
```

### 8. Legal and Compliance

- **Terms of Service:** Always review API terms, especially regarding data redistribution
- **Rate Limits:** Respect all rate limits to avoid IP bans
- **Attribution:** Some free APIs require attribution in commercial use
- **Data Rights:** Understand what you can do with the data (personal use vs. redistribution)
- **Privacy:** Handle any user data in compliance with regulations (GDPR, etc.)

---

## Conclusion

This comprehensive guide covers 20+ data sources across exchanges, aggregators, institutional providers, on-chain analytics, and DeFi protocols. For quantitative trading:

**Recommended Starting Stack:**
1. **Exchange APIs** (Binance/Coinbase) - Free, real-time, good quality
2. **CoinGecko** - Free historical data, good for market overview
3. **DeFi Llama** - Free DeFi metrics
4. **Dune Analytics** - Free on-chain queries

**For Serious Quant Trading:**
1. **Tardis.dev** or **CoinAPI** - Institutional-grade tick data
2. **Glassnode** - On-chain analytics
3. **The Graph** - DeFi protocol data
4. **Kaiko** or **Amberdata** - Enterprise-level coverage

Always start with free tiers to validate your strategy before investing in expensive data subscriptions. Combine multiple sources for robust, cross-validated data pipelines.

---

**Last Updated:** November 2025

**Note:** Pricing and features are subject to change. Always verify current offerings on provider websites.
