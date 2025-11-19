# Recommended Scripts & Tools for Quantitative Trading

A curated list of 10+ utility scripts and tools for quantitative trading, pre-market analysis, and portfolio management.

---

## 1. **yfinance**
- **Purpose:** Download historical and real-time stock market data from Yahoo Finance
- **Technology:** Python library
- **Use Case:** Data download, historical OHLCV data retrieval for backtesting and analysis
- **Automation Potential:** HIGH - Threaded downloads, easy integration in automated pipelines for daily data collection

---

## 2. **TA-Lib (Technical Analysis Library)**
- **Purpose:** Calculate 200+ technical indicators (RSI, MACD, Bollinger Bands, ADX, Stochastic)
- **Technology:** C/C++ core with Python/R/Ruby wrappers, Cython-optimized
- **Use Case:** Pre-market scans, indicator calculations for signal generation, data cleaning/normalization
- **Automation Potential:** VERY HIGH - 2-4x faster than alternatives, ideal for real-time pre-market scanning systems

---

## 3. **Backtrader**
- **Purpose:** Feature-rich framework for backtesting and live trading strategies
- **Technology:** Python framework with extensive documentation
- **Use Case:** Strategy backtesting, performance analysis, trade journaling, portfolio simulation
- **Automation Potential:** VERY HIGH - Supports multiple data formats, indicators, analyzers; real-time trading support

---

## 4. **Zipline**
- **Purpose:** Event-driven backtesting engine for algorithmic trading strategies
- **Technology:** Python, originally used by Quantopian, Apache 2.0 licensed
- **Use Case:** Strategy backtesting, performance analysis, machine learning integration (scikit-learn)
- **Automation Potential:** HIGH - Pandas integration, extensive algorithm library, supports ML tools

---

## 5. **VectorBT**
- **Purpose:** Ultra-fast vectorized backtesting and portfolio analysis (1M simulations in 20 seconds)
- **Technology:** Python with NumPy, Pandas, Numba acceleration
- **Use Case:** Large-scale backtesting, parameter optimization, portfolio modeling, volatility analysis
- **Automation Potential:** EXTREME - 70-100ms for 1M orders (Apple M1); excellent for batch analysis and regime detection

---

## 6. **CCXT (CryptoCurrency eXchange Trading)**
- **Purpose:** Unified API for 100+ cryptocurrency exchanges; download and trading
- **Technology:** Python library with REST/WebSocket APIs
- **Use Case:** Crypto market data download, pre-market scans for crypto assets, algorithmic trading
- **Automation Potential:** VERY HIGH - Supports camelcase/underscore notation, private API access, real-time streaming

---

## 7. **QSTrader**
- **Purpose:** Backtesting framework with live trading and risk management support
- **Technology:** Python framework
- **Use Case:** Position sizing, risk monitoring, performance analysis, strategy backtesting with drawdown tracking
- **Automation Potential:** VERY HIGH - Built-in risk management, position sizing, automated trade execution

---

## 8. **pandas-datareader**
- **Purpose:** Download market data from multiple sources (Yahoo, Google, FRED, IEX, Crypto)
- **Technology:** Python library built on Pandas
- **Use Case:** Multi-asset data downloads, correlation analysis across different sources, data cleaning
- **Automation Potential:** HIGH - Supports multiple data providers, flexible for portfolio-level data aggregation

---

## 9. **PyAlgoTrade**
- **Purpose:** Backtesting library with NumPy/SciPy integration
- **Technology:** Python framework with scientific library support
- **Use Case:** Strategy backtesting, performance analysis, indicator development
- **Automation Potential:** HIGH - Complete documentation, NumPy integration, suitable for research workflows

---

## 10. **TradesViz**
- **Purpose:** Trade journal with 600+ statistical metrics and correlation analysis
- **Technology:** Web-based platform with API
- **Use Case:** Trade journaling, performance analysis, correlation analysis (trade factors), equity curve tracking
- **Automation Potential:** HIGH - Automated trade imports, correlation reporting, multi-instrument analysis

---

## 11. **QuantConnect**
- **Purpose:** Cloud-based algorithmic trading platform with datasets marketplace
- **Technology:** Python/C# with cloud infrastructure
- **Use Case:** Backtesting, live trading, data downloads, performance analysis, multi-asset correlation studies
- **Automation Potential:** VERY HIGH - Cloud execution, 180+ engineers maintained, extensive datasets, live trading

---

## 12. **QuantRocket**
- **Purpose:** Data aggregation and strategy platform using TimescaleDB
- **Technology:** Python framework with time-series database backend
- **Use Case:** Live market data aggregation, pre-market scans, strategy backtesting (Moonshot/Zipline)
- **Automation Potential:** VERY HIGH - Optimized database for tick data, real-time aggregation, custom scripts

---

## Focus Areas Coverage

| Area | Recommended Tools |
|------|-------------------|
| **Data Download** | yfinance, pandas-datareader, CCXT, QuantRocket |
| **Data Cleaning** | TA-Lib, Pandas, Numpy |
| **Pre-Market Scans** | TA-Lib, VectorBT, QuantRocket |
| **Position Sizing** | QSTrader, Backtrader, QuantConnect |
| **Risk Monitoring** | QSTrader, TradesViz, QuantConnect |
| **Performance Analysis** | VectorBT, Zipline, TradesViz, Backtrader |
| **Trade Journaling** | TradesViz, Backtrader |
| **Correlation Analysis** | TradesViz, Pandas, VectorBT |
| **Volatility Calculations** | TA-Lib, VectorBT, NumPy |
| **Regime Detection** | VectorBT, QuantRocket, Zipline (with HMM) |

---

## Implementation Stack Recommendation

**Minimal Setup (Light):**
- Data: yfinance
- Indicators: TA-Lib
- Backtesting: VectorBT
- Journaling: TradesViz

**Advanced Setup (Production):**
- Data: QuantRocket + CCXT
- Indicators: TA-Lib
- Backtesting: VectorBT + Zipline
- Risk Management: QSTrader
- Analysis: TradesViz + Custom Pandas
- Automation: Native Python cron/scheduler

**Enterprise Setup:**
- Platform: QuantConnect
- Data: QuantConnect Datasets + QuantRocket
- Backtesting: VectorBT (speed) + Zipline (research)
- Execution: QuantConnect or IB-insync
- Analysis: TradesViz + Custom analytics

---

## Notes

- All Python tools are open-source except QuantConnect (freemium) and TradesViz (freemium)
- VectorBT offers exceptional speed for large-scale testing and regime analysis
- TA-Lib is essential for any pre-market scanning system requiring real-time calculations
- Combine multiple tools: data from yfinance/CCXT → TA-Lib indicators → VectorBT backtests → TradesViz journaling
- Consider IB-insync for Interactive Brokers real-time data and live execution
