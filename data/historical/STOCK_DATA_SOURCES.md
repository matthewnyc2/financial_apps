# Comprehensive Historical Stock Market Data Sources for Quantitative Trading

*Last Updated: November 2025*

This document provides a comprehensive overview of stock market data sources suitable for pre-market quantitative trading, including detailed information about data coverage, granularity, access methods, costs, and pre-market/after-hours availability.

---

## Table of Contents

1. [Free & Low-Cost Data Sources](#free--low-cost-data-sources)
2. [Premium Data Providers](#premium-data-providers)
3. [Broker APIs](#broker-apis)
4. [Options & Derivatives Data](#options--derivatives-data)
5. [Tick & High-Frequency Data](#tick--high-frequency-data)
6. [Alternative & Specialized Data](#alternative--specialized-data)
7. [Comparison Matrix](#comparison-matrix)
8. [Code Examples](#code-examples)

---

## Free & Low-Cost Data Sources

### 1. Yahoo Finance (yfinance)

**Provider:** Yahoo Finance
**URL:** https://pypi.org/project/yfinance/

**Data Coverage:**
- Exchanges: Global stock exchanges (US, EU, Asia)
- Instruments: Stocks, ETFs, indices, currencies, cryptocurrencies
- Historical Range: Varies by ticker, typically 10-30+ years
- Geographic Coverage: Worldwide

**Data Granularity:**
- 1 minute (last 7 days only)
- 2, 5, 15, 30, 60 minutes
- Daily, Weekly, Monthly

**Data Fields:**
- OHLCV (Open, High, Low, Close, Volume)
- Adjusted Close (for splits & dividends)
- Dividends
- Stock Splits
- Basic fundamentals

**Access Method:**
- Python library (yfinance)
- No official API
- Web scraping based

**Cost:** FREE

**Pre-Market/After-Hours:**
- ❌ Not available in historical data
- ⚠️ Limited intraday data (last 7 days only)

**Corporate Actions:**
- ✅ Automatic adjustment for splits
- ✅ Dividend data available
- ✅ Adjusted close prices

**Limitations:**
- Unofficial API (web scraping)
- Rate limiting and IP bans possible
- Not suitable for production/commercial use
- Inconsistent data availability

**Code Example:**
```python
import yfinance as yf

# Download historical data
ticker = yf.Ticker("AAPL")

# Get historical prices
hist = ticker.history(start="2020-01-01", end="2025-01-01", interval="1d")

# Get 1-minute data (last 7 days only)
hist_1m = ticker.history(period="7d", interval="1m")

# Get dividends and splits
dividends = ticker.dividends
splits = ticker.splits

# Get fundamental data
info = ticker.info
financials = ticker.financials
balance_sheet = ticker.balance_sheet
```

---

### 2. Alpha Vantage

**Provider:** Alpha Vantage
**URL:** https://www.alphavantage.co/

**Data Coverage:**
- Exchanges: US markets (primary), global markets
- Instruments: Stocks, ETFs, forex, cryptocurrencies
- Historical Range: 20+ years for US equities
- Official NASDAQ data vendor

**Data Granularity:**
- 1, 5, 15, 30, 60 minutes
- Daily, Weekly, Monthly
- Intraday data (last 2 years)

**Data Fields:**
- OHLCV
- Adjusted prices
- Technical indicators (50+ precomputed)
- Fundamental data (income statements, balance sheets, cash flow)
- Real-time quotes
- Economic indicators

**Access Method:**
- REST API (JSON/CSV)
- API key required (free registration)

**Cost:**
- Free Tier: 500 requests/day, 5 requests/minute
- Basic: $29.99/month - 75 requests/minute, 1,200 requests/day
- Premium: $249.99/month - 1,200 requests/minute, 30,000 requests/day
- Enterprise: Custom pricing

**Pre-Market/After-Hours:**
- ❌ Not available in free tier
- ⚠️ Limited extended hours data even in paid tiers

**Corporate Actions:**
- ✅ Adjusted prices for splits and dividends
- ✅ Dividend data available
- ✅ Split data available

**Code Example:**
```python
import requests
import pandas as pd

API_KEY = 'your_api_key'

# Get daily data
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=AAPL&apikey={API_KEY}&outputsize=full'
response = requests.get(url)
data = response.json()

# Get intraday data
url_intraday = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=5min&apikey={API_KEY}'
intraday = requests.get(url_intraday).json()

# Get technical indicators
url_sma = f'https://www.alphavantage.co/query?function=SMA&symbol=AAPL&interval=daily&time_period=20&series_type=close&apikey={API_KEY}'
sma = requests.get(url_sma).json()

# Get fundamental data
url_overview = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol=AAPL&apikey={API_KEY}'
overview = requests.get(url_overview).json()
```

---

### 3. Finnhub

**Provider:** Finnhub
**URL:** https://finnhub.io/

**Data Coverage:**
- Exchanges: 60+ global exchanges
- Instruments: Stocks, ETFs, forex, cryptocurrencies
- Historical Range: 30+ years for major US stocks
- Real-time data for global markets

**Data Granularity:**
- 1, 5, 15, 30, 60 minutes
- Daily (D)
- Weekly (W)
- Monthly (M)
- Real-time streaming

**Data Fields:**
- OHLCV
- Real-time quotes
- Company fundamentals
- Earnings data
- News sentiment
- ESG scores
- Insider transactions
- IPO calendar
- Economic indicators
- Audio earnings call transcripts

**Access Method:**
- REST API (JSON)
- WebSocket for real-time data
- API key required

**Cost:**
- Free Tier: 60 API calls/minute
- Starter: $49.99/month - US market data
- Professional: $199.99/month (annual) - Global coverage, audio transcripts
- Enterprise: Custom pricing

**Pre-Market/After-Hours:**
- ⚠️ Limited availability
- Available in Professional tier and above

**Corporate Actions:**
- ✅ Stock splits tracked
- ✅ Dividend data
- ✅ Merger & acquisition data

**Code Example:**
```python
import finnhub
import pandas as pd

# Setup client
finnhub_client = finnhub.Client(api_key="your_api_key")

# Stock candles (historical data)
res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
df = pd.DataFrame(res)

# Real-time quote
quote = finnhub_client.quote('AAPL')

# Company profile
profile = finnhub_client.company_profile2(symbol='AAPL')

# Earnings calendar
earnings = finnhub_client.earnings_calendar(
    _from="2024-01-01",
    to="2024-12-31",
    symbol="AAPL"
)

# News sentiment
sentiment = finnhub_client.news_sentiment('AAPL')
```

---

### 4. Twelve Data

**Provider:** Twelve Data
**URL:** https://twelvedata.com/

**Data Coverage:**
- Exchanges: 100+ global exchanges
- Instruments: 100,000+ stocks, ETFs, indices, forex, crypto
- Historical Range: 20+ years
- Global coverage

**Data Granularity:**
- 1, 5, 15, 30, 45 minutes
- 1, 2, 4 hours
- Daily, Weekly, Monthly
- Real-time streaming

**Data Fields:**
- OHLCV
- Adjusted prices
- 100+ technical indicators (precomputed)
- Fundamental data
- Real-time quotes
- ETF holdings
- Mutual fund data

**Access Method:**
- REST API (JSON/CSV)
- WebSocket for real-time
- API key required

**Cost:**
- Free: 800 calls/day, 8 calls/minute
- Basic: $29/month - 8,000 calls/day, 80 calls/minute
- Pro: $79/month - 30,000 calls/day, 300 calls/minute
- Ultra: $329/month - 120,000 calls/day, 1,200 calls/minute

**Pre-Market/After-Hours:**
- ✅ Available in Pro tier and above
- Extended hours data included

**Corporate Actions:**
- ✅ Automatic split adjustments
- ✅ Dividend data
- ✅ Adjusted close prices

**Notable Features:**
- 99.95% uptime SLA
- AI-powered analytics
- Customizable technical indicators
- Bulk data download

**Code Example:**
```python
import requests
import pandas as pd

API_KEY = 'your_api_key'

# Time series data
url = f'https://api.twelvedata.com/time_series?symbol=AAPL&interval=1min&apikey={API_KEY}&outputsize=5000'
response = requests.get(url)
data = response.json()

# Technical indicators
url_sma = f'https://api.twelvedata.com/sma?symbol=AAPL&interval=1day&time_period=20&apikey={API_KEY}'
sma = requests.get(url_sma).json()

# Real-time price
url_price = f'https://api.twelvedata.com/price?symbol=AAPL&apikey={API_KEY}'
price = requests.get(url_price).json()

# Quote (OHLCV + more)
url_quote = f'https://api.twelvedata.com/quote?symbol=AAPL&apikey={API_KEY}'
quote = requests.get(url_quote).json()
```

---

### 5. Marketstack

**Provider:** Marketstack (by APILayer)
**URL:** https://marketstack.com/

**Data Coverage:**
- Exchanges: 70+ global exchanges
- Instruments: 170,000+ stocks and ETFs
- Historical Range: 30+ years
- Real-time and intraday data

**Data Granularity:**
- 1, 5, 10, 15, 30, 60 minutes (paid plans)
- Daily (EOD)
- Tick-level data available

**Data Fields:**
- OHLCV
- Adjusted prices
- Splits and dividends
- Intraday data
- Real-time quotes (paid)
- Stock indices

**Access Method:**
- REST API (JSON)
- API key required
- Updated every minute

**Cost:**
- Free: 100 requests/month
- Basic: $9.99/month - 10,000 requests/month
- Professional: $49.99/month - 100,000 requests/month, real-time
- Business: $149.99/month - 500,000 requests/month

**Pre-Market/After-Hours:**
- ⚠️ Limited availability
- Available in Business tier

**Corporate Actions:**
- ✅ Split adjustments
- ✅ Dividend data
- ✅ Currency conversion

**Code Example:**
```python
import requests

API_KEY = 'your_access_key'

# EOD data
url = f'http://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols=AAPL'
response = requests.get(url)
data = response.json()

# Intraday data (requires paid plan)
url_intraday = f'http://api.marketstack.com/v1/intraday?access_key={API_KEY}&symbols=AAPL&interval=1min'
intraday = requests.get(url_intraday).json()

# Historical data with date range
url_hist = f'http://api.marketstack.com/v1/eod?access_key={API_KEY}&symbols=AAPL&date_from=2020-01-01&date_to=2025-01-01'
hist = requests.get(url_hist).json()
```

---

## Premium Data Providers

### 6. Polygon.io

**Provider:** Polygon.io
**URL:** https://polygon.io/

**Data Coverage:**
- Exchanges: All US exchanges (NYSE, NASDAQ, CBOE, etc.)
- Instruments: Stocks, options, indices, forex, cryptocurrencies
- Historical Range: 15+ years for stocks, options data from 2010
- Tick-level data available

**Data Granularity:**
- Tick-by-tick (every trade and quote)
- 1, 5, 15, 30 minutes
- Hourly, Daily, Weekly, Monthly
- Real-time streaming via WebSocket

**Data Fields:**
- OHLCV
- Bid/Ask spreads
- Options Greeks
- Company fundamentals
- Earnings, dividends, splits
- News and sentiment
- Market-wide aggregates

**Access Method:**
- REST API (JSON/CSV)
- WebSocket streaming
- Flat files (bulk download)
- API key required

**Cost:**
- Free: 5 API calls/minute (delayed data)
- Starter: $29/month - 100 calls/minute, delayed quotes
- Developer: $99/month - Unlimited calls, delayed data
- Advanced: $199/month - Real-time stock data
- Professional: $399/month - Real-time stocks + options
- Enterprise: Custom pricing - Full tick data

**Pre-Market/After-Hours:**
- ✅ Available in Advanced tier and above
- Full extended hours coverage (4am-8pm ET)

**Corporate Actions:**
- ✅ Comprehensive split tracking
- ✅ Dividend calendar
- ✅ Adjusted prices
- ✅ Factor files for adjustments

**Notable Features:**
- Unlimited API calls on paid plans
- Direct SIP feed access
- Sub-millisecond timestamps
- 10-year historical options data

**Code Example:**
```python
from polygon import RESTClient
import pandas as pd

API_KEY = 'your_api_key'
client = RESTClient(API_KEY)

# Get aggregates (bars)
aggs = client.get_aggs(
    ticker="AAPL",
    multiplier=1,
    timespan="minute",
    from_="2024-01-01",
    to="2024-12-31",
    limit=50000
)

# Get trades (tick data)
trades = client.list_trades(
    ticker="AAPL",
    timestamp_gte="2024-01-01",
    limit=50000
)

# Get quotes
quotes = client.list_quotes(
    ticker="AAPL",
    timestamp_gte="2024-01-01",
    limit=50000
)

# Get daily open/close
daily_oc = client.get_daily_open_close_agg("AAPL", "2024-01-09")

# Get previous close
prev_close = client.get_previous_close_agg("AAPL")

# Get splits
splits = client.list_splits(ticker="AAPL")

# Get dividends
dividends = client.list_dividends(ticker="AAPL")
```

---

### 7. EODHD (EOD Historical Data)

**Provider:** EOD Historical Data
**URL:** https://eodhd.com/

**Data Coverage:**
- Exchanges: 150+ global exchanges
- Instruments: 150,000+ tickers (stocks, ETFs, indices)
- Historical Range: 30+ years for major markets
- Forex: 1,100+ pairs
- Cryptocurrencies: 1,000+ coins

**Data Granularity:**
- 1, 5, 15, 30 minutes (intraday)
- Hourly
- Daily (EOD)
- Bulk downloads available

**Data Fields:**
- OHLCV
- Adjusted prices
- Splits and dividends
- Fundamental data (detailed financials)
- Company profiles
- ETF holdings
- Macroeconomic data
- Financial news
- Sentiment analysis

**Access Method:**
- REST API (JSON/CSV)
- Bulk CSV downloads
- API key required
- WebSocket for real-time (premium)

**Cost:**
- All World: €19.99/month (~$21) - All EOD data, no fundamental
- All-World Extended: €49.99/month (~$53) - EOD + intraday
- All World Extended+: €79.99/month (~$85) - Add fundamental data
- Enterprise: Custom pricing

**Pre-Market/After-Hours:**
- ⚠️ Limited availability
- Intraday data includes some extended hours

**Corporate Actions:**
- ✅ Comprehensive splits/dividends API
- ✅ Adjusted and unadjusted prices
- ✅ Historical corporate actions database

**Notable Features:**
- Very cost-effective for bulk historical data
- Excellent fundamental data coverage
- Bulk download options reduce API calls
- Good for backtesting with large datasets

**Code Example:**
```python
import requests
import pandas as pd

API_TOKEN = 'your_api_token'

# Get EOD data
url = f'https://eodhd.com/api/eod/AAPL.US?api_token={API_TOKEN}&fmt=json'
eod = requests.get(url).json()

# Get intraday data
url_intraday = f'https://eodhd.com/api/intraday/AAPL.US?api_token={API_TOKEN}&interval=5m&fmt=json'
intraday = requests.get(url_intraday).json()

# Get fundamentals
url_fundamentals = f'https://eodhd.com/api/fundamentals/AAPL.US?api_token={API_TOKEN}'
fundamentals = requests.get(url_fundamentals).json()

# Get splits and dividends
url_div = f'https://eodhd.com/api/div/AAPL.US?api_token={API_TOKEN}&fmt=json'
dividends = requests.get(url_div).json()

# Bulk download (CSV)
url_bulk = f'https://eodhd.com/api/eod-bulk-last-day/US?api_token={API_TOKEN}&fmt=csv'
bulk_data = pd.read_csv(url_bulk)
```

---

### 8. Databento

**Provider:** Databento
**URL:** https://databento.com/

**Data Coverage:**
- Exchanges: US equities, futures, options
- Instruments: All US-listed stocks, ETFs, options, futures
- Historical Range: Varies by dataset, extensive tick history
- Direct exchange feeds

**Data Granularity:**
- Tick-by-tick (every trade, quote, order book update)
- Aggregated bars (1s, 1m, 1h, 1d)
- Market depth (full order book)
- OHLCV

**Data Fields:**
- Tick data (trades, quotes)
- Order book depth
- Market microstructure signals
- OHLCV aggregates
- Imbalances
- Statistics

**Access Method:**
- Python SDK
- REST API
- Historical data download
- Real-time streaming

**Cost:**
- $125 in free credits (sign-up bonus)
- Pay-as-you-go pricing
- Real-time: $300-$2,500/month depending on data type
- Historical: Varies by dataset and date range
- Volume discounts available

**Pre-Market/After-Hours:**
- ✅ Full extended hours coverage
- Tick data includes all trading sessions

**Corporate Actions:**
- ✅ Split adjustments available
- ⚠️ Does NOT provide pre-calculated IV or Greeks for options
- Factor files available

**Notable Features:**
- Institutional-grade data quality
- Sub-microsecond timestamps
- Direct SIP/exchange feeds
- Standardized data formats
- No API rate limits

**Code Example:**
```python
import databento as db

# Initialize client
client = db.Historical('YOUR_API_KEY')

# Get historical tick data
data = client.timeseries.get_range(
    dataset='GLBX.MDP3',
    symbols=['AAPL'],
    start='2024-01-01',
    end='2024-01-31',
    schema='trades'
)

# Get OHLCV bars
bars = client.timeseries.get_range(
    dataset='XNAS.ITCH',
    symbols=['AAPL'],
    start='2024-01-01',
    schema='ohlcv-1m'
)

# Get order book snapshots
books = client.timeseries.get_range(
    dataset='XNAS.ITCH',
    symbols=['AAPL'],
    start='2024-01-01T09:30:00',
    end='2024-01-01T16:00:00',
    schema='mbp-10'  # Market by price, 10 levels
)

# Save to file
data.to_csv('aapl_trades.csv')
```

---

### 9. Tiingo

**Provider:** Tiingo
**URL:** https://www.tiingo.com/

**Data Coverage:**
- Exchanges: US markets (primary), global markets
- Instruments: Stocks, ETFs, mutual funds, cryptocurrencies
- Historical Range: 30+ years for US equities
- News coverage: Real-time financial news

**Data Granularity:**
- Tick data (real-time)
- 1, 5, 15, 30 minutes, hourly
- Daily
- Real-time streaming

**Data Fields:**
- OHLCV
- Adjusted prices (splits & dividends)
- Fundamental data
- Real-time quotes
- News articles with sentiment
- Cryptocurrency data

**Access Method:**
- REST API (JSON/CSV)
- WebSocket for real-time
- Python client library
- R package
- Excel add-in

**Cost:**
- Free: Limited to 1,000 unique symbols/month, 500 requests/hour
- Starter: $10/month - 20,000 requests/month
- Power: $30/month - 50,000 requests/month
- Commercial: $500/month - Unlimited requests

**Pre-Market/After-Hours:**
- ⚠️ Limited in free tier
- ✅ Available in paid tiers

**Corporate Actions:**
- ✅ Splits and dividends tracked
- ✅ Adjusted and unadjusted prices
- ✅ Historical adjustments

**Notable Features:**
- High data quality and reliability
- Good for retail and institutional
- Excellent documentation
- Multiple client libraries

**Code Example:**
```python
from tiingo import TiingoClient
import pandas as pd

config = {'api_key': 'YOUR_API_KEY'}
client = TiingoClient(config)

# Get historical prices
historical_prices = client.get_dataframe(
    'AAPL',
    startDate='2020-01-01',
    endDate='2025-01-01',
    frequency='daily'
)

# Get intraday data
intraday = client.get_dataframe(
    'AAPL',
    frequency='1min',
    startDate='2024-01-01',
    endDate='2024-01-02'
)

# Get latest price
ticker_price = client.get_ticker_price('AAPL')

# Get ticker metadata
ticker_metadata = client.get_ticker_metadata('AAPL')

# Get news
news = client.get_news(
    tickers=['AAPL'],
    startDate='2024-01-01',
    endDate='2024-12-31'
)
```

---

### 10. Intrinio

**Provider:** Intrinio
**URL:** https://intrinio.com/

**Data Coverage:**
- Exchanges: Global coverage (North America, Europe, Asia)
- Instruments: Stocks, ETFs, mutual funds, indices, options, forex
- Historical Range: 30+ years
- Over 300 data feeds available

**Data Granularity:**
- Real-time tick data
- 1, 5, 15, 30, 60 minutes
- Daily, Weekly, Monthly

**Data Fields:**
- OHLCV
- Real-time quotes
- Extensive fundamental data
- Options data with Greeks
- Institutional ownership
- SEC filings
- Insider transactions
- ETF holdings
- Economic data

**Access Method:**
- REST API (JSON/CSV)
- WebSocket streaming
- SDKs for Python, JavaScript, R, Excel
- Dedicated support

**Cost:**
- No free tier (trials available)
- Pricing based on data feeds needed
- US Fundamentals: Starting at $75/month
- Real-time prices: Starting at $100/month
- Options data: $300+/month
- Custom enterprise pricing

**Pre-Market/After-Hours:**
- ✅ Available with real-time feeds
- Extended hours data included

**Corporate Actions:**
- ✅ Comprehensive corporate actions tracking
- ✅ Standardized data across securities
- ✅ Historical adjustments

**Notable Features:**
- Pay only for data you need
- Excellent developer support
- High data standardization
- Good for both small teams and enterprises

**Code Example:**
```python
import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException

intrinio.ApiClient().configuration.api_key['api_key'] = 'YOUR_API_KEY'
security_api = intrinio.SecurityApi()

# Get historical data
historical = security_api.get_security_stock_prices(
    identifier='AAPL',
    start_date='2020-01-01',
    end_date='2025-01-01',
    frequency='daily'
)

# Get intraday prices
intraday = security_api.get_security_intraday_prices(
    identifier='AAPL',
    source='iex',
    start_date='2024-01-01T09:30:00.000Z',
    end_date='2024-01-01T16:00:00.000Z'
)

# Get real-time quote
quote = security_api.get_security_realtime_price(identifier='AAPL')

# Get fundamentals
fundamentals = intrinio.FundamentalsApi().get_fundamental_standardized_financials(
    id='AAPL-income_statement-2024-Q1'
)
```

---

### 11. Xignite

**Provider:** Xignite (a Markit on Demand company)
**URL:** https://www.xignite.com/

**Data Coverage:**
- Exchanges: Global coverage (200+ sources)
- Instruments: Equities, options, forex, fixed income, commodities, funds
- Historical Range: Extensive historical archives
- 12 billion API requests served daily

**Data Granularity:**
- Real-time tick data
- Minute-by-minute
- Intraday intervals
- Daily, historical

**Data Fields:**
- OHLCV
- Real-time quotes
- Corporate actions (splits, dividends, M&A, name changes)
- Fundamental data
- Options chains with Greeks
- Fixed income data
- Global market data

**Access Method:**
- REST API (SOAP and REST)
- JSON, XML, CSV formats
- Cloud-based infrastructure
- High-availability SLA

**Cost:**
- Enterprise-focused pricing
- No public pricing (contact sales)
- Typically $1,000+/month
- Custom packages based on needs

**Pre-Market/After-Hours:**
- ✅ Full extended hours coverage
- Dedicated pre-market/after-hours API endpoints

**Corporate Actions:**
- ✅ Industry-leading corporate actions database
- ✅ Real-time corporate action updates
- ✅ Historical corporate action adjustments
- ✅ Detailed M&A tracking

**Notable Features:**
- Enterprise-grade reliability and security
- Partnerships with 250+ data providers (FactSet, Morningstar)
- Scalable infrastructure
- Excellent for large organizations
- Compliance and security features

**Code Example:**
```python
import requests

# Xignite uses different product APIs
# Example with Global Quotes API

api_token = 'YOUR_TOKEN'

# Get real-time quote
url = f'https://globalquotes.xignite.com/v3/xGlobalQuotes.json/GetGlobalQuote?IdentifierType=Symbol&Identifier=AAPL&_token={api_token}'
quote = requests.get(url).json()

# Get historical quotes
url_hist = f'https://globalhistorical.xignite.com/v3/xGlobalHistorical.json/GetGlobalHistoricalQuotes?IdentifierType=Symbol&Identifier=AAPL&StartDate=1/1/2020&EndDate=12/31/2024&_token={api_token}'
historical = requests.get(url_hist).json()

# Get extended hours quotes
url_extended = f'https://globalquotes.xignite.com/v3/xGlobalQuotes.json/GetExtendedQuote?IdentifierType=Symbol&Identifier=AAPL&_token={api_token}'
extended = requests.get(url_extended).json()

# Get corporate actions
url_actions = f'https://globalmaster.xignite.com/v3/xGlobalMaster.json/GetCorporateActions?IdentifierType=Symbol&Identifier=AAPL&_token={api_token}'
actions = requests.get(url_actions).json()
```

---

## Broker APIs

### 12. Interactive Brokers (IBKR)

**Provider:** Interactive Brokers
**URL:** https://www.interactivebrokers.com/
**API Docs:** https://interactivebrokers.github.io/tws-api/

**Data Coverage:**
- Exchanges: 150+ markets in 33 countries
- Instruments: Stocks, options, futures, forex, bonds, CFDs
- Historical Range: Varies by instrument (typically 10+ years)
- Global coverage

**Data Granularity:**
- Tick-by-tick
- 1, 5, 10, 15, 30 seconds
- 1, 2, 3, 5, 10, 15, 20, 30 minutes
- 1, 2, 3, 4, 8 hours
- Daily, Weekly, Monthly

**Data Fields:**
- OHLCV
- Bid/Ask
- Trades
- Order book (Level 2)
- Historical volatility
- Options Greeks
- Fundamental data

**Access Method:**
- TWS API (Python, Java, C++, C#)
- Client Portal API (REST)
- FIX protocol
- Requires active account

**Cost:**
- FREE for account holders
- Market data subscriptions required:
  - US Securities Snapshot: $10/month
  - US Equity and Options Add-On Streaming Bundle: $4.50/month
  - Level 2 data: Additional fees
- Waived with minimum account activity

**Pre-Market/After-Hours:**
- ✅ Full extended hours coverage
- Pre-market: 4:00 AM - 9:30 AM ET
- After-hours: 4:00 PM - 8:00 PM PT

**Corporate Actions:**
- ✅ Automatic adjustment for splits
- ✅ Dividend tracking
- ✅ Corporate action notifications

**Notable Features:**
- Professional-grade execution
- Global market access
- Low latency
- Direct market access (DMA)

**Code Example:**
```python
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time

class IBapi(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = []

    def historicalData(self, reqId, bar):
        self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume])

def run_loop():
    app.run()

# Initialize app
app = IBapi()
app.connect('127.0.0.1', 7497, 123)  # 7497 for TWS, 4001 for IB Gateway

# Start the socket in a thread
api_thread = threading.Thread(target=run_loop, daemon=True)
api_thread.start()

time.sleep(1)  # Sleep interval to allow connection to establish

# Create contract object
contract = Contract()
contract.symbol = 'AAPL'
contract.secType = 'STK'
contract.exchange = 'SMART'
contract.currency = 'USD'

# Request historical data
app.reqHistoricalData(
    reqId=1,
    contract=contract,
    endDateTime='',
    durationStr='1 M',
    barSizeSetting='1 min',
    whatToShow='TRADES',
    useRTH=0,  # 0 = Include extended hours, 1 = Regular trading hours only
    formatDate=1,
    keepUpToDate=False,
    chartOptions=[]
)

time.sleep(5)  # Wait for data
print(app.data)
```

---

### 13. TD Ameritrade (Now Charles Schwab)

**Provider:** TD Ameritrade / Charles Schwab
**URL:** https://developer.tdameritrade.com/
**Note:** API being transitioned to Schwab platform

**Data Coverage:**
- Exchanges: US markets
- Instruments: Stocks, ETFs, options, mutual funds
- Historical Range: Back to ~2000 for major equities
- US-focused

**Data Granularity:**
- 1, 5, 10, 15, 30 minutes
- Daily, Weekly, Monthly
- Real-time streaming

**Data Fields:**
- OHLCV
- Options chains
- Real-time quotes
- Market movers
- Fundamental data
- Account information (for account holders)

**Access Method:**
- REST API
- WebSocket streaming
- OAuth 2.0 authentication
- Free for all (no account required for market data)

**Cost:**
- FREE (no account needed for market data API)
- Account required for trading

**Pre-Market/After-Hours:**
- ✅ Extended hours quotes available
- Historical extended hours data limited

**Corporate Actions:**
- ✅ Adjusted prices
- ✅ Dividend calendar
- ✅ Splits tracked

**Notable Features:**
- Free API access
- Good documentation
- Python wrapper (tda-api) available
- Being migrated to Schwab platform

**Code Example:**
```python
from tda import auth, client
import json

# One-time authentication
try:
    c = auth.client_from_token_file('token.json', api_key)
except FileNotFoundError:
    from selenium import webdriver
    with webdriver.Chrome() as driver:
        c = auth.client_from_login_flow(
            driver, api_key, redirect_uri, 'token.json'
        )

# Get price history
response = c.get_price_history(
    'AAPL',
    period_type=client.Client.PriceHistory.PeriodType.MONTH,
    period=6,
    frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
    frequency=1
)
history = response.json()

# Get real-time quote
quote_response = c.get_quote('AAPL')
quote = quote_response.json()

# Get option chain
options = c.get_option_chain(
    'AAPL',
    contract_type=client.Client.Options.ContractType.ALL,
    strike_count=10
).json()

# Get movers
movers = c.get_movers(
    '$DJI',
    direction=client.Client.Movers.Direction.UP,
    change=client.Client.Movers.Change.PERCENT
).json()
```

---

### 14. Alpaca

**Provider:** Alpaca Markets
**URL:** https://alpaca.markets/

**Data Coverage:**
- Exchanges: US stock exchanges
- Instruments: Stocks, ETFs, cryptocurrencies
- Historical Range: 7+ years for US equities
- Crypto: Real-time and historical

**Data Granularity:**
- Tick-by-tick (trades and quotes)
- 1, 5, 15, 30 minutes
- 1, 2, 4, 8, 12 hours
- Daily, Weekly, Monthly
- Real-time streaming

**Data Fields:**
- OHLCV
- Trades (tick)
- Quotes (tick)
- Bars (aggregated)
- Order book snapshots
- Latest quotes

**Access Method:**
- REST API (v2)
- WebSocket streaming
- Python SDK (alpaca-py)
- API key authentication
- Commission-free trading

**Cost:**
- Free: Live trading account (paper or funded)
- Market Data:
  - IEX (Free): Real-time, limited
  - SIP (Paid): $9-99/month - Full market data, all exchanges
- No minimum balance for API access

**Pre-Market/After-Hours:**
- ✅ Full extended hours support
- Trades and bars include pre/post market automatically
- Extended hours: 4:00 AM - 8:00 PM ET

**Corporate Actions:**
- ✅ Split adjustments
- ✅ Dividend data
- ✅ Adjusted prices

**Notable Features:**
- Commission-free trading
- Modern REST API
- Excellent documentation
- Good for algorithmic trading
- Paper trading environment
- Up to 10,000 API calls/minute

**Code Example:**
```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockTradesRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime

# Initialize client (no account needed for data)
client = StockHistoricalDataClient(api_key='YOUR_KEY', secret_key='YOUR_SECRET')

# Get bars (includes extended hours by default)
request_params = StockBarsRequest(
    symbol_or_symbols=['AAPL'],
    timeframe=TimeFrame.Minute,
    start=datetime(2024, 1, 1),
    end=datetime(2024, 1, 31)
)
bars = client.get_stock_bars(request_params)

# Get trades (tick data)
trades_request = StockTradesRequest(
    symbol_or_symbols=['AAPL'],
    start=datetime(2024, 1, 1, 9, 30),
    end=datetime(2024, 1, 1, 16, 0)
)
trades = client.get_stock_trades(trades_request)

# Get quotes
from alpaca.data.requests import StockQuotesRequest
quotes_request = StockQuotesRequest(
    symbol_or_symbols=['AAPL'],
    start=datetime(2024, 1, 1, 9, 30)
)
quotes = client.get_stock_quotes(quotes_request)

# Real-time streaming
from alpaca.data.live import StockDataStream

wss_client = StockDataStream('YOUR_KEY', 'YOUR_SECRET')

async def quote_data_handler(data):
    print(data)

wss_client.subscribe_quotes(quote_data_handler, 'AAPL')
wss_client.run()
```

---

### 15. Tradier

**Provider:** Tradier
**URL:** https://tradier.com/ / https://documentation.tradier.com/

**Data Coverage:**
- Exchanges: US markets
- Instruments: Stocks, options, ETFs
- Historical Range: Varies (limited compared to others)
- Options data excellent

**Data Granularity:**
- Tick data (time & sales)
- 1, 5, 15 minutes
- Daily
- Real-time streaming

**Data Fields:**
- OHLCV
- Real-time quotes
- Options chains with Greeks
- Time & sales
- Market calendar
- Corporate actions

**Access Method:**
- REST API
- WebSocket streaming
- OAuth authentication
- Requires brokerage account

**Cost:**
- FREE with Tradier brokerage account
- Subscription accounts: Free data
- Fees for inactive accounts:
  - <$2,000 balance + <2 trades/year: $50 inactivity fee
  - <2 trades/month (international): $20/month maintenance

**Pre-Market/After-Hours:**
- ✅ Real-time extended hours quotes
- Limited historical extended hours data

**Corporate Actions:**
- ✅ Corporate actions API
- ✅ Dividend data
- ✅ Split tracking

**Notable Features:**
- Excellent options data
- Real-time Greeks
- Free for active traders
- Good API documentation

**Code Example:**
```python
import requests

API_KEY = 'your_access_token'
headers = {'Authorization': f'Bearer {API_KEY}', 'Accept': 'application/json'}

# Get historical data
url = 'https://api.tradier.com/v1/markets/history'
params = {
    'symbol': 'AAPL',
    'interval': 'daily',
    'start': '2020-01-01',
    'end': '2025-01-01'
}
history = requests.get(url, params=params, headers=headers).json()

# Get real-time quote
url_quote = 'https://api.tradier.com/v1/markets/quotes'
quote = requests.get(url_quote, params={'symbols': 'AAPL'}, headers=headers).json()

# Get options chain
url_chain = 'https://api.tradier.com/v1/markets/options/chains'
chain = requests.get(url_chain, params={'symbol': 'AAPL', 'expiration': '2024-12-20'}, headers=headers).json()

# Get Greeks
url_greeks = 'https://api.tradier.com/v1/markets/options/strikes'
greeks = requests.get(url_greeks, params={'symbol': 'AAPL', 'expiration': '2024-12-20'}, headers=headers).json()

# Get time & sales
url_timesales = 'https://api.tradier.com/v1/markets/timesales'
timesales = requests.get(url_timesales, params={'symbol': 'AAPL', 'interval': 'tick'}, headers=headers).json()

# Get corporate actions
url_corp = 'https://api.tradier.com/v1/markets/fundamentals/corporate_actions'
corp_actions = requests.get(url_corp, params={'symbols': 'AAPL'}, headers=headers).json()
```

---

## Options & Derivatives Data

### 16. Market Data App

**Provider:** Market Data
**URL:** https://www.marketdata.app/

**Data Coverage:**
- Exchanges: US markets
- Instruments: Stocks, options, indices
- Historical Range: Options data back to 2010
- US equity options focus

**Data Granularity:**
- Real-time
- 1, 5, 15, 30 minutes
- Hourly, Daily
- End-of-day

**Data Fields:**
- OHLCV
- Options chains
- Real-time Greeks (Delta, Gamma, Vega, Theta, Rho)
- Implied Volatility
- Options quotes
- Stock quotes

**Access Method:**
- REST API
- WebSocket
- Google Sheets Add-On
- Excel integration

**Cost:**
- Starter: $24.99/month - 100,000 API calls
- Trader: $49.99/month - 500,000 API calls
- Investor: $99.99/month - 2,000,000 API calls
- Enterprise: Custom pricing

**Pre-Market/After-Hours:**
- ✅ Extended hours data available

**Corporate Actions:**
- ✅ Adjusted prices
- ✅ Split tracking

**Notable Features:**
- Real-time Greeks calculation
- Historical options data
- Google Sheets integration
- Clean, simple API

**Code Example:**
```python
import requests

# Get stock quote
url = 'https://api.marketdata.app/v1/stocks/quotes/AAPL/'
headers = {'Authorization': 'Bearer YOUR_TOKEN'}
quote = requests.get(url, headers=headers).json()

# Get options chain
url_chain = 'https://api.marketdata.app/v1/options/chain/AAPL/'
chain = requests.get(url_chain, headers=headers).json()

# Get options quotes with Greeks
url_option = 'https://api.marketdata.app/v1/options/quotes/AAPL250117C00150000/'
option_quote = requests.get(url_option, headers=headers).json()
# Returns: delta, gamma, theta, vega, rho, iv

# Get historical options prices
url_hist = 'https://api.marketdata.app/v1/options/quotes/AAPL250117C00150000/history/'
params = {'from': '2024-01-01', 'to': '2024-12-31'}
hist_options = requests.get(url_hist, params=params, headers=headers).json()
```

---

### 17. CBOE DataShop

**Provider:** Chicago Board Options Exchange
**URL:** https://datashop.cboe.com/

**Data Coverage:**
- Exchanges: CBOE exchanges
- Instruments: US stock options, index options, ETF options
- Historical Range: Extensive archives
- Official exchange data

**Data Granularity:**
- 1-minute intervals
- Custom intervals
- Tick-by-tick available
- Daily summaries

**Data Fields:**
- NBBO (National Best Bid/Offer) with size
- OHLC prices
- Trade volumes
- Open interest
- Implied Volatility (optional)
- Greeks (Delta, Gamma, Vega, Theta, Rho) (optional)
- Options on stocks, ETFs, indices

**Access Method:**
- Trade Optimizer API
- Bulk file download
- Custom data feeds
- FTP delivery

**Cost:**
- Custom pricing (contact sales)
- Trade Optimizer API subscription
- Additional fees for IV and Greeks
- Free historical volume data available

**Pre-Market/After-Hours:**
- ✅ Full trading session data
- Pre-market and after-hours options trading

**Corporate Actions:**
- ✅ Comprehensive adjustment tracking
- Official exchange adjustments

**Notable Features:**
- Official exchange data (highest quality)
- Full options market depth
- Greeks and IV available
- Custom data packages

---

### 18. First Rate Data (Options)

**Provider:** First Rate Data
**URL:** https://firstratedata.com/options-data

**Data Coverage:**
- Instruments: US-listed equity, ETF, and index options
- Historical Range: January 2010 - present
- Full historical option chains
- 15+ years of data

**Data Granularity:**
- End-of-day (EOD)
- Full option chain snapshots

**Data Fields:**
- Bid/Offer quotes
- Bid/Offer volumes
- Implied Volatility (bid and ask)
- Close of day Open Interest
- Greeks (Delta, Gamma, Vega, Theta, Rho)
- Last trade price
- Underlying stock price

**Access Method:**
- Bulk download (CSV/ZIP)
- API access for bundle subscribers
- One-time purchase or subscription

**Cost:**
- Single ticker: ~$299 one-time + $99/year updates
- Bundles: $59-99/month subscription
- Total archive: Contact for pricing

**Pre-Market/After-Hours:**
- ❌ EOD data only

**Corporate Actions:**
- ✅ Adjusted for splits
- Historical chain accuracy maintained

**Notable Features:**
- Comprehensive historical options archive
- Greeks pre-calculated
- Both IV and Greeks for bid/ask
- Good for backtesting options strategies
- Can convert to TradeStation, MetaStock formats

---

## Tick & High-Frequency Data

### 19. IQFeed (DTN)

**Provider:** DTN IQFeed
**URL:** https://www.iqfeed.net/

**Data Coverage:**
- Exchanges: US and Canadian markets, futures, forex
- Instruments: Stocks, options, futures, indices, forex
- Historical Range: 180 days of tick history (includes extended hours)
- International markets available

**Data Granularity:**
- Tick-by-tick (microsecond timestamps if available)
- 1, 5, 10, 15, 30, 60 seconds
- Minute bars, daily, weekly, monthly
- Real-time streaming

**Data Fields:**
- Every trade tick
- Every quote tick
- OHLCV bars
- Bid/Ask
- Market depth (Level 2)
- Time & sales

**Access Method:**
- Socket-based API
- Direct feed connection
- Low-latency
- Various client libraries

**Cost:**
- Core Service: $45/month
- Market Depth (Level 2): +$23/month
- Real-time Futures: +$23/month
- International Markets: +$35/month
- Options: +$58/month
- Total can range: $45-$200+/month depending on needs

**Pre-Market/After-Hours:**
- ✅ Full extended hours coverage
- 180 days of tick history includes pre/post market
- Microsecond timestamps

**Corporate Actions:**
- ✅ Split and dividend adjustments
- Real-time corporate action feeds

**Notable Features:**
- Professional-grade tick data
- Very low latency
- 180-day tick history buffer
- Every trade and quote captured
- Popular for HFT and algo trading
- Used by many trading platforms

---

### 20. eSignal

**Provider:** eSignal (Interactive Data)
**URL:** https://www.esignal.com/

**Data Coverage:**
- Exchanges: Global markets
- Instruments: Stocks, futures, forex, options
- Historical Range: Extensive archives
- Real-time global coverage

**Data Granularity:**
- Tick-by-tick
- Second, minute intervals
- Daily, weekly, monthly
- Real-time streaming

**Data Fields:**
- OHLCV
- Tick data
- Level 2 (market depth)
- Time & sales
- Market scanner data

**Access Method:**
- Desktop application
- API access
- Direct data feed

**Cost:**
- Classic: $52/month (15-min delayed quotes)
- Signature: $204/month (real-time)
- Elite: $416/month (advanced features)
- Plus exchange fees (~$10/month per exchange)

**Pre-Market/After-Hours:**
- ✅ Extended hours data available
- Pre-market and after-hours tracking

**Corporate Actions:**
- ✅ Automatic adjustments
- Corporate action tracking

**Notable Features:**
- Professional trading platform
- Advanced charting
- Real-time scanning
- Global market coverage
- Used by professional traders

---

## Alternative & Specialized Data

### 21. QuantConnect

**Provider:** QuantConnect
**URL:** https://www.quantconnect.com/

**Data Coverage:**
- Exchanges: US, International
- Instruments: Equities, options, futures, forex, crypto, CFDs
- Historical Range: 1998-present for US equities
- Tick resolution data

**Data Granularity:**
- Tick-by-tick
- Second, minute, hour, daily

**Data Fields:**
- OHLCV
- Tick data (trades/quotes)
- Fundamental data
- Alternative data
- Options data
- Corporate actions

**Access Method:**
- Cloud-based backtesting platform
- LEAN engine (open-source)
- API for live trading
- Data available through platform

**Cost:**
- Free: Limited backtesting
- Quant Researcher: $8/month
- Team: $20/month/seat
- Trading: $50/month/node (live trading)
- Data costs additional for some datasets

**Pre-Market/After-Hours:**
- ✅ Available in tick data
- Raw data normalization includes extended hours

**Corporate Actions:**
- ✅ Sophisticated corporate actions handling
- ✅ Factor files for adjustments
- ✅ Split handling with automatic portfolio adjustments
- ✅ Dividend tracking

**Notable Features:**
- Integrated backtesting platform
- Open-source algorithm framework (LEAN)
- Institutional-grade data
- Live trading integration
- Multiple data vendors integrated

**Code Example:**
```python
# QuantConnect Algorithm Framework
class MyAlgorithm(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2025, 1, 1)
        self.SetCash(100000)

        # Add equity with minute resolution
        self.AddEquity("AAPL", Resolution.Minute)

        # Add options
        option = self.AddOption("AAPL", Resolution.Minute)
        option.SetFilter(-5, 5, 0, 30)

    def OnData(self, data):
        # Access historical data
        history = self.History(["AAPL"], 30, Resolution.Daily)

        # Check for corporate actions
        if data.Splits.ContainsKey("AAPL"):
            split = data.Splits["AAPL"]
            self.Debug(f"Split occurred: {split.SplitFactor}")

        if data.Dividends.ContainsKey("AAPL"):
            dividend = data.Dividends["AAPL"]
            self.Debug(f"Dividend: ${dividend.Distribution}")
```

---

### 22. Norgate Data

**Provider:** Norgate Data
**URL:** https://norgatedata.com/

**Data Coverage:**
- Exchanges: US, Australian, Canadian, European markets
- Instruments: Stocks, ETFs, indices, futures
- Historical Range: Extensive (back to 1950s for some indices)
- Delisted securities included (survivorship-bias free)

**Data Granularity:**
- 1-minute bars
- Daily
- Weekly
- Monthly

**Data Fields:**
- OHLCV
- Adjusted and unadjusted prices
- Delisted securities
- Index constituents (historical)
- Futures continuous contracts

**Access Method:**
- Desktop application (Windows)
- Python library (norgatedata)
- Direct integration with Amibroker, MetaStock, etc.
- Local database

**Cost:**
- Silver: $29.95/month - US stocks & ETFs
- Gold: $59.95/month - Add futures data
- Platinum: $99.95/month - Add delisted securities & more markets
- Diamond: $199.95/month - Full coverage including 1-min bars

**Pre-Market/After-Hours:**
- ❌ Regular hours only for daily data
- ⚠️ Some extended hours in minute data

**Corporate Actions:**
- ✅ Comprehensive adjustment handling
- ✅ Multiple adjustment modes
- ✅ Delisted securities (prevents survivorship bias)
- ✅ Historical index constituents

**Notable Features:**
- Survivorship-bias free data
- Historical index constituents
- Excellent for backtesting
- Local database (fast access)
- Python integration

**Code Example:**
```python
import norgatedata

# Get price data
pricedata = norgatedata.price_timeseries(
    'AAPL',
    stock_price_adjustment_setting=norgatedata.StockPriceAdjustmentType.TOTALRETURN,
    padding_setting=norgatedata.PaddingType.NONE,
    start_date='2020-01-01',
    end_date='2025-01-01',
    timeseriesformat='pandas-dataframe'
)

# Get index constituents (historical)
constituents = norgatedata.index_constituent_timeseries(
    'S&P 500',
    start_date='2020-01-01'
)

# Check if stock was in index on specific date
was_in_sp500 = norgatedata.index_constituent_held_on_date(
    'AAPL',
    'S&P 500',
    '2024-01-01'
)
```

---

## Comparison Matrix

| Provider | Cost (Starting) | Pre/Post Hours | Options Data | Tick Data | Free Tier | Best For |
|----------|----------------|----------------|--------------|-----------|-----------|----------|
| **Yahoo Finance** | Free | ❌ | Limited | ❌ | ✅ | Quick research, testing |
| **Alpha Vantage** | Free-$30/mo | ❌ | ❌ | ❌ | ✅ | Small projects, technicals |
| **Polygon.io** | $29-$399/mo | ✅ | ✅ | ✅ | Limited | Algo trading, options |
| **Finnhub** | Free-$200/mo | ⚠️ | Limited | ❌ | ✅ | News, fundamentals |
| **Twelve Data** | Free-$329/mo | ✅ | ❌ | ❌ | ✅ | Reliable APIs, global data |
| **Marketstack** | $10-$150/mo | ⚠️ | ❌ | ⚠️ | Limited | EOD data, simple use |
| **EODHD** | €20-€80/mo | ⚠️ | ✅ | ❌ | ❌ | Bulk historical, fundamentals |
| **Databento** | Pay-per-use | ✅ | ✅ | ✅ | $125 credit | Institutional, tick data |
| **Tiingo** | $10-$500/mo | ✅ | Limited | ⚠️ | Limited | Quality data, news |
| **Intrinio** | $75+/mo | ✅ | ✅ | ✅ | ❌ | Customized feeds |
| **Xignite** | Enterprise | ✅ | ✅ | ✅ | ❌ | Enterprise, global |
| **Interactive Brokers** | Free* | ✅ | ✅ | ✅ | Account req | Trading, global markets |
| **TD Ameritrade** | Free | ✅ | ✅ | ❌ | ✅ | Free API, options |
| **Alpaca** | $9-$99/mo | ✅ | Limited | ✅ | Account req | Algo trading, modern API |
| **Tradier** | Free* | ✅ | ✅ | ⚠️ | Account req | Options Greeks |
| **Market Data App** | $25-$100/mo | ✅ | ✅ | ❌ | ❌ | Options Greeks, sheets |
| **CBOE DataShop** | Enterprise | ✅ | ✅ | ✅ | ❌ | Official options data |
| **First Rate Data** | $299-$99/mo | ❌ | ✅ | ❌ | ❌ | Historical options bulk |
| **IQFeed** | $45-$200/mo | ✅ | ✅ | ✅ | ❌ | HFT, professional trading |
| **eSignal** | $204-$416/mo | ✅ | ✅ | ✅ | ❌ | Professional platform |
| **QuantConnect** | Free-$50/mo | ✅ | ✅ | ✅ | ✅ | Backtesting, algo dev |
| **Norgate Data** | $30-$200/mo | ⚠️ | ❌ | ⚠️ | ❌ | Survivorship-free, backtesting |

*Free with account/activity requirements

---

## Code Examples

### Pandas DataReader with yfinance Override

```python
import yfinance as yf
import pandas_datareader as pdr
from datetime import datetime

# Override pandas_datareader to use yfinance
yf.pdr_override()

# Download data
data = pdr.get_data_yahoo('AAPL', start='2020-01-01', end='2025-01-01')

# Multiple symbols
tickers = ['AAPL', 'MSFT', 'GOOGL']
data_multi = pdr.get_data_yahoo(tickers, start='2020-01-01', end='2025-01-01')

# Just adjusted close
adj_close = pdr.get_data_yahoo(tickers, start='2020-01-01')['Adj Close']
```

### Multi-Source Data Aggregation

```python
import pandas as pd
import yfinance as yf
import requests

class MultiSourceData:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_yfinance_data(self, start, end):
        """Free daily data"""
        ticker = yf.Ticker(self.symbol)
        return ticker.history(start=start, end=end)

    def get_alphavantage_data(self, api_key):
        """Get Alpha Vantage data"""
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={self.symbol}&apikey={api_key}&outputsize=full'
        r = requests.get(url)
        data = r.json()['Time Series (Daily)']
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index)
        return df.astype(float)

    def get_polygon_data(self, api_key, start, end):
        """Get Polygon.io tick data"""
        from polygon import RESTClient
        client = RESTClient(api_key)
        aggs = client.get_aggs(
            ticker=self.symbol,
            multiplier=1,
            timespan="day",
            from_=start,
            to=end
        )
        return pd.DataFrame(aggs)

    def merge_sources(self, start, end, alphavantage_key=None, polygon_key=None):
        """Combine multiple sources with fallback"""
        try:
            # Try polygon first (most reliable)
            if polygon_key:
                return self.get_polygon_data(polygon_key, start, end)
        except:
            pass

        try:
            # Fallback to Alpha Vantage
            if alphavantage_key:
                return self.get_alphavantage_data(alphavantage_key)
        except:
            pass

        # Final fallback to yfinance
        return self.get_yfinance_data(start, end)

# Usage
msd = MultiSourceData('AAPL')
data = msd.merge_sources(
    '2020-01-01',
    '2025-01-01',
    alphavantage_key='YOUR_AV_KEY',
    polygon_key='YOUR_POLYGON_KEY'
)
```

### Pre-Market Data Collection

```python
import pandas as pd
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, time

def get_premarket_data(symbol, date, api_key, secret_key):
    """
    Get pre-market data (4:00 AM - 9:30 AM ET)
    """
    client = StockHistoricalDataClient(api_key, secret_key)

    # Define pre-market hours
    premarket_start = datetime.combine(date, time(4, 0))  # 4:00 AM
    premarket_end = datetime.combine(date, time(9, 30))   # 9:30 AM

    request = StockBarsRequest(
        symbol_or_symbols=[symbol],
        timeframe=TimeFrame.Minute,
        start=premarket_start,
        end=premarket_end
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    # Filter for pre-market only
    premarket_df = df.between_time('04:00', '09:29')

    return premarket_df

# Usage
premarket = get_premarket_data(
    'AAPL',
    datetime(2024, 11, 15).date(),
    'YOUR_API_KEY',
    'YOUR_SECRET_KEY'
)

print(f"Pre-market volume: {premarket['volume'].sum()}")
print(f"Pre-market high: {premarket['high'].max()}")
print(f"Pre-market low: {premarket['low'].min()}")
```

### Corporate Actions Tracking

```python
import requests
import pandas as pd

def get_corporate_actions(symbol, start_date, end_date):
    """
    Aggregate corporate actions from multiple sources
    """
    actions = {
        'splits': [],
        'dividends': [],
        'mergers': []
    }

    # Get from EODHD
    eodhd_token = 'YOUR_TOKEN'
    url = f'https://eodhd.com/api/div/{symbol}.US?api_token={eodhd_token}&from={start_date}&to={end_date}&fmt=json'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            for item in data:
                if item['type'] == 'dividend':
                    actions['dividends'].append({
                        'date': item['date'],
                        'amount': item['value']
                    })
                elif item['type'] == 'split':
                    actions['splits'].append({
                        'date': item['date'],
                        'ratio': item['split']
                    })
    except Exception as e:
        print(f"Error fetching EODHD data: {e}")

    # Get from yfinance as backup
    import yfinance as yf
    ticker = yf.Ticker(symbol)

    splits_df = ticker.splits
    if not splits_df.empty:
        for date, ratio in splits_df.items():
            if start_date <= date.strftime('%Y-%m-%d') <= end_date:
                actions['splits'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'ratio': ratio
                })

    div_df = ticker.dividends
    if not div_df.empty:
        for date, amount in div_df.items():
            if start_date <= date.strftime('%Y-%m-%d') <= end_date:
                actions['dividends'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'amount': amount
                })

    return actions

# Usage
actions = get_corporate_actions('AAPL', '2020-01-01', '2025-01-01')
print(f"Splits: {len(actions['splits'])}")
print(f"Dividends: {len(actions['dividends'])}")
```

### Adjusting Prices for Splits

```python
import pandas as pd
import numpy as np

def adjust_for_splits(prices_df, splits_df):
    """
    Manually adjust historical prices for stock splits

    Parameters:
    - prices_df: DataFrame with 'date' and OHLCV columns
    - splits_df: DataFrame with 'date' and 'ratio' columns
    """
    df = prices_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Calculate cumulative adjustment factor
    adjustment_factor = 1.0

    for _, split in splits_df.iterrows():
        split_date = pd.to_datetime(split['date'])
        split_ratio = split['ratio']

        # Adjust all prices before the split
        mask = df['date'] < split_date

        df.loc[mask, 'open'] = df.loc[mask, 'open'] / split_ratio
        df.loc[mask, 'high'] = df.loc[mask, 'high'] / split_ratio
        df.loc[mask, 'low'] = df.loc[mask, 'low'] / split_ratio
        df.loc[mask, 'close'] = df.loc[mask, 'close'] / split_ratio
        df.loc[mask, 'volume'] = df.loc[mask, 'volume'] * split_ratio

    return df

# Example usage
prices = pd.DataFrame({
    'date': pd.date_range('2020-01-01', '2020-12-31'),
    'close': np.random.randn(366).cumsum() + 100
})

splits = pd.DataFrame({
    'date': ['2020-08-31'],  # Apple's 4-for-1 split
    'ratio': [4.0]
})

adjusted = adjust_for_splits(prices, splits)
```

---

## Recommendations by Use Case

### For Beginners / Research
- **Yahoo Finance (yfinance)**: Free, easy to use
- **Alpha Vantage**: Free tier, good documentation
- **Finnhub**: Good free tier with news and fundamentals

### For Algorithmic Trading
- **Alpaca**: Modern API, commission-free, extended hours
- **Interactive Brokers**: Professional execution, global markets
- **Polygon.io**: Unlimited API calls, tick data

### For Options Trading
- **Tradier**: Free Greeks, good options chains
- **Polygon.io**: Historical options, Greeks available
- **Market Data App**: Real-time Greeks calculation
- **CBOE DataShop**: Official exchange data

### For Backtesting
- **EODHD**: Cost-effective bulk historical data
- **Norgate Data**: Survivorship-bias free, index constituents
- **QuantConnect**: Integrated backtesting platform
- **Databento**: Institutional-grade tick data

### For Pre-Market Trading
- **Alpaca**: Full extended hours (4am-8pm)
- **Interactive Brokers**: Global pre-market access
- **Polygon.io**: Extended hours tick data
- **Twelve Data**: Extended hours in Pro tier

### For High-Frequency Trading
- **IQFeed**: Low latency, every tick
- **Databento**: Sub-microsecond timestamps
- **Interactive Brokers**: Direct market access
- **eSignal**: Professional-grade ticks

### For Global Markets
- **Interactive Brokers**: 150+ markets, 33 countries
- **Xignite**: 200+ data sources globally
- **EODHD**: 150+ exchanges worldwide
- **Intrinio**: Global coverage, standardized data

---

## Important Considerations

### Data Quality
- Always validate data from multiple sources
- Check for missing data, especially around corporate actions
- Verify adjusted vs. unadjusted prices
- Test with known historical events

### Corporate Actions
- Ensure your data is adjusted for splits and dividends
- Understand the difference between split-adjusted and total-return adjusted
- Keep track of delisting and ticker changes
- Validate adjustment factors

### Pre-Market Data Considerations
- Lower liquidity in extended hours
- Wider bid-ask spreads
- Different trading rules
- Not all stocks trade pre-market
- Validate data quality (can have errors)

### Rate Limits
- Free tiers have strict rate limits
- Plan your data requests efficiently
- Consider caching data locally
- Use bulk downloads when possible

### Survivorship Bias
- Use Norgate Data or similar for survivorship-bias free datasets
- Include delisted securities in backtests
- Track index constituent changes over time

### Costs
- Start with free tiers for testing
- Scale up as needed
- Consider data storage costs
- Factor in exchange fees for real-time data

---

## Conclusion

This comprehensive guide covers 20+ data sources suitable for quantitative trading with pre-market capabilities. Key takeaways:

1. **Free Options**: Yahoo Finance, Alpha Vantage, Finnhub provide good starting points
2. **Premium Quality**: Polygon.io, Databento, IQFeed for professional needs
3. **Broker APIs**: Interactive Brokers, Alpaca offer free data with accounts
4. **Options Focus**: Tradier, Market Data, CBOE for options with Greeks
5. **Extended Hours**: Alpaca, Polygon.io, IB, Twelve Data have best coverage
6. **Backtesting**: EODHD, Norgate, QuantConnect for historical analysis

Choose based on your specific needs: budget, data granularity, market coverage, and whether you need pre-market/options data.

---

*Document created: November 2025*
*For updates and corrections, please refer to individual provider documentation.*
