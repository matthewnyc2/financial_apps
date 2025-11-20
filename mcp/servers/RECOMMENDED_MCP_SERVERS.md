# Recommended MCP Servers for Financial Data Integration and Trading Operations

**Last Updated:** November 18, 2025
**Author:** Financial Apps Architecture Team
**Version:** 1.0

---

## Table of Contents

1. [Introduction to MCP in Financial Systems](#introduction)
2. [Market Data Distribution Servers](#market-data-distribution)
3. [Historical & Backtesting Data Servers](#historical-backtesting)
4. [Real-Time Trading & Order Management](#trading-order-management)
5. [Portfolio & Risk Management Servers](#portfolio-risk)
6. [Economic Data & Macroeconomic Indicators](#economic-data)
7. [News & Sentiment Analysis Servers](#news-sentiment)
8. [Cryptocurrency & Digital Assets](#cryptocurrency)
9. [Options & Derivatives Data](#options-derivatives)
10. [Implementation Guide](#implementation-guide)
11. [Integration Patterns](#integration-patterns)
12. [Security Considerations](#security)

---

## Introduction to MCP in Financial Systems {#introduction}

The **Model Context Protocol (MCP)** is an open protocol that standardizes how AI models interact with external tools, data sources, and systems. For financial applications, MCP provides:

- **Standardized Communication**: Unified interface for diverse financial data sources
- **AI Integration**: Seamless connection between LLMs and trading systems
- **Data Consistency**: Structured data flow across market data, execution, and analytics
- **Modular Architecture**: Plug-and-play components for different financial services

### MCP Architecture in Trading Systems

```
┌─────────────┐
│   AI Agent  │ (Claude, GPT, etc.)
│  (LLM Client)│
└──────┬──────┘
       │ MCP Protocol
       │
┌──────▼──────────────────────────┐
│   MCP Server Layer              │
│  - Market Data                  │
│  - Order Management             │
│  - Risk Analytics               │
│  - Portfolio Management         │
└──────┬──────────────────────────┘
       │
┌──────▼──────────────────────────┐
│   Financial Data Sources        │
│  - Exchanges                    │
│  - Brokers                      │
│  - Data Providers               │
│  - Economic Databases           │
└─────────────────────────────────┘
```

---

## 1. Alpha Vantage MCP Server {#market-data-distribution}

### Overview
Official Alpha Vantage API MCP server providing comprehensive real-time and historical market data across multiple asset classes.

**GitHub:** Official Alpha Vantage MCP
**Website:** https://mcp.alphavantage.co/
**Technology:** Python/TypeScript
**License:** Open Source

### Financial Data Types Served

- **Equities**: Real-time quotes, historical daily/intraday prices
- **Options**: Real-time options data, Greeks, IV surface
- **Forex**: 150+ currency pairs, real-time and historical
- **Cryptocurrencies**: 500+ digital assets, market cap, volume
- **Commodities**: Oil, gold, silver, agricultural products
- **ETFs**: ETF holdings, sector allocations, performance
- **Economic Indicators**: GDP, unemployment, inflation, interest rates

### Protocol Operations Supported

```typescript
// Available Tools/Resources
{
  "tools": [
    "TIME_SERIES_DAILY",           // Historical daily prices
    "TIME_SERIES_INTRADAY",        // Intraday 1min, 5min, 15min, 30min, 60min
    "REALTIME_OPTIONS",            // Real-time options data
    "CURRENCY_EXCHANGE_RATE",      // FX rates
    "DIGITAL_CURRENCY_DAILY",      // Crypto OHLCV
    "RSI",                         // Relative Strength Index
    "MACD",                        // Moving Average Convergence Divergence
    "SMA",                         // Simple Moving Average
    "EMA",                         // Exponential Moving Average
    "BBANDS",                      // Bollinger Bands
    "COMPANY_OVERVIEW",            // Fundamental data
    "INCOME_STATEMENT",            // Financial statements
    "BALANCE_SHEET",               // Balance sheet data
    "CASH_FLOW",                   // Cash flow statements
    "EARNINGS",                    // Earnings data
    "NEWS_SENTIMENT"               // Market news with sentiment
  ]
}
```

### Integration Points

1. **Market Data Pipeline**: Ingest real-time and historical data
2. **Technical Analysis**: Built-in 50+ technical indicators
3. **Fundamental Analysis**: Financial statements and metrics
4. **Sentiment Analysis**: News sentiment scoring
5. **Multi-Asset Coverage**: Single API for stocks, forex, crypto

### Implementation Example

```python
# Alpha Vantage MCP Server Setup
# File: alpha_vantage_mcp_server.py

from mcp import Server, Tool
import requests
import os

class AlphaVantageMCPServer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"

    def get_time_series_daily(self, symbol: str, outputsize: str = "compact"):
        """
        Fetch daily time series data for a given symbol.

        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            outputsize: 'compact' (100 days) or 'full' (20+ years)
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize,
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_technical_indicator(self, symbol: str, indicator: str,
                                interval: str = "daily", time_period: int = 14):
        """
        Calculate technical indicators (RSI, MACD, SMA, etc.)

        Args:
            symbol: Stock ticker
            indicator: Technical indicator name (RSI, MACD, SMA, etc.)
            interval: Time interval (1min, 5min, daily, weekly, monthly)
            time_period: Number of data points for calculation
        """
        params = {
            'function': indicator,
            'symbol': symbol,
            'interval': interval,
            'time_period': time_period,
            'series_type': 'close',
            'apikey': self.api_key
        }
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_realtime_options(self, symbol: str, date: str = None):
        """
        Retrieve real-time options data including Greeks.

        Args:
            symbol: Underlying stock ticker
            date: Expiration date (optional, defaults to nearest)
        """
        params = {
            'function': 'REALTIME_OPTIONS',
            'symbol': symbol,
            'apikey': self.api_key
        }
        if date:
            params['date'] = date
        response = requests.get(self.base_url, params=params)
        return response.json()

    def get_news_sentiment(self, tickers: str = None, topics: str = None,
                          time_from: str = None, time_to: str = None):
        """
        Fetch market news with AI-powered sentiment analysis.

        Args:
            tickers: Comma-separated ticker symbols
            topics: Topics (e.g., 'technology', 'finance')
            time_from: Start time (YYYYMMDDTHHMM)
            time_to: End time (YYYYMMDDTHHMM)
        """
        params = {
            'function': 'NEWS_SENTIMENT',
            'apikey': self.api_key
        }
        if tickers:
            params['tickers'] = tickers
        if topics:
            params['topics'] = topics
        if time_from:
            params['time_from'] = time_from
        if time_to:
            params['time_to'] = time_to
        response = requests.get(self.base_url, params=params)
        return response.json()

# MCP Server Configuration
def setup_mcp_server():
    server = Server("alpha-vantage-mcp")
    av = AlphaVantageMCPServer(os.getenv('ALPHA_VANTAGE_API_KEY'))

    # Register tools
    server.register_tool(
        Tool(
            name="get_stock_daily_data",
            description="Fetch daily stock prices",
            handler=av.get_time_series_daily
        )
    )

    server.register_tool(
        Tool(
            name="calculate_technical_indicator",
            description="Calculate technical indicators (RSI, MACD, etc.)",
            handler=av.get_technical_indicator
        )
    )

    server.register_tool(
        Tool(
            name="get_options_data",
            description="Get real-time options data with Greeks",
            handler=av.get_realtime_options
        )
    )

    server.register_tool(
        Tool(
            name="analyze_news_sentiment",
            description="Analyze market news sentiment",
            handler=av.get_news_sentiment
        )
    )

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Multi-Asset Portfolio Analysis**: Single source for stocks, forex, crypto
2. **Technical Trading Strategies**: Pre-calculated indicators for signal generation
3. **Fundamental Screening**: Filter stocks based on financial metrics
4. **Sentiment-Based Trading**: Incorporate news sentiment into models
5. **Options Strategy Backtesting**: Historical options data with Greeks
6. **Economic Calendar Integration**: Track macro events and indicators

---

## 2. Twelve Data MCP Server

### Overview
Professional-grade financial market data API with WebSocket support for real-time streaming.

**GitHub:** https://github.com/twelvedata/mcp
**Technology:** Python, WebSocket
**Data Coverage:** 60,000+ instruments

### Financial Data Types Served

- **Stocks**: Global equities from 100+ exchanges
- **Forex**: 2,000+ currency pairs
- **Cryptocurrencies**: 1,000+ digital assets
- **ETFs**: Exchange-traded funds worldwide
- **Indices**: Major global market indices
- **Bonds**: Government and corporate bonds

### Protocol Operations Supported

```javascript
// WebSocket Real-Time Streaming
{
  "subscribe": {
    "action": "subscribe",
    "params": {
      "symbols": ["AAPL", "MSFT", "GOOGL"],
      "event": "price"  // price, quote, heartbeat
    }
  },

  "time_series": {
    "interval": "1min|5min|15min|30min|1h|1day|1week|1month",
    "outputsize": 5000,  // Max data points
    "timezone": "America/New_York"
  },

  "technical_indicators": [
    "SMA", "EMA", "WMA", "DEMA", "TEMA", "TRIMA",
    "KAMA", "MAMA", "VWAP", "T3", "MACD", "MACDEXT",
    "STOCH", "STOCHF", "RSI", "STOCHRSI", "WILLR",
    "ADX", "ADXR", "APO", "PPO", "MOM", "BOP",
    "CCI", "CMO", "ROC", "ROCR", "AROON", "AROONOSC",
    "MFI", "TRIX", "ULTOSC", "DX", "MINUS_DI",
    "PLUS_DI", "MINUS_DM", "PLUS_DM", "BBANDS",
    "MIDPOINT", "MIDPRICE", "SAR", "TRANGE", "ATR",
    "NATR", "AD", "ADOSC", "OBV", "HT_TRENDLINE",
    "HT_SINE", "HT_TRENDMODE", "HT_DCPERIOD",
    "HT_DCPHASE", "HT_PHASOR"
  ],

  "fundamentals": [
    "profile", "dividends", "splits", "earnings",
    "earnings_calendar", "ipo_calendar", "statistics",
    "insider_transactions", "income_statement",
    "balance_sheet", "cash_flow", "options_expiration"
  ]
}
```

### Integration Points

1. **Real-Time Data Streaming**: WebSocket for live price updates
2. **Historical Data Warehouse**: Up to 30 years of historical data
3. **Technical Analysis Engine**: 100+ built-in indicators
4. **Fundamental Data Integration**: Earnings, financials, corporate actions
5. **Reference Data**: Instrument metadata, exchange calendars

### Implementation Example

```python
# Twelve Data MCP Server with WebSocket
# File: twelvedata_mcp_server.py

import asyncio
import websockets
import json
from mcp import Server, Tool, Resource
from twelvedata import TDClient

class TwelveDataMCPServer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.td = TDClient(apikey=api_key)
        self.ws_connection = None

    async def stream_prices(self, symbols: list, callback):
        """
        Stream real-time prices via WebSocket.

        Args:
            symbols: List of ticker symbols
            callback: Function to handle incoming data
        """
        ws_url = "wss://ws.twelvedata.com/v1/quotes/price"

        async with websockets.connect(ws_url) as websocket:
            subscribe_message = {
                "action": "subscribe",
                "params": {
                    "symbols": ",".join(symbols)
                }
            }
            await websocket.send(json.dumps(subscribe_message))

            while True:
                message = await websocket.recv()
                data = json.loads(message)
                await callback(data)

    def get_time_series(self, symbol: str, interval: str = "1day",
                       outputsize: int = 30, **kwargs):
        """
        Fetch historical time series data.

        Args:
            symbol: Ticker symbol
            interval: Time interval (1min, 5min, 15min, 30min, 1h, 1day, etc.)
            outputsize: Number of data points (max 5000)
        """
        ts = self.td.time_series(
            symbol=symbol,
            interval=interval,
            outputsize=outputsize,
            **kwargs
        )
        return ts.as_json()

    def get_technical_indicator(self, symbol: str, indicator: str,
                               interval: str = "1day", **params):
        """
        Calculate technical indicators.

        Args:
            symbol: Ticker symbol
            indicator: Indicator name (e.g., 'rsi', 'macd', 'bbands')
            interval: Time interval
            **params: Indicator-specific parameters
        """
        indicator_method = getattr(self.td, indicator.lower())
        result = indicator_method(
            symbol=symbol,
            interval=interval,
            **params
        )
        return result.as_json()

    def get_quote(self, symbol: str):
        """Get real-time quote for a symbol."""
        quote = self.td.quote(symbol=symbol)
        return quote.as_json()

    def get_fundamentals(self, symbol: str, data_type: str = "profile"):
        """
        Fetch fundamental data.

        Args:
            symbol: Ticker symbol
            data_type: profile, dividends, splits, earnings, etc.
        """
        if data_type == "profile":
            result = self.td.get_stock_profile(symbol)
        elif data_type == "dividends":
            result = self.td.get_dividends(symbol)
        elif data_type == "splits":
            result = self.td.get_splits(symbol)
        elif data_type == "earnings":
            result = self.td.get_earnings(symbol)
        elif data_type == "income_statement":
            result = self.td.get_income_statement(symbol)
        elif data_type == "balance_sheet":
            result = self.td.get_balance_sheet(symbol)
        elif data_type == "cash_flow":
            result = self.td.get_cash_flow(symbol)
        else:
            raise ValueError(f"Unknown data type: {data_type}")

        return result.as_json()

    def get_exchange_rate(self, symbol: str, base_currency: str = "USD"):
        """
        Get forex exchange rate.

        Args:
            symbol: Currency pair symbol
            base_currency: Base currency code
        """
        rate = self.td.exchange_rate(
            symbol=f"{symbol}/{base_currency}"
        )
        return rate.as_json()

# Configuration
def setup_mcp_server():
    import os
    server = Server("twelvedata-mcp")
    td_server = TwelveDataMCPServer(os.getenv('TWELVE_DATA_API_KEY'))

    # Register tools
    tools = [
        Tool(
            name="get_time_series",
            description="Fetch historical price data",
            handler=td_server.get_time_series
        ),
        Tool(
            name="calculate_indicator",
            description="Calculate technical indicators",
            handler=td_server.get_technical_indicator
        ),
        Tool(
            name="get_real_time_quote",
            description="Get real-time quote",
            handler=td_server.get_quote
        ),
        Tool(
            name="get_company_fundamentals",
            description="Fetch fundamental data",
            handler=td_server.get_fundamentals
        ),
        Tool(
            name="get_forex_rate",
            description="Get currency exchange rate",
            handler=td_server.get_exchange_rate
        )
    ]

    for tool in tools:
        server.register_tool(tool)

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **High-Frequency Trading**: Low-latency WebSocket streaming
2. **Multi-Asset Strategies**: Unified API for stocks, forex, crypto
3. **Global Market Coverage**: Access to 100+ international exchanges
4. **Technical Analysis**: Pre-calculated indicators reduce compute overhead
5. **Fundamental Research**: Corporate actions and financial statements
6. **Currency Hedging**: Real-time forex data for multi-currency portfolios

---

## 3. QuantConnect MCP Server {#historical-backtesting}

### Overview
Comprehensive quantitative trading platform with 400TB+ historical data and cloud-based backtesting engine.

**GitHub:** Community & Official implementations
**Website:** https://www.quantconnect.com
**Technology:** C#, Python
**Data Coverage:** 20+ years historical data

### Financial Data Types Served

- **Equities**: US stocks, tick-level to daily data
- **Options**: Full options chain history
- **Futures**: Commodity and financial futures
- **Forex**: Tick-level FX data
- **Cryptocurrencies**: Bitcoin, Ethereum, major altcoins
- **Alternative Data**: Sentiment, fundamentals, macro indicators
- **CFDs**: Contracts for difference

### Protocol Operations Supported

```python
# QuantConnect MCP Tools
{
  "tools": [
    # Project Management
    "create_project",
    "list_projects",
    "read_project_file",
    "update_project_file",
    "delete_project",

    # Data Access
    "get_historical_data",
    "get_market_hours",
    "get_symbol_properties",
    "search_symbols",

    # Backtesting
    "create_backtest",
    "read_backtest_results",
    "list_backtests",
    "get_backtest_report",
    "compare_backtests",

    # Live Trading
    "create_live_algorithm",
    "stop_live_algorithm",
    "get_live_status",
    "liquidate_live_algorithm",

    # Optimization
    "create_optimization",
    "read_optimization_results",
    "get_parameter_sensitivity",

    # Portfolio Construction
    "run_portfolio_optimizer",
    "get_risk_metrics",
    "calculate_sharpe_ratio",
    "calculate_max_drawdown"
  ]
}
```

### Integration Points

1. **Historical Data Warehouse**: 400TB+ tick-to-daily data
2. **Backtesting Engine**: Cloud-based strategy testing
3. **Live Trading**: 20+ broker integrations
4. **Research Environment**: Jupyter notebooks, IDE integration
5. **Portfolio Optimization**: Mean-variance, Black-Litterman, risk parity
6. **Alternative Data**: Sentiment, short interest, insider trading

### Implementation Example

```python
# QuantConnect MCP Server
# File: quantconnect_mcp_server.py

from mcp import Server, Tool
import requests
import json
from typing import Dict, List, Optional

class QuantConnectMCPServer:
    def __init__(self, user_id: str, api_token: str):
        self.user_id = user_id
        self.api_token = api_token
        self.base_url = "https://www.quantconnect.com/api/v2"
        self.headers = {
            "Authorization": f"Basic {self._encode_credentials()}"
        }

    def _encode_credentials(self):
        import base64
        credentials = f"{self.user_id}:{self.api_token}"
        return base64.b64encode(credentials.encode()).decode()

    def create_project(self, name: str, language: str = "Py"):
        """
        Create a new algorithm project.

        Args:
            name: Project name
            language: Programming language ('Py' or 'CS')
        """
        url = f"{self.base_url}/projects/create"
        params = {
            "name": name,
            "language": language
        }
        response = requests.post(url, params=params, headers=self.headers)
        return response.json()

    def create_backtest(self, project_id: int, compile_id: str,
                       backtest_name: str):
        """
        Run a backtest for an algorithm.

        Args:
            project_id: Project ID
            compile_id: Compilation ID
            backtest_name: Name for the backtest
        """
        url = f"{self.base_url}/backtests/create"
        params = {
            "projectId": project_id,
            "compileId": compile_id,
            "backtestName": backtest_name
        }
        response = requests.post(url, params=params, headers=self.headers)
        return response.json()

    def read_backtest(self, project_id: int, backtest_id: str):
        """
        Get backtest results and statistics.

        Args:
            project_id: Project ID
            backtest_id: Backtest ID
        """
        url = f"{self.base_url}/backtests/read"
        params = {
            "projectId": project_id,
            "backtestId": backtest_id
        }
        response = requests.get(url, params=params, headers=self.headers)
        return response.json()

    def update_project_file(self, project_id: int, file_name: str,
                           content: str):
        """
        Update algorithm code.

        Args:
            project_id: Project ID
            file_name: File name (e.g., 'main.py')
            content: Python/C# code content
        """
        url = f"{self.base_url}/files/update"
        data = {
            "projectId": project_id,
            "name": file_name,
            "content": content
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

    def create_live_algorithm(self, project_id: int, compile_id: str,
                             server_type: str, brokerage: Dict,
                             data_provider: Dict):
        """
        Deploy algorithm to live trading.

        Args:
            project_id: Project ID
            compile_id: Compilation ID
            server_type: Server type (512, 1024, 2048 MB)
            brokerage: Brokerage configuration
            data_provider: Data feed configuration
        """
        url = f"{self.base_url}/live/create"
        data = {
            "projectId": project_id,
            "compileId": compile_id,
            "serverType": server_type,
            "brokerage": brokerage,
            "dataProvider": data_provider
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()

# Example Algorithm Code
SAMPLE_ALGORITHM = """
from AlgorithmImports import *

class MeanReversionAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)
        self.SetEndDate(2024, 12, 31)
        self.SetCash(100000)

        # Add SPY with minute resolution
        self.spy = self.AddEquity("SPY", Resolution.Minute).Symbol

        # Bollinger Bands indicator
        self.bb = self.BB("SPY", 20, 2, Resolution.Daily)

        # Schedule function to run at market open
        self.Schedule.On(
            self.DateRules.EveryDay("SPY"),
            self.TimeRules.AfterMarketOpen("SPY", 1),
            self.Rebalance
        )

        self.SetWarmUp(20)

    def Rebalance(self):
        if self.IsWarmingUp:
            return

        price = self.Securities["SPY"].Price

        # Mean reversion logic
        if not self.Portfolio.Invested:
            # Buy when price touches lower band
            if price <= self.bb.LowerBand.Current.Value:
                self.SetHoldings("SPY", 1.0)
                self.Debug(f"BUY: Price {price} below lower band {self.bb.LowerBand.Current.Value}")
        else:
            # Sell when price touches upper band
            if price >= self.bb.UpperBand.Current.Value:
                self.Liquidate("SPY")
                self.Debug(f"SELL: Price {price} above upper band {self.bb.UpperBand.Current.Value}")

    def OnData(self, data):
        pass
"""

def setup_mcp_server():
    import os
    server = Server("quantconnect-mcp")
    qc = QuantConnectMCPServer(
        os.getenv('QC_USER_ID'),
        os.getenv('QC_API_TOKEN')
    )

    # Register tools
    server.register_tool(Tool(
        name="create_trading_project",
        description="Create new algorithm project",
        handler=qc.create_project
    ))

    server.register_tool(Tool(
        name="run_backtest",
        description="Execute backtest with historical data",
        handler=qc.create_backtest
    ))

    server.register_tool(Tool(
        name="get_backtest_results",
        description="Retrieve backtest performance metrics",
        handler=qc.read_backtest
    ))

    server.register_tool(Tool(
        name="update_algorithm_code",
        description="Modify algorithm code",
        handler=qc.update_project_file
    ))

    server.register_tool(Tool(
        name="deploy_live_trading",
        description="Deploy algorithm to live trading",
        handler=qc.create_live_algorithm
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Strategy Backtesting**: Test algorithms on 20+ years of data
2. **Multi-Asset Research**: Unified platform for equities, options, futures, forex, crypto
3. **Live Trading Deployment**: Paper and live trading with 20+ brokers
4. **Portfolio Optimization**: Risk-adjusted portfolio construction
5. **Alternative Data Integration**: Sentiment, fundamental, macroeconomic signals
6. **Institutional-Grade Research**: Jupyter notebooks, IDE integration

---

## 4. Alpaca MCP Server {#trading-order-management}

### Overview
Commission-free trading API with full order management and execution capabilities for stocks, options, and crypto.

**GitHub:** https://github.com/alpacahq/alpaca-mcp-server
**Technology:** Python, REST API, WebSocket
**Regulatory:** SEC-registered broker-dealer, FINRA member

### Financial Data Types Served

- **Stocks**: US equities, all listed securities
- **ETFs**: Exchange-traded funds
- **Options**: Equity options (calls and puts)
- **Cryptocurrencies**: Bitcoin, Ethereum, major altcoins
- **Account Data**: Positions, orders, portfolio value
- **Market Data**: Real-time and historical bars, quotes, trades

### Protocol Operations Supported

```typescript
// Alpaca MCP Tools
{
  "account_management": [
    "get_account",              // Account details, buying power
    "get_portfolio_history",    // Historical portfolio value
    "get_positions",            // Current positions
    "close_all_positions"       // Liquidate all holdings
  ],

  "order_management": [
    "submit_order",             // Market, limit, stop orders
    "get_orders",               // List all orders
    "get_order_by_id",          // Get specific order
    "cancel_order",             // Cancel pending order
    "cancel_all_orders",        // Cancel all open orders
    "replace_order"             // Modify existing order
  ],

  "market_data": [
    "get_bars",                 // OHLCV bars (1Min to 1Day)
    "get_latest_quote",         // Real-time bid/ask
    "get_latest_trade",         // Last trade price
    "get_snapshot",             // Complete market snapshot
    "get_news",                 // Market news
    "get_option_chain"          // Options data
  ],

  "order_types": {
    "market": "Execute at current market price",
    "limit": "Execute at specific price or better",
    "stop": "Trigger market order at stop price",
    "stop_limit": "Trigger limit order at stop price",
    "trailing_stop": "Dynamic stop based on price movement"
  },

  "time_in_force": [
    "day",      // Good for day
    "gtc",      // Good til cancelled
    "ioc",      // Immediate or cancel
    "fok",      // Fill or kill
    "opg",      // Market on open
    "cls"       // Market on close
  ]
}
```

### Integration Points

1. **Order Execution**: Direct market access for stocks, ETFs, options, crypto
2. **Account Management**: Real-time portfolio tracking
3. **Market Data**: Real-time and historical price data
4. **Paper Trading**: Simulated trading environment
5. **WebSocket Streaming**: Real-time market data and account updates
6. **Broker Integration**: Seamless connection to Alpaca brokerage

### Implementation Example

```python
# Alpaca MCP Server
# File: alpaca_mcp_server.py

from mcp import Server, Tool
from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.trading.requests import (
    MarketOrderRequest, LimitOrderRequest, StopOrderRequest,
    TakeProfitRequest, StopLossRequest
)
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import os

class AlpacaMCPServer:
    def __init__(self, api_key: str, secret_key: str, paper: bool = True):
        self.trading_client = TradingClient(
            api_key, secret_key, paper=paper
        )
        self.data_client = StockHistoricalDataClient(api_key, secret_key)

    def get_account_info(self):
        """Get account information including buying power."""
        account = self.trading_client.get_account()
        return {
            "account_number": account.account_number,
            "status": account.status,
            "currency": account.currency,
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
            "last_equity": float(account.last_equity),
            "long_market_value": float(account.long_market_value),
            "short_market_value": float(account.short_market_value),
            "initial_margin": float(account.initial_margin),
            "maintenance_margin": float(account.maintenance_margin),
            "daytrade_count": account.daytrade_count,
            "pattern_day_trader": account.pattern_day_trader
        }

    def submit_market_order(self, symbol: str, qty: float, side: str,
                           time_in_force: str = "day"):
        """
        Submit a market order.

        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            time_in_force: 'day', 'gtc', 'ioc', 'fok'
        """
        order_data = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            time_in_force=TimeInForce[time_in_force.upper()]
        )
        order = self.trading_client.submit_order(order_data)
        return self._serialize_order(order)

    def submit_limit_order(self, symbol: str, qty: float, side: str,
                          limit_price: float, time_in_force: str = "day"):
        """
        Submit a limit order.

        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            limit_price: Maximum buy price or minimum sell price
            time_in_force: Order duration
        """
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            limit_price=limit_price,
            time_in_force=TimeInForce[time_in_force.upper()]
        )
        order = self.trading_client.submit_order(order_data)
        return self._serialize_order(order)

    def submit_bracket_order(self, symbol: str, qty: float, side: str,
                           entry_price: float, take_profit_price: float,
                           stop_loss_price: float):
        """
        Submit a bracket order (entry + take profit + stop loss).

        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            entry_price: Entry limit price
            take_profit_price: Take profit limit price
            stop_loss_price: Stop loss price
        """
        order_data = LimitOrderRequest(
            symbol=symbol,
            qty=qty,
            side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
            limit_price=entry_price,
            time_in_force=TimeInForce.GTC,
            order_class="bracket",
            take_profit=TakeProfitRequest(limit_price=take_profit_price),
            stop_loss=StopLossRequest(stop_price=stop_loss_price)
        )
        order = self.trading_client.submit_order(order_data)
        return self._serialize_order(order)

    def get_all_positions(self):
        """Get all current positions."""
        positions = self.trading_client.get_all_positions()
        return [self._serialize_position(pos) for pos in positions]

    def get_position(self, symbol: str):
        """Get position for specific symbol."""
        position = self.trading_client.get_open_position(symbol)
        return self._serialize_position(position)

    def close_position(self, symbol: str, qty: float = None,
                      percentage: float = None):
        """
        Close a position.

        Args:
            symbol: Stock ticker
            qty: Number of shares to close (optional)
            percentage: Percentage of position to close (optional)
        """
        if qty:
            order = self.trading_client.close_position(symbol, qty=qty)
        elif percentage:
            order = self.trading_client.close_position(symbol, percentage=percentage)
        else:
            order = self.trading_client.close_position(symbol)
        return self._serialize_order(order)

    def get_orders(self, status: str = "all", limit: int = 100):
        """
        Get orders filtered by status.

        Args:
            status: 'all', 'open', 'closed'
            limit: Maximum number of orders to return
        """
        from alpaca.trading.requests import GetOrdersRequest
        from alpaca.trading.enums import QueryOrderStatus

        request = GetOrdersRequest(
            status=QueryOrderStatus[status.upper()],
            limit=limit
        )
        orders = self.trading_client.get_orders(request)
        return [self._serialize_order(order) for order in orders]

    def cancel_order(self, order_id: str):
        """Cancel a specific order."""
        self.trading_client.cancel_order_by_id(order_id)
        return {"status": "cancelled", "order_id": order_id}

    def get_historical_bars(self, symbol: str, start_date: str,
                           end_date: str, timeframe: str = "1Day"):
        """
        Get historical OHLCV bars.

        Args:
            symbol: Stock ticker
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Bar size (1Min, 5Min, 15Min, 1Hour, 1Day)
        """
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            start=datetime.fromisoformat(start_date),
            end=datetime.fromisoformat(end_date),
            timeframe=TimeFrame[timeframe]
        )
        bars = self.data_client.get_stock_bars(request)
        return self._serialize_bars(bars[symbol])

    def get_latest_quote(self, symbol: str):
        """Get latest bid/ask quote."""
        request = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        quote = self.data_client.get_stock_latest_quote(request)[symbol]
        return {
            "symbol": symbol,
            "bid_price": float(quote.bid_price),
            "bid_size": quote.bid_size,
            "ask_price": float(quote.ask_price),
            "ask_size": quote.ask_size,
            "timestamp": quote.timestamp.isoformat()
        }

    def _serialize_order(self, order):
        """Convert order object to dictionary."""
        return {
            "id": str(order.id),
            "client_order_id": order.client_order_id,
            "symbol": order.symbol,
            "qty": float(order.qty) if order.qty else None,
            "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
            "side": order.side.value,
            "type": order.order_type.value,
            "time_in_force": order.time_in_force.value,
            "limit_price": float(order.limit_price) if order.limit_price else None,
            "stop_price": float(order.stop_price) if order.stop_price else None,
            "status": order.status.value,
            "created_at": order.created_at.isoformat(),
            "filled_at": order.filled_at.isoformat() if order.filled_at else None,
            "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else None
        }

    def _serialize_position(self, position):
        """Convert position object to dictionary."""
        return {
            "symbol": position.symbol,
            "qty": float(position.qty),
            "avg_entry_price": float(position.avg_entry_price),
            "current_price": float(position.current_price),
            "market_value": float(position.market_value),
            "cost_basis": float(position.cost_basis),
            "unrealized_pl": float(position.unrealized_pl),
            "unrealized_plpc": float(position.unrealized_plpc),
            "side": position.side.value
        }

    def _serialize_bars(self, bars):
        """Convert bars to list of dictionaries."""
        return [
            {
                "timestamp": bar.timestamp.isoformat(),
                "open": float(bar.open),
                "high": float(bar.high),
                "low": float(bar.low),
                "close": float(bar.close),
                "volume": bar.volume,
                "vwap": float(bar.vwap) if bar.vwap else None
            }
            for bar in bars
        ]

# MCP Server Setup
def setup_mcp_server():
    server = Server("alpaca-trading-mcp")
    alpaca = AlpacaMCPServer(
        os.getenv('ALPACA_API_KEY'),
        os.getenv('ALPACA_SECRET_KEY'),
        paper=True  # Use paper trading by default
    )

    # Account tools
    server.register_tool(Tool(
        name="get_account",
        description="Get account information and buying power",
        handler=alpaca.get_account_info
    ))

    # Order execution tools
    server.register_tool(Tool(
        name="submit_market_order",
        description="Execute market order",
        handler=alpaca.submit_market_order
    ))

    server.register_tool(Tool(
        name="submit_limit_order",
        description="Execute limit order",
        handler=alpaca.submit_limit_order
    ))

    server.register_tool(Tool(
        name="submit_bracket_order",
        description="Execute bracket order with TP/SL",
        handler=alpaca.submit_bracket_order
    ))

    # Position management tools
    server.register_tool(Tool(
        name="get_positions",
        description="Get all current positions",
        handler=alpaca.get_all_positions
    ))

    server.register_tool(Tool(
        name="close_position",
        description="Close a position",
        handler=alpaca.close_position
    ))

    # Order management tools
    server.register_tool(Tool(
        name="get_orders",
        description="List orders",
        handler=alpaca.get_orders
    ))

    server.register_tool(Tool(
        name="cancel_order",
        description="Cancel an order",
        handler=alpaca.cancel_order
    ))

    # Market data tools
    server.register_tool(Tool(
        name="get_historical_data",
        description="Get historical OHLCV bars",
        handler=alpaca.get_historical_bars
    ))

    server.register_tool(Tool(
        name="get_quote",
        description="Get latest bid/ask quote",
        handler=alpaca.get_latest_quote
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Algorithmic Trading**: Automated order execution
2. **Portfolio Rebalancing**: Systematic position management
3. **Market Making**: Bid/ask quote management
4. **Bracket Orders**: Risk-managed entry/exit strategies
5. **Paper Trading**: Strategy testing without real capital
6. **Multi-Asset Trading**: Unified API for stocks, ETFs, options, crypto

---

## 5. Polygon.io MCP Server

### Overview
Enterprise-grade real-time and historical financial data with extensive news feeds and market events.

**GitHub:** https://github.com/polygon-io/mcp_polygon
**Technology:** REST API, WebSocket
**Data Coverage:** Stocks, options, forex, crypto

### Financial Data Types Served

- **Equities**: US stocks, real-time and historical
- **Options**: Full options chain with Greeks
- **Forex**: Global currency pairs
- **Cryptocurrencies**: Major digital assets
- **Market News**: Real-time news feed with publisher data
- **Ticker Details**: Company information, branding, metadata
- **Aggregates**: OHLCV bars at multiple timeframes

### Protocol Operations Supported

```javascript
// Polygon.io MCP Tools
{
  "market_data": {
    "get_aggregates": "OHLCV bars (minute to monthly)",
    "get_grouped_daily": "All tickers daily snapshot",
    "get_previous_close": "Previous day close",
    "get_snapshot_all": "Current snapshot all symbols",
    "get_snapshot_ticker": "Current snapshot single ticker"
  },

  "options_data": {
    "get_option_contract": "Single option contract details",
    "get_options_chain": "Full options chain for underlying",
    "get_option_snapshot": "Current option quote and Greeks"
  },

  "reference_data": {
    "get_ticker_details": "Company info, branding, address",
    "get_ticker_news": "News articles for ticker",
    "get_market_news": "General market news",
    "get_ticker_types": "Asset type classification",
    "get_exchanges": "Exchange metadata",
    "get_market_holidays": "Market calendar",
    "get_market_status": "Current market status"
  },

  "forex_crypto": {
    "get_forex_aggregates": "FX pair bars",
    "get_forex_quotes": "Real-time FX quotes",
    "get_crypto_aggregates": "Crypto OHLCV",
    "get_crypto_trades": "Crypto trade history"
  }
}
```

### Integration Points

1. **Real-Time Market Data**: WebSocket streaming for live prices
2. **Historical Data Access**: Years of tick-level history
3. **News Integration**: Real-time news with ticker associations
4. **Reference Data**: Company metadata, market calendars
5. **Options Analytics**: Greeks, IV, open interest
6. **Multi-Asset Support**: Stocks, options, forex, crypto unified API

### Implementation Example

```python
# Polygon.io MCP Server
# File: polygon_mcp_server.py

from mcp import Server, Tool
from polygon import RESTClient
from datetime import datetime, timedelta
import os

class PolygonMCPServer:
    def __init__(self, api_key: str):
        self.client = RESTClient(api_key)

    def get_aggregates(self, ticker: str, multiplier: int, timespan: str,
                      from_date: str, to_date: str, adjusted: bool = True):
        """
        Get OHLCV aggregates.

        Args:
            ticker: Stock ticker
            multiplier: Size of timespan (e.g., 1, 5, 15)
            timespan: Unit (minute, hour, day, week, month)
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            adjusted: Adjust for splits/dividends
        """
        aggs = self.client.get_aggs(
            ticker=ticker,
            multiplier=multiplier,
            timespan=timespan,
            from_=from_date,
            to=to_date,
            adjusted=adjusted
        )

        return [
            {
                "timestamp": datetime.fromtimestamp(agg.timestamp / 1000).isoformat(),
                "open": agg.open,
                "high": agg.high,
                "low": agg.low,
                "close": agg.close,
                "volume": agg.volume,
                "vwap": agg.vwap if hasattr(agg, 'vwap') else None,
                "transactions": agg.transactions if hasattr(agg, 'transactions') else None
            }
            for agg in aggs
        ]

    def get_ticker_news(self, ticker: str = None, limit: int = 10,
                       published_utc_gte: str = None):
        """
        Get news articles.

        Args:
            ticker: Filter by ticker symbol (optional)
            limit: Number of articles (max 1000)
            published_utc_gte: Published after this datetime
        """
        news = self.client.list_ticker_news(
            ticker=ticker,
            limit=limit,
            published_utc_gte=published_utc_gte
        )

        return [
            {
                "id": article.id,
                "publisher": article.publisher.name,
                "title": article.title,
                "author": article.author,
                "published_utc": article.published_utc,
                "article_url": article.article_url,
                "tickers": article.tickers,
                "keywords": article.keywords if hasattr(article, 'keywords') else [],
                "description": article.description if hasattr(article, 'description') else None
            }
            for article in news
        ]

    def get_ticker_details(self, ticker: str, date: str = None):
        """
        Get company details.

        Args:
            ticker: Stock ticker
            date: Date for historical details (optional)
        """
        details = self.client.get_ticker_details(ticker, date=date)

        return {
            "ticker": details.ticker,
            "name": details.name,
            "market": details.market,
            "locale": details.locale,
            "primary_exchange": details.primary_exchange,
            "type": details.type,
            "active": details.active,
            "currency_name": details.currency_name,
            "cik": details.cik if hasattr(details, 'cik') else None,
            "composite_figi": details.composite_figi if hasattr(details, 'composite_figi') else None,
            "share_class_figi": details.share_class_figi if hasattr(details, 'share_class_figi') else None,
            "market_cap": details.market_cap if hasattr(details, 'market_cap') else None,
            "phone_number": details.phone_number if hasattr(details, 'phone_number') else None,
            "address": {
                "address1": details.address.address1 if hasattr(details, 'address') else None,
                "city": details.address.city if hasattr(details, 'address') else None,
                "state": details.address.state if hasattr(details, 'address') else None,
                "postal_code": details.address.postal_code if hasattr(details, 'address') else None
            } if hasattr(details, 'address') else None,
            "description": details.description if hasattr(details, 'description') else None,
            "sic_code": details.sic_code if hasattr(details, 'sic_code') else None,
            "sic_description": details.sic_description if hasattr(details, 'sic_description') else None,
            "homepage_url": details.homepage_url if hasattr(details, 'homepage_url') else None,
            "total_employees": details.total_employees if hasattr(details, 'total_employees') else None,
            "list_date": details.list_date if hasattr(details, 'list_date') else None,
            "branding": {
                "logo_url": details.branding.logo_url if hasattr(details, 'branding') else None,
                "icon_url": details.branding.icon_url if hasattr(details, 'branding') else None
            } if hasattr(details, 'branding') else None
        }

    def get_snapshot(self, ticker: str):
        """Get current market snapshot for a ticker."""
        snapshot = self.client.get_snapshot_ticker("stocks", ticker)

        return {
            "ticker": snapshot.ticker,
            "updated": datetime.fromtimestamp(snapshot.updated / 1000000000).isoformat(),
            "day": {
                "open": snapshot.day.open,
                "high": snapshot.day.high,
                "low": snapshot.day.low,
                "close": snapshot.day.close,
                "volume": snapshot.day.volume,
                "vwap": snapshot.day.vwap
            },
            "prev_day": {
                "open": snapshot.prev_day.open,
                "high": snapshot.prev_day.high,
                "low": snapshot.prev_day.low,
                "close": snapshot.prev_day.close,
                "volume": snapshot.prev_day.volume,
                "vwap": snapshot.prev_day.vwap
            },
            "min": {
                "accumulated_volume": snapshot.min.av,
                "open": snapshot.min.o,
                "high": snapshot.min.h,
                "low": snapshot.min.l,
                "close": snapshot.min.c,
                "volume": snapshot.min.v,
                "vwap": snapshot.min.vw
            } if hasattr(snapshot, 'min') else None
        }

    def get_options_chain(self, underlying_ticker: str,
                         expiration_date: str = None,
                         contract_type: str = None,
                         strike_price: float = None):
        """
        Get options chain.

        Args:
            underlying_ticker: Underlying stock ticker
            expiration_date: Filter by expiration (YYYY-MM-DD)
            contract_type: 'call' or 'put'
            strike_price: Filter by strike price
        """
        contracts = self.client.list_options_contracts(
            underlying_ticker=underlying_ticker,
            expiration_date=expiration_date,
            contract_type=contract_type,
            strike_price=strike_price
        )

        return [
            {
                "ticker": contract.ticker,
                "underlying_ticker": contract.underlying_ticker,
                "expiration_date": contract.expiration_date,
                "strike_price": contract.strike_price,
                "contract_type": contract.contract_type,
                "shares_per_contract": contract.shares_per_contract,
                "exercise_style": contract.exercise_style if hasattr(contract, 'exercise_style') else None
            }
            for contract in contracts
        ]

def setup_mcp_server():
    server = Server("polygon-mcp")
    polygon = PolygonMCPServer(os.getenv('POLYGON_API_KEY'))

    # Register tools
    server.register_tool(Tool(
        name="get_stock_bars",
        description="Get historical OHLCV data",
        handler=polygon.get_aggregates
    ))

    server.register_tool(Tool(
        name="get_market_news",
        description="Get news articles for tickers",
        handler=polygon.get_ticker_news
    ))

    server.register_tool(Tool(
        name="get_company_details",
        description="Get company information and metadata",
        handler=polygon.get_ticker_details
    ))

    server.register_tool(Tool(
        name="get_market_snapshot",
        description="Get current market data snapshot",
        handler=polygon.get_snapshot
    ))

    server.register_tool(Tool(
        name="get_options_data",
        description="Get options chain for underlying",
        handler=polygon.get_options_chain
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **News-Driven Trading**: Real-time news sentiment analysis
2. **Options Strategies**: Full chain data with Greeks
3. **Market Surveillance**: Monitor all tickers simultaneously
4. **Reference Data Management**: Company metadata, market calendars
5. **Multi-Asset Analytics**: Unified data for stocks, options, forex, crypto
6. **High-Frequency Trading**: Tick-level data access

---

## 6. FRED Economic Data MCP Server {#economic-data}

### Overview
Access to Federal Reserve Economic Data (FRED) for macroeconomic indicators and research.

**GitHub:** Multiple community implementations
**Website:** https://fred.stlouisfed.org
**Technology:** Python, REST API
**Data Coverage:** 800,000+ time series

### Financial Data Types Served

- **GDP**: Gross domestic product, growth rates
- **Employment**: Unemployment rate, jobless claims, payrolls
- **Inflation**: CPI, PCE, producer price index
- **Interest Rates**: Federal funds rate, treasury yields
- **Money Supply**: M1, M2, M3 aggregates
- **Trade**: Imports, exports, trade balance
- **Housing**: Home sales, construction, prices
- **Consumer Sentiment**: Michigan index, confidence
- **Manufacturing**: Industrial production, PMI
- **Corporate**: Profits, debt, credit spreads

### Protocol Operations Supported

```python
# FRED MCP Tools
{
  "data_retrieval": {
    "fetch_series_data": "Get time series observations",
    "search_series": "Search for series by keywords",
    "get_series_info": "Get series metadata",
    "get_series_categories": "Get category tree",
    "get_series_release": "Get release information"
  },

  "popular_series": {
    "GDP": "Gross Domestic Product",
    "UNRATE": "Unemployment Rate",
    "CPIAUCSL": "Consumer Price Index",
    "FEDFUNDS": "Federal Funds Rate",
    "DGS10": "10-Year Treasury Rate",
    "DEXUSEU": "USD/EUR Exchange Rate",
    "SP500": "S&P 500 Index",
    "VIXCLS": "VIX Volatility Index",
    "DCOILWTICO": "WTI Crude Oil Price",
    "GOLDAMGBD228NLBM": "Gold Price",
    "M2SL": "M2 Money Supply",
    "UMCSENT": "Consumer Sentiment",
    "INDPRO": "Industrial Production",
    "PAYEMS": "Total Nonfarm Payrolls",
    "HOUST": "Housing Starts"
  },

  "transformations": [
    "lin",    # Levels (no transformation)
    "chg",    # Change
    "ch1",    # Change from year ago
    "pch",    # Percent change
    "pc1",    # Percent change from year ago
    "pca",    # Compounded annual rate of change
    "cch",    # Continuously compounded rate of change
    "cca",    # Continuously compounded annual rate of change
    "log"     # Natural log
  ]
}
```

### Integration Points

1. **Macro Research**: Economic indicator analysis
2. **Factor Models**: Macro factors for return attribution
3. **Risk Management**: Recession indicators, volatility forecasts
4. **Currency Trading**: Interest rate differentials, economic releases
5. **Sector Rotation**: Economic cycle positioning
6. **Alternative Data**: Combine with market data for signals

### Implementation Example

```python
# FRED MCP Server
# File: fred_mcp_server.py

from mcp import Server, Tool
from fredapi import Fred
import pandas as pd
from datetime import datetime
import os

class FREDMCPServer:
    def __init__(self, api_key: str):
        self.fred = Fred(api_key=api_key)

    def fetch_series(self, series_id: str, observation_start: str = None,
                    observation_end: str = None, frequency: str = None,
                    aggregation_method: str = None,
                    transformation: str = None):
        """
        Fetch time series data.

        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE')
            observation_start: Start date (YYYY-MM-DD)
            observation_end: End date (YYYY-MM-DD)
            frequency: Data frequency (d, w, bw, m, q, sa, a)
            aggregation_method: How to aggregate (avg, sum, eop)
            transformation: Data transformation (lin, chg, pch, etc.)
        """
        series = self.fred.get_series(
            series_id,
            observation_start=observation_start,
            observation_end=observation_end,
            frequency=frequency,
            aggregation_method=aggregation_method,
            transformation=transformation
        )

        return {
            "series_id": series_id,
            "data": [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value) if pd.notna(value) else None
                }
                for date, value in series.items()
            ]
        }

    def search_series(self, search_text: str, limit: int = 100):
        """
        Search for series by keywords.

        Args:
            search_text: Search keywords
            limit: Maximum results
        """
        results = self.fred.search(search_text, limit=limit)

        return [
            {
                "id": row['id'],
                "title": row['title'],
                "frequency": row['frequency'],
                "units": row['units'],
                "seasonal_adjustment": row['seasonal_adjustment'],
                "last_updated": row['last_updated'],
                "popularity": row['popularity'],
                "notes": row['notes']
            }
            for _, row in results.iterrows()
        ]

    def get_series_info(self, series_id: str):
        """Get metadata for a series."""
        info = self.fred.get_series_info(series_id)

        return {
            "id": info['id'],
            "title": info['title'],
            "observation_start": info['observation_start'],
            "observation_end": info['observation_end'],
            "frequency": info['frequency'],
            "units": info['units'],
            "seasonal_adjustment": info['seasonal_adjustment'],
            "last_updated": info['last_updated'],
            "popularity": info['popularity'],
            "notes": info['notes']
        }

    def get_multiple_series(self, series_ids: list, observation_start: str = None,
                           observation_end: str = None):
        """
        Fetch multiple series at once.

        Args:
            series_ids: List of FRED series IDs
            observation_start: Start date
            observation_end: End date
        """
        data = {}
        for series_id in series_ids:
            series = self.fred.get_series(
                series_id,
                observation_start=observation_start,
                observation_end=observation_end
            )
            data[series_id] = [
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "value": float(value) if pd.notna(value) else None
                }
                for date, value in series.items()
            ]

        return data

    def get_economic_indicators_dashboard(self):
        """Get key economic indicators for dashboard."""
        indicators = {
            "GDP": "GDP",
            "Unemployment": "UNRATE",
            "Inflation_CPI": "CPIAUCSL",
            "Fed_Funds_Rate": "FEDFUNDS",
            "Treasury_10Y": "DGS10",
            "SP500": "SP500",
            "VIX": "VIXCLS",
            "Consumer_Sentiment": "UMCSENT",
            "Industrial_Production": "INDPRO",
            "Housing_Starts": "HOUST"
        }

        dashboard = {}
        for name, series_id in indicators.items():
            try:
                series = self.fred.get_series(series_id)
                latest = series.dropna().iloc[-1]
                dashboard[name] = {
                    "series_id": series_id,
                    "latest_value": float(latest),
                    "latest_date": series.dropna().index[-1].strftime("%Y-%m-%d"),
                    "previous_value": float(series.dropna().iloc[-2]),
                    "change": float(latest - series.dropna().iloc[-2])
                }
            except Exception as e:
                dashboard[name] = {"error": str(e)}

        return dashboard

# Predefined macro analysis functions
class MacroAnalysis:
    """Macroeconomic analysis utilities."""

    @staticmethod
    def calculate_yield_curve(fred_client: Fred):
        """Calculate treasury yield curve."""
        maturities = {
            "1M": "DGS1MO",
            "3M": "DGS3MO",
            "6M": "DGS6MO",
            "1Y": "DGS1",
            "2Y": "DGS2",
            "3Y": "DGS3",
            "5Y": "DGS5",
            "7Y": "DGS7",
            "10Y": "DGS10",
            "20Y": "DGS20",
            "30Y": "DGS30"
        }

        curve = {}
        for maturity, series_id in maturities.items():
            series = fred_client.get_series(series_id)
            latest = series.dropna().iloc[-1]
            curve[maturity] = float(latest)

        # Calculate 10Y-2Y spread (recession indicator)
        curve["10Y-2Y_Spread"] = curve["10Y"] - curve["2Y"]

        return curve

    @staticmethod
    def get_recession_indicators(fred_client: Fred):
        """Get leading recession indicators."""
        indicators = {}

        # Yield curve inversion
        dgs10 = fred_client.get_series("DGS10")
        dgs2 = fred_client.get_series("DGS2")
        spread = dgs10 - dgs2
        indicators["yield_curve_10y2y"] = float(spread.iloc[-1])
        indicators["yield_curve_inverted"] = spread.iloc[-1] < 0

        # Unemployment rate trend
        unrate = fred_client.get_series("UNRATE")
        indicators["unemployment_rate"] = float(unrate.iloc[-1])
        indicators["unemployment_3m_change"] = float(unrate.iloc[-1] - unrate.iloc[-4])

        # Leading economic index
        # lei = fred_client.get_series("USSLIND")
        # indicators["leading_index"] = float(lei.iloc[-1])

        # Consumer sentiment
        sentiment = fred_client.get_series("UMCSENT")
        indicators["consumer_sentiment"] = float(sentiment.iloc[-1])
        indicators["sentiment_change"] = float(sentiment.iloc[-1] - sentiment.iloc[-2])

        return indicators

def setup_mcp_server():
    server = Server("fred-economic-data-mcp")
    fred_server = FREDMCPServer(os.getenv('FRED_API_KEY'))

    # Register tools
    server.register_tool(Tool(
        name="fetch_economic_series",
        description="Fetch FRED time series data",
        handler=fred_server.fetch_series
    ))

    server.register_tool(Tool(
        name="search_economic_data",
        description="Search FRED database by keywords",
        handler=fred_server.search_series
    ))

    server.register_tool(Tool(
        name="get_series_metadata",
        description="Get series information and metadata",
        handler=fred_server.get_series_info
    ))

    server.register_tool(Tool(
        name="get_multiple_indicators",
        description="Fetch multiple economic indicators",
        handler=fred_server.get_multiple_series
    ))

    server.register_tool(Tool(
        name="get_economic_dashboard",
        description="Get key economic indicators summary",
        handler=fred_server.get_economic_indicators_dashboard
    ))

    # Macro analysis tools
    fred_client = Fred(api_key=os.getenv('FRED_API_KEY'))

    server.register_tool(Tool(
        name="get_yield_curve",
        description="Calculate treasury yield curve",
        handler=lambda: MacroAnalysis.calculate_yield_curve(fred_client)
    ))

    server.register_tool(Tool(
        name="get_recession_indicators",
        description="Get leading recession indicators",
        handler=lambda: MacroAnalysis.get_recession_indicators(fred_client)
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Macro Trading Strategies**: Trade based on economic cycles
2. **Recession Forecasting**: Monitor leading indicators
3. **Currency Trading**: Interest rate differentials
4. **Sector Rotation**: Position based on economic regime
5. **Risk Management**: Adjust portfolio based on macro conditions
6. **Factor Modeling**: Incorporate macro factors in quantitative models

---

## 7. InvestMCP - News & Sentiment Analysis Server {#news-sentiment}

### Overview
Comprehensive suite for real-time stock analysis, technical indicators, and financial news sentiment using FinBERT.

**GitHub:** https://github.com/arrpitk/InvestMCP
**Technology:** Python, FinBERT (Hugging Face), News APIs
**AI Model:** FinBERT for financial sentiment analysis

### Financial Data Types Served

- **News Articles**: Real-time financial news
- **Sentiment Scores**: Positive/negative/neutral with confidence
- **Technical Indicators**: 28+ indicators (RSI, MACD, Bollinger Bands)
- **Trading Signals**: Automated buy/sell signals
- **Market Data**: Real-time prices and quotes
- **Social Media**: Twitter/X sentiment (optional)

### Protocol Operations Supported

```python
# InvestMCP Tools
{
  "sentiment_analysis": {
    "analyze_news_sentiment": "FinBERT sentiment for news articles",
    "get_ticker_news": "Fetch news for specific ticker",
    "analyze_market_sentiment": "Overall market sentiment",
    "get_sentiment_history": "Historical sentiment trends"
  },

  "technical_analysis": {
    "indicators": [
      "RSI", "MACD", "Bollinger_Bands", "SMA", "EMA",
      "Stochastic", "ATR", "ADX", "CCI", "Williams_R",
      "OBV", "VWAP", "Ichimoku", "Parabolic_SAR"
    ],
    "pattern_recognition": [
      "Head_and_Shoulders", "Double_Top", "Double_Bottom",
      "Triangle", "Flag", "Wedge", "Channel"
    ]
  },

  "trading_signals": {
    "generate_signals": "Combined technical + sentiment signals",
    "signal_types": ["BUY", "SELL", "HOLD"],
    "confidence_levels": "0.0 to 1.0"
  },

  "sentiment_models": {
    "FinBERT": "Financial domain BERT model",
    "output_format": {
      "sentiment": "positive|negative|neutral",
      "confidence": "0.0 to 1.0",
      "scores": {
        "positive": "float",
        "negative": "float",
        "neutral": "float"
      }
    }
  }
}
```

### Integration Points

1. **News Aggregation**: Multiple news sources (Bloomberg, Reuters, WSJ)
2. **Sentiment Engine**: FinBERT model for financial text
3. **Technical Analysis**: Pre-calculated indicators
4. **Signal Generation**: Combined fundamental + technical + sentiment
5. **Real-Time Alerts**: News-driven trading signals
6. **Social Media**: Optional Twitter/Reddit sentiment

### Implementation Example

```python
# InvestMCP - News & Sentiment Server
# File: invest_mcp_server.py

from mcp import Server, Tool
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import requests
from datetime import datetime, timedelta
import numpy as np

class InvestMCPServer:
    def __init__(self, news_api_key: str):
        self.news_api_key = news_api_key

        # Load FinBERT model for sentiment analysis
        self.tokenizer = AutoTokenizer.from_pretrained(
            "ProsusAI/finbert"
        )
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "ProsusAI/finbert"
        )
        self.model.eval()

    def analyze_sentiment(self, text: str):
        """
        Analyze sentiment of financial text using FinBERT.

        Args:
            text: Financial news text or headline

        Returns:
            Sentiment classification with confidence scores
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # FinBERT labels: positive, negative, neutral
        labels = ["positive", "negative", "neutral"]
        scores = predictions[0].tolist()

        sentiment_idx = np.argmax(scores)
        sentiment = labels[sentiment_idx]
        confidence = scores[sentiment_idx]

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": scores[0],
                "negative": scores[1],
                "neutral": scores[2]
            }
        }

    def get_news_for_ticker(self, ticker: str, days: int = 7,
                           limit: int = 20):
        """
        Fetch recent news articles for a ticker.

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back
            limit: Maximum number of articles
        """
        # Using News API (example)
        url = "https://newsapi.org/v2/everything"

        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        params = {
            "q": f"{ticker} OR stock",
            "from": from_date,
            "sortBy": "publishedAt",
            "pageSize": limit,
            "apiKey": self.news_api_key,
            "language": "en",
            "domains": "bloomberg.com,reuters.com,cnbc.com,wsj.com,ft.com"
        }

        response = requests.get(url, params=params)
        articles = response.json().get("articles", [])

        return [
            {
                "title": article["title"],
                "description": article["description"],
                "url": article["url"],
                "published_at": article["publishedAt"],
                "source": article["source"]["name"],
                "author": article.get("author")
            }
            for article in articles
        ]

    def analyze_ticker_sentiment(self, ticker: str, days: int = 7):
        """
        Analyze overall sentiment for a ticker based on recent news.

        Args:
            ticker: Stock ticker
            days: Days to analyze
        """
        news = self.get_news_for_ticker(ticker, days)

        if not news:
            return {
                "ticker": ticker,
                "error": "No news found",
                "sentiment": None
            }

        sentiments = []
        analyzed_articles = []

        for article in news:
            text = f"{article['title']}. {article['description']}"
            if text and text != "None. None":
                sentiment = self.analyze_sentiment(text)
                sentiments.append(sentiment)
                analyzed_articles.append({
                    **article,
                    "sentiment": sentiment
                })

        if not sentiments:
            return {
                "ticker": ticker,
                "error": "No valid articles to analyze",
                "sentiment": None
            }

        # Calculate aggregate sentiment
        avg_positive = np.mean([s["scores"]["positive"] for s in sentiments])
        avg_negative = np.mean([s["scores"]["negative"] for s in sentiments])
        avg_neutral = np.mean([s["scores"]["neutral"] for s in sentiments])

        overall_sentiment = "positive" if avg_positive > max(avg_negative, avg_neutral) else \
                           "negative" if avg_negative > avg_neutral else "neutral"

        return {
            "ticker": ticker,
            "period": f"{days} days",
            "articles_analyzed": len(sentiments),
            "overall_sentiment": overall_sentiment,
            "sentiment_scores": {
                "positive": float(avg_positive),
                "negative": float(avg_negative),
                "neutral": float(avg_neutral)
            },
            "sentiment_distribution": {
                "positive": sum(1 for s in sentiments if s["sentiment"] == "positive"),
                "negative": sum(1 for s in sentiments if s["sentiment"] == "negative"),
                "neutral": sum(1 for s in sentiments if s["sentiment"] == "neutral")
            },
            "articles": analyzed_articles
        }

    def generate_sentiment_signal(self, ticker: str, days: int = 7,
                                  threshold: float = 0.6):
        """
        Generate trading signal based on sentiment analysis.

        Args:
            ticker: Stock ticker
            days: Days to analyze
            threshold: Confidence threshold for signal (0.0 to 1.0)
        """
        sentiment_data = self.analyze_ticker_sentiment(ticker, days)

        if sentiment_data.get("error"):
            return {
                "ticker": ticker,
                "signal": "HOLD",
                "reason": sentiment_data["error"],
                "confidence": 0.0
            }

        scores = sentiment_data["sentiment_scores"]
        overall = sentiment_data["overall_sentiment"]

        # Generate signal
        if overall == "positive" and scores["positive"] >= threshold:
            signal = "BUY"
            confidence = scores["positive"]
            reason = f"Strong positive sentiment ({scores['positive']:.2%})"
        elif overall == "negative" and scores["negative"] >= threshold:
            signal = "SELL"
            confidence = scores["negative"]
            reason = f"Strong negative sentiment ({scores['negative']:.2%})"
        else:
            signal = "HOLD"
            confidence = scores["neutral"]
            reason = f"Neutral or weak sentiment"

        return {
            "ticker": ticker,
            "signal": signal,
            "confidence": float(confidence),
            "reason": reason,
            "sentiment_data": sentiment_data
        }

    def analyze_earnings_sentiment(self, ticker: str,
                                   earnings_date: str = None):
        """
        Analyze sentiment around earnings announcements.

        Args:
            ticker: Stock ticker
            earnings_date: Date of earnings (YYYY-MM-DD), defaults to recent
        """
        # Get news around earnings date
        if earnings_date:
            date_obj = datetime.strptime(earnings_date, "%Y-%m-%d")
        else:
            date_obj = datetime.now()

        # Look 3 days before and after earnings
        news = []
        for offset in range(-3, 4):
            day_news = self.get_news_for_ticker(
                ticker,
                days=1,
                limit=10
            )
            news.extend(day_news)

        # Analyze sentiment trend
        daily_sentiment = {}
        for article in news:
            date = article["published_at"][:10]
            if date not in daily_sentiment:
                daily_sentiment[date] = []

            text = f"{article['title']}. {article['description']}"
            sentiment = self.analyze_sentiment(text)
            daily_sentiment[date].append(sentiment)

        # Calculate daily average
        trend = {}
        for date, sentiments in sorted(daily_sentiment.items()):
            avg_positive = np.mean([s["scores"]["positive"] for s in sentiments])
            avg_negative = np.mean([s["scores"]["negative"] for s in sentiments])
            trend[date] = {
                "positive": float(avg_positive),
                "negative": float(avg_negative),
                "article_count": len(sentiments)
            }

        return {
            "ticker": ticker,
            "earnings_date": earnings_date or "recent",
            "sentiment_trend": trend
        }

def setup_mcp_server():
    import os
    server = Server("invest-mcp-sentiment")
    invest = InvestMCPServer(os.getenv('NEWS_API_KEY'))

    # Register tools
    server.register_tool(Tool(
        name="analyze_text_sentiment",
        description="Analyze sentiment of financial text using FinBERT",
        handler=invest.analyze_sentiment
    ))

    server.register_tool(Tool(
        name="get_ticker_news",
        description="Fetch recent news for ticker",
        handler=invest.get_news_for_ticker
    ))

    server.register_tool(Tool(
        name="analyze_ticker_sentiment",
        description="Analyze overall sentiment from news",
        handler=invest.analyze_ticker_sentiment
    ))

    server.register_tool(Tool(
        name="generate_sentiment_signal",
        description="Generate buy/sell signal from sentiment",
        handler=invest.generate_sentiment_signal
    ))

    server.register_tool(Tool(
        name="analyze_earnings_sentiment",
        description="Analyze sentiment around earnings",
        handler=invest.analyze_earnings_sentiment
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **News-Driven Trading**: Generate signals from breaking news
2. **Earnings Trading**: Sentiment analysis around earnings
3. **Event-Driven Strategies**: React to major announcements
4. **Risk Management**: Monitor negative sentiment spikes
5. **Alpha Generation**: Sentiment as a factor in quantitative models
6. **Social Trading**: Community sentiment analysis

---

## 8. Binance Cryptocurrency MCP Server {#cryptocurrency}

### Overview
Real-time cryptocurrency market data and trading access for Binance exchange.

**GitHub:** https://github.com/snjyor/binance-mcp
**Technology:** Python, Binance API, WebSocket
**Data Coverage:** 1,000+ crypto pairs

### Financial Data Types Served

- **Spot Markets**: BTC, ETH, altcoins, stablecoins
- **Futures**: Perpetual and delivery contracts
- **Options**: Crypto options (if available)
- **Order Book**: Real-time bids/asks
- **Trade History**: Recent trades
- **Account Data**: Balances, positions, P&L
- **Funding Rates**: Perpetual contract funding
- **Liquidations**: Liquidation events

### Protocol Operations Supported

```javascript
// Binance MCP Tools
{
  "market_data": {
    "get_ticker_price": "Current price for symbol",
    "get_order_book": "Bid/ask depth",
    "get_recent_trades": "Last trades",
    "get_klines": "OHLCV candlestick data",
    "get_24hr_stats": "24h price change stats",
    "get_ticker_price_all": "All symbol prices"
  },

  "account_management": {
    "get_account_info": "Balances and permissions",
    "get_open_orders": "Current open orders",
    "get_all_orders": "Order history",
    "get_my_trades": "Trade history"
  },

  "trading": {
    "create_order": "Place new order",
    "cancel_order": "Cancel existing order",
    "cancel_all_orders": "Cancel all orders for symbol",
    "order_types": ["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT"]
  },

  "futures_specific": {
    "get_funding_rate": "Current funding rate",
    "get_position_risk": "Current positions",
    "change_leverage": "Adjust leverage",
    "change_margin_type": "ISOLATED or CROSSED"
  },

  "websocket_streams": {
    "trade_stream": "Real-time trades",
    "kline_stream": "Real-time candlesticks",
    "depth_stream": "Order book updates",
    "ticker_stream": "24h ticker updates",
    "user_data_stream": "Account updates"
  }
}
```

### Integration Points

1. **Crypto Trading**: Direct access to Binance markets
2. **Real-Time Data**: WebSocket streaming for live prices
3. **Account Management**: Balance tracking, P&L calculation
4. **Futures Trading**: Leverage, funding rates, liquidations
5. **DeFi Integration**: On-chain data combined with CEX data
6. **Arbitrage**: Cross-exchange price comparison

### Implementation Example

```python
# Binance MCP Server
# File: binance_mcp_server.py

from mcp import Server, Tool
from binance.client import Client
from binance.enums import *
import os

class BinanceMCPServer:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        if testnet:
            self.client = Client(
                api_key, api_secret,
                testnet=True
            )
        else:
            self.client = Client(api_key, api_secret)

    def get_ticker_price(self, symbol: str = None):
        """Get current price for symbol(s)."""
        if symbol:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return {
                "symbol": ticker["symbol"],
                "price": float(ticker["price"])
            }
        else:
            tickers = self.client.get_all_tickers()
            return [
                {
                    "symbol": t["symbol"],
                    "price": float(t["price"])
                }
                for t in tickers
            ]

    def get_order_book(self, symbol: str, limit: int = 100):
        """Get order book depth."""
        depth = self.client.get_order_book(symbol=symbol, limit=limit)

        return {
            "symbol": symbol,
            "bids": [
                {"price": float(bid[0]), "quantity": float(bid[1])}
                for bid in depth["bids"]
            ],
            "asks": [
                {"price": float(ask[0]), "quantity": float(ask[1])}
                for ask in depth["asks"]
            ],
            "last_update_id": depth["lastUpdateId"]
        }

    def get_klines(self, symbol: str, interval: str, limit: int = 500,
                  start_time: int = None, end_time: int = None):
        """
        Get candlestick data.

        Args:
            symbol: Trading pair
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, 1w, 1M)
            limit: Number of klines (max 1000)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
        """
        klines = self.client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_time,
            endTime=end_time
        )

        return [
            {
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
                "quote_volume": float(k[7]),
                "trades": k[8],
                "taker_buy_base": float(k[9]),
                "taker_buy_quote": float(k[10])
            }
            for k in klines
        ]

    def get_account_info(self):
        """Get account information."""
        account = self.client.get_account()

        return {
            "maker_commission": account["makerCommission"],
            "taker_commission": account["takerCommission"],
            "can_trade": account["canTrade"],
            "can_withdraw": account["canWithdraw"],
            "can_deposit": account["canDeposit"],
            "balances": [
                {
                    "asset": balance["asset"],
                    "free": float(balance["free"]),
                    "locked": float(balance["locked"])
                }
                for balance in account["balances"]
                if float(balance["free"]) > 0 or float(balance["locked"]) > 0
            ]
        }

    def create_market_order(self, symbol: str, side: str, quantity: float):
        """
        Place market order.

        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
        """
        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_MARKET,
            quantity=quantity
        )

        return self._serialize_order(order)

    def create_limit_order(self, symbol: str, side: str, quantity: float,
                          price: float, time_in_force: str = "GTC"):
        """
        Place limit order.

        Args:
            symbol: Trading pair
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: GTC, IOC, FOK
        """
        order = self.client.create_order(
            symbol=symbol,
            side=side,
            type=ORDER_TYPE_LIMIT,
            quantity=quantity,
            price=price,
            timeInForce=time_in_force
        )

        return self._serialize_order(order)

    def cancel_order(self, symbol: str, order_id: int = None,
                    orig_client_order_id: str = None):
        """Cancel an order."""
        result = self.client.cancel_order(
            symbol=symbol,
            orderId=order_id,
            origClientOrderId=orig_client_order_id
        )

        return self._serialize_order(result)

    def get_open_orders(self, symbol: str = None):
        """Get all open orders."""
        orders = self.client.get_open_orders(symbol=symbol)

        return [self._serialize_order(order) for order in orders]

    def _serialize_order(self, order):
        """Convert order to dictionary."""
        return {
            "symbol": order["symbol"],
            "order_id": order["orderId"],
            "client_order_id": order.get("clientOrderId"),
            "price": float(order.get("price", 0)),
            "orig_qty": float(order.get("origQty", 0)),
            "executed_qty": float(order.get("executedQty", 0)),
            "cumulative_quote_qty": float(order.get("cumulativeQuoteQty", 0)),
            "status": order.get("status"),
            "time_in_force": order.get("timeInForce"),
            "type": order.get("type"),
            "side": order.get("side"),
            "stop_price": float(order.get("stopPrice", 0)),
            "time": order.get("time"),
            "update_time": order.get("updateTime")
        }

def setup_mcp_server():
    server = Server("binance-crypto-mcp")
    binance = BinanceMCPServer(
        os.getenv('BINANCE_API_KEY'),
        os.getenv('BINANCE_API_SECRET'),
        testnet=True  # Use testnet for safety
    )

    # Market data tools
    server.register_tool(Tool(
        name="get_crypto_price",
        description="Get current cryptocurrency price",
        handler=binance.get_ticker_price
    ))

    server.register_tool(Tool(
        name="get_orderbook",
        description="Get order book depth",
        handler=binance.get_order_book
    ))

    server.register_tool(Tool(
        name="get_candlestick_data",
        description="Get OHLCV candlestick data",
        handler=binance.get_klines
    ))

    # Account tools
    server.register_tool(Tool(
        name="get_account",
        description="Get account balances and info",
        handler=binance.get_account_info
    ))

    # Trading tools
    server.register_tool(Tool(
        name="place_market_order",
        description="Execute market order",
        handler=binance.create_market_order
    ))

    server.register_tool(Tool(
        name="place_limit_order",
        description="Execute limit order",
        handler=binance.create_limit_order
    ))

    server.register_tool(Tool(
        name="cancel_crypto_order",
        description="Cancel an order",
        handler=binance.cancel_order
    ))

    server.register_tool(Tool(
        name="get_open_crypto_orders",
        description="Get all open orders",
        handler=binance.get_open_orders
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Cryptocurrency Trading**: Automated crypto trading strategies
2. **Market Making**: Provide liquidity on Binance
3. **Arbitrage**: Cross-exchange price differences
4. **DeFi Integration**: Combine CEX and DEX data
5. **Portfolio Management**: Track crypto holdings
6. **Futures Trading**: Leverage trading with funding rate arbitrage

---

## 9. Yahoo Finance MCP Server

### Overview
Free, no-authentication stock market data server with comprehensive coverage.

**GitHub:** Multiple community implementations
**Technology:** Python, yfinance library
**Data Coverage:** Global stocks, ETFs, indices, forex, crypto

### Financial Data Types Served

- **Stocks**: Global equities
- **ETFs**: Exchange-traded funds
- **Indices**: Market indices worldwide
- **Forex**: Currency pairs
- **Cryptocurrencies**: Major digital assets
- **Mutual Funds**: Fund data
- **Commodities**: Futures contracts
- **Financial Statements**: Income, balance sheet, cash flow
- **Options**: Options chains

### Protocol Operations Supported

```python
# Yahoo Finance MCP Tools
{
  "market_data": {
    "get_historical_data": "Historical OHLCV",
    "get_current_price": "Real-time quote (15min delay)",
    "get_info": "Company information",
    "get_financials": "Financial statements",
    "get_dividends": "Dividend history",
    "get_splits": "Stock split history",
    "get_options": "Options chain",
    "get_recommendations": "Analyst recommendations",
    "get_calendar": "Earnings calendar"
  },

  "intervals": [
    "1m", "2m", "5m", "15m", "30m", "60m", "90m",
    "1h", "1d", "5d", "1wk", "1mo", "3mo"
  ],

  "periods": [
    "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y",
    "5y", "10y", "ytd", "max"
  ]
}
```

### Implementation Example

```python
# Yahoo Finance MCP Server
# File: yahoo_finance_mcp_server.py

from mcp import Server, Tool
import yfinance as yf
from datetime import datetime, timedelta

class YahooFinanceMCPServer:
    def __init__(self):
        pass

    def get_historical_data(self, ticker: str, period: str = "1mo",
                           interval: str = "1d", start: str = None,
                           end: str = None):
        """
        Get historical price data.

        Args:
            ticker: Stock ticker
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            start: Start date (YYYY-MM-DD)
            end: End date (YYYY-MM-DD)
        """
        stock = yf.Ticker(ticker)

        if start and end:
            hist = stock.history(start=start, end=end, interval=interval)
        else:
            hist = stock.history(period=period, interval=interval)

        return {
            "ticker": ticker,
            "data": [
                {
                    "date": index.strftime("%Y-%m-%d %H:%M:%S"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                    "dividends": float(row.get("Dividends", 0)),
                    "stock_splits": float(row.get("Stock Splits", 0))
                }
                for index, row in hist.iterrows()
            ]
        }

    def get_stock_info(self, ticker: str):
        """Get comprehensive stock information."""
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "company_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "website": info.get("website"),
            "description": info.get("longBusinessSummary"),
            "market_cap": info.get("marketCap"),
            "enterprise_value": info.get("enterpriseValue"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "price_to_book": info.get("priceToBook"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "52week_high": info.get("fiftyTwoWeekHigh"),
            "52week_low": info.get("fiftyTwoWeekLow"),
            "50day_average": info.get("fiftyDayAverage"),
            "200day_average": info.get("twoHundredDayAverage"),
            "volume": info.get("volume"),
            "average_volume": info.get("averageVolume"),
            "shares_outstanding": info.get("sharesOutstanding"),
            "float_shares": info.get("floatShares"),
            "employees": info.get("fullTimeEmployees")
        }

    def get_financials(self, ticker: str, statement_type: str = "income"):
        """
        Get financial statements.

        Args:
            ticker: Stock ticker
            statement_type: 'income', 'balance', or 'cashflow'
        """
        stock = yf.Ticker(ticker)

        if statement_type == "income":
            df = stock.financials
        elif statement_type == "balance":
            df = stock.balance_sheet
        elif statement_type == "cashflow":
            df = stock.cashflow
        else:
            return {"error": "Invalid statement type"}

        return {
            "ticker": ticker,
            "statement_type": statement_type,
            "data": df.to_dict()
        }

    def get_options_chain(self, ticker: str, expiration: str = None):
        """
        Get options chain.

        Args:
            ticker: Stock ticker
            expiration: Expiration date (YYYY-MM-DD), defaults to nearest
        """
        stock = yf.Ticker(ticker)

        if expiration:
            options = stock.option_chain(expiration)
        else:
            # Get nearest expiration
            expirations = stock.options
            if not expirations:
                return {"error": "No options available"}
            options = stock.option_chain(expirations[0])

        return {
            "ticker": ticker,
            "expiration": expiration or stock.options[0] if stock.options else None,
            "calls": options.calls.to_dict('records'),
            "puts": options.puts.to_dict('records')
        }

    def get_dividends(self, ticker: str):
        """Get dividend history."""
        stock = yf.Ticker(ticker)
        dividends = stock.dividends

        return {
            "ticker": ticker,
            "dividends": [
                {
                    "date": index.strftime("%Y-%m-%d"),
                    "amount": float(value)
                }
                for index, value in dividends.items()
            ]
        }

    def get_recommendations(self, ticker: str):
        """Get analyst recommendations."""
        stock = yf.Ticker(ticker)
        recommendations = stock.recommendations

        if recommendations is None or recommendations.empty:
            return {"ticker": ticker, "recommendations": []}

        return {
            "ticker": ticker,
            "recommendations": recommendations.to_dict('records')
        }

def setup_mcp_server():
    server = Server("yahoo-finance-mcp")
    yf_server = YahooFinanceMCPServer()

    server.register_tool(Tool(
        name="get_historical_prices",
        description="Get historical stock prices",
        handler=yf_server.get_historical_data
    ))

    server.register_tool(Tool(
        name="get_company_info",
        description="Get company information and metrics",
        handler=yf_server.get_stock_info
    ))

    server.register_tool(Tool(
        name="get_financial_statements",
        description="Get income, balance sheet, or cash flow",
        handler=yf_server.get_financials
    ))

    server.register_tool(Tool(
        name="get_options",
        description="Get options chain data",
        handler=yf_server.get_options_chain
    ))

    server.register_tool(Tool(
        name="get_dividend_history",
        description="Get historical dividends",
        handler=yf_server.get_dividends
    ))

    server.register_tool(Tool(
        name="get_analyst_recommendations",
        description="Get analyst recommendations",
        handler=yf_server.get_recommendations
    ))

    return server

if __name__ == "__main__":
    server = setup_mcp_server()
    server.run()
```

### Use Cases for Trading Systems

1. **Prototype Development**: Free data for testing strategies
2. **Personal Trading**: Individual investor portfolios
3. **Educational Projects**: Learning algorithmic trading
4. **Fundamental Analysis**: Financial statement screening
5. **Dividend Strategies**: Dividend tracking and forecasting
6. **Options Strategies**: Options chain analysis

---

## 10. Financial Datasets MCP Server

### Overview
Professional-grade financial statements and market data API via MCP.

**GitHub:** https://github.com/financial-datasets/mcp-server
**Technology:** Python, REST API
**Data Coverage:** US equities, fundamentals, market data

### Financial Data Types Served

- **Income Statements**: Revenue, earnings, margins
- **Balance Sheets**: Assets, liabilities, equity
- **Cash Flow Statements**: Operating, investing, financing
- **Stock Prices**: Historical and real-time prices
- **Market News**: Financial news articles
- **Company Metrics**: P/E, P/B, ROE, debt ratios
- **Insider Trading**: Insider transactions
- **Institutional Holdings**: 13F filings

### Protocol Operations Supported

```python
# Financial Datasets MCP Tools
{
  "fundamental_data": {
    "get_income_statement": "Income statement (annual/quarterly)",
    "get_balance_sheet": "Balance sheet (annual/quarterly)",
    "get_cash_flow": "Cash flow statement (annual/quarterly)",
    "get_financial_ratios": "Key financial ratios",
    "get_key_metrics": "Performance metrics"
  },

  "market_data": {
    "get_stock_prices": "Historical prices",
    "get_real_time_quote": "Current price",
    "get_intraday_prices": "Intraday bars"
  },

  "company_data": {
    "get_company_profile": "Company information",
    "get_insider_trading": "Insider transactions",
    "get_institutional_holdings": "13F holdings",
    "get_sec_filings": "SEC filing links"
  },

  "screening": {
    "screen_stocks": "Filter stocks by criteria",
    "get_market_movers": "Top gainers/losers",
    "get_most_active": "Most traded stocks"
  }
}
```

### Use Cases for Trading Systems

1. **Fundamental Analysis**: Deep dive into financial health
2. **Value Investing**: Screen undervalued stocks
3. **Insider Trading Tracking**: Monitor insider activity
4. **Institutional Flow**: Track smart money
5. **Financial Modeling**: Build DCF and valuation models
6. **Earnings Analysis**: Analyze earnings trends

---

## Implementation Guide {#implementation-guide}

### General Setup Steps

#### 1. Install MCP SDK

```bash
# Python
pip install mcp

# Node.js
npm install @modelcontextprotocol/sdk
```

#### 2. Configure API Keys

Create `.env` file:

```bash
# Market Data
ALPHA_VANTAGE_API_KEY=your_key_here
TWELVE_DATA_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here
YAHOO_FINANCE_KEY=not_required

# Trading
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here

# Economic Data
FRED_API_KEY=your_key_here

# News & Sentiment
NEWS_API_KEY=your_key_here

# Backtesting
QC_USER_ID=your_user_id
QC_API_TOKEN=your_token

# Financial Datasets
FINANCIAL_DATASETS_API_KEY=your_key_here
```

#### 3. MCP Client Configuration

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "alpha-vantage": {
      "command": "python",
      "args": ["/path/to/alpha_vantage_mcp_server.py"],
      "env": {
        "ALPHA_VANTAGE_API_KEY": "your_key"
      }
    },
    "alpaca-trading": {
      "command": "python",
      "args": ["/path/to/alpaca_mcp_server.py"],
      "env": {
        "ALPACA_API_KEY": "your_key",
        "ALPACA_SECRET_KEY": "your_secret"
      }
    },
    "fred-economic": {
      "command": "python",
      "args": ["/path/to/fred_mcp_server.py"],
      "env": {
        "FRED_API_KEY": "your_key"
      }
    }
  }
}
```

#### 4. Server Discovery and Testing

```python
# test_mcp_servers.py
from mcp import Client
import asyncio

async def test_server(server_url):
    async with Client(server_url) as client:
        # List available tools
        tools = await client.list_tools()
        print("Available tools:", tools)

        # List resources
        resources = await client.list_resources()
        print("Available resources:", resources)

        # Test a tool
        result = await client.call_tool(
            "get_stock_daily_data",
            arguments={"symbol": "AAPL"}
        )
        print("Test result:", result)

asyncio.run(test_server("http://localhost:3000"))
```

---

## Integration Patterns {#integration-patterns}

### Pattern 1: Multi-Source Data Aggregation

```python
# Aggregate data from multiple MCP servers
class MultiSourceDataAggregator:
    def __init__(self):
        self.alpha_vantage = AlphaVantageMCPServer(AV_KEY)
        self.twelve_data = TwelveDataMCPServer(TD_KEY)
        self.polygon = PolygonMCPServer(POLYGON_KEY)

    async def get_comprehensive_data(self, symbol):
        # Parallel data fetch
        av_data = await self.alpha_vantage.get_time_series_daily(symbol)
        td_data = await self.twelve_data.get_time_series(symbol)
        polygon_data = await self.polygon.get_aggregates(symbol)

        # Merge and deduplicate
        merged = self.merge_time_series([av_data, td_data, polygon_data])
        return merged
```

### Pattern 2: News-Driven Trading Workflow

```python
# Sentiment-based trading decision
class SentimentTradingStrategy:
    def __init__(self):
        self.sentiment = InvestMCPServer(NEWS_KEY)
        self.trading = AlpacaMCPServer(ALPACA_KEY, ALPACA_SECRET)
        self.data = AlphaVantageMCPServer(AV_KEY)

    async def execute_strategy(self, ticker):
        # Get sentiment signal
        signal = await self.sentiment.generate_sentiment_signal(ticker)

        # Get technical confirmation
        rsi = await self.data.get_technical_indicator(ticker, "RSI")

        # Execute trade if aligned
        if signal["signal"] == "BUY" and rsi < 30:
            await self.trading.submit_market_order(ticker, 100, "buy")
        elif signal["signal"] == "SELL" and rsi > 70:
            await self.trading.close_position(ticker)
```

### Pattern 3: Economic Data Integration

```python
# Macro-driven portfolio allocation
class MacroAllocationStrategy:
    def __init__(self):
        self.fred = FREDMCPServer(FRED_KEY)
        self.trading = AlpacaMCPServer(ALPACA_KEY, ALPACA_SECRET)

    async def adjust_allocation(self):
        # Get recession indicators
        indicators = await self.fred.get_recession_indicators()

        # Adjust portfolio based on macro regime
        if indicators["yield_curve_inverted"]:
            # Defensive: increase bonds, reduce equities
            await self.trading.submit_market_order("TLT", 100, "buy")
            await self.trading.close_position("SPY", percentage=0.5)
        else:
            # Risk-on: increase equities
            await self.trading.submit_market_order("SPY", 50, "buy")
```

---

## Security Considerations {#security}

### API Key Management

1. **Never hardcode API keys** in source code
2. **Use environment variables** or secure vaults
3. **Rotate keys regularly** (every 90 days)
4. **Use read-only keys** for market data
5. **Separate paper/live trading keys**

### Network Security

1. **Use HTTPS** for all API calls
2. **Implement rate limiting** to prevent abuse
3. **Validate all inputs** to prevent injection
4. **Monitor for suspicious activity**

### Trading Security

1. **Paper trading first** before live deployment
2. **Set position size limits** to control risk
3. **Implement kill switches** for runaway algorithms
4. **Log all trades** for audit trail
5. **Monitor P&L** in real-time

### Data Privacy

1. **Encrypt sensitive data** at rest and in transit
2. **Comply with regulations** (GDPR, CCPA)
3. **Audit access logs** regularly
4. **Minimize data retention** to necessary period

---

## Conclusion

This document provides comprehensive specifications for 10+ MCP servers covering:

✅ **Market Data**: Alpha Vantage, Twelve Data, Polygon, Yahoo Finance
✅ **Trading**: Alpaca, Binance
✅ **Backtesting**: QuantConnect
✅ **Economic Data**: FRED
✅ **Sentiment**: InvestMCP
✅ **Fundamentals**: Financial Datasets

Each server provides standardized MCP interfaces for AI-driven financial applications, enabling seamless integration of market data, trading execution, risk management, and analytics.

For production deployment, consider:
- **Data redundancy**: Use multiple data sources
- **Failover mechanisms**: Handle API outages gracefully
- **Performance optimization**: Cache frequently accessed data
- **Cost management**: Monitor API usage and costs
- **Compliance**: Ensure regulatory compliance for your jurisdiction

---

**Document Version:** 1.0
**Last Updated:** November 18, 2025
**Maintained By:** Financial Apps Architecture Team
