# Opening Hour Stock Predictor - System Architecture

## Overview

A comprehensive, multi-threaded stock prediction system designed to identify stocks most likely to gain/lose value during the first hour of trading.

## System Components

### 1. Data Acquisition Layer (`data/`)
- **Multi-source API integration**: Finnhub, Alpaca, yfinance, Alpha Vantage
- **Async download** with rate limiting (500 req/min)
- **Redis caching** with 1-hour TTL
- **Historical data**: 2+ years of minute-level OHLCV
- **News aggregation**: Google News RSS, Alpha Vantage, yfinance
- **Pre-market data**: Extended hours trading information

### 2. Quantitative Analysis Engine (`analysis/quantitative.py`)
**Stage 1: Technical Indicators (Vectorized)**
- RSI (7, 14 periods)
- MACD (8-17-9 for intraday)
- Bollinger Bands (20, 2)
- ATR for volatility
- VWAP (anchored to market open)
- Volume indicators (OBV, volume spikes)

**Stage 2: Statistical Tests**
- Mean reversion analysis (ADF test)
- Volatility modeling (GARCH forecasts)
- Opening Range Breakout patterns
- Gap analysis and classification

**Stage 3: Market Microstructure**
- Bid-ask spread analysis (when available)
- Order flow imbalance
- Pre-market volume analysis

### 3. News Sentiment Analysis (`analysis/sentiment.py`)
- **FinBERT** for financial text (63.3% accuracy)
- **VADER** for real-time fallback (339x faster)
- **Multi-source aggregation**: News (70%), Reddit (20%), Twitter (10%)
- **Temporal decay**: Exponential with λ=0.3
- **Importance weighting**: Earnings (1.0), M&A (1.0), General (0.4)
- **TF-IDF deduplication** at 85% threshold

### 4. Machine Learning Prediction (`models/`)
**Model Ensemble:**
- **XGBoost** (baseline, 60-70% directional accuracy)
- **BiLSTM** (temporal dependencies, 94%+ training accuracy)
- **CNN-LSTM-Attention** (hybrid spatial-temporal)
- **Stacking meta-learner** (Logistic Regression)

**Features (50+ total):**
- Price-based: OHLCV, returns, gaps
- Technical: 15 indicators
- Sentiment: 7 sentiment scores
- Temporal: Day of week, time of day
- Market: SPY correlation, sector strength

**Validation:**
- Walk-forward optimization (252/63/21 windows)
- Out-of-sample testing (30% holdout)
- Monte Carlo simulation (1000 runs)
- PBO (Probability of Backtest Overfitting) < 0.25

### 5. Multi-Stage Filtering Pipeline (`analysis/filtering.py`)

```
3000 stocks (entire market)
    ↓ Stage 1: Basic Filters (1ms)
1500 stocks (liquidity + price + volume)
    ↓ Stage 2: Outlier Detection (100ms)
1000 stocks (MCD, Mahalanobis distance)
    ↓ Stage 3: Factor Scoring (500ms)
200 stocks (Fama-French, clustering)
    ↓ Stage 4: ML Ranking (200ms)
50 stocks (XGBoost + ensemble)
    ↓ Stage 5: Portfolio Optimization (50ms)
10-20 stocks (Max Sharpe, Ledoit-Wolf)
```

**Scoring Methodology:**
- Value (30%): Book-to-market, P/E
- Momentum (30%): 3-month, 6-month returns
- Quality (20%): ROE, profit margins
- Volatility (20%): Low-vol factor

### 6. Results Storage (`data/database.py`)
**TimescaleDB Schema:**
- `predictions` - All strategy predictions with features
- `actual_results` - Trade outcomes with execution details
- `strategy_performance` - Aggregated metrics by period
- `equity_curves` - Daily equity tracking
- `prediction_accuracy` - Direction and return accuracy
- `backtests` - Historical test results

### 7. Command-Line Interface (`cli.py`)

**Main Menu:**
```
1. Predict Opening Hour Gainers (Top 10)
2. Predict Opening Hour Losers (Top 10)
3. Analyze Specific Stock
4. Run Backtest (Historical Validation)
5. Compare Predictions vs Actuals
6. View Performance Metrics
7. Update Models (Retrain)
8. Download Latest Data
9. Configuration Settings
0. Exit
```

### 8. Backtesting Engine (`models/backtest.py`)
- **VectorBT** for speed (1M simulations in 20s)
- **Walk-forward optimization**
- **Transaction costs**: $0.005/share
- **Slippage modeling**: 0.1% for opening hour volatility
- **Monte Carlo risk analysis**
- **Performance metrics**: Sharpe, Sortino, Calmar, max drawdown

## Data Flow

```
┌─────────────────────┐
│  User Input (CLI)   │
└──────────┬──────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  1. Data Acquisition (Async, Multi-threaded)    │
│     - Download 1000+ stocks (50 workers)        │
│     - Fetch news (parallel)                     │
│     - Check cache first (Redis)                 │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  2. Quantitative Analysis (Multiprocessing)     │
│     - Calculate 50+ indicators (8 workers)      │
│     - Vectorized NumPy operations               │
│     - GPU acceleration (optional)               │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  3. Sentiment Analysis (Parallel)               │
│     - FinBERT scoring (batch processing)        │
│     - Multi-source aggregation                  │
│     - Temporal decay weighting                  │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  4. Multi-Stage Filtering                       │
│     - Stage 1: Basic filters (O(n))             │
│     - Stage 2: Outliers (O(n·p²))               │
│     - Stage 3: Factor scoring (O(n·k))          │
│     - Stage 4: ML ranking (O(n·log n))          │
│     - Stage 5: Portfolio opt (O(p³))            │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  5. ML Prediction (Ensemble)                    │
│     - XGBoost probability                       │
│     - LSTM forecast                             │
│     - Stacking meta-model                       │
│     - Confidence intervals                      │
└──────────┬──────────────────────────────────────┘
           │
           v
┌─────────────────────────────────────────────────┐
│  6. Results & Storage                           │
│     - Top 10 gainers/losers                     │
│     - Store predictions (TimescaleDB)           │
│     - Display with reasons                      │
│     - Export to CSV/JSON                        │
└─────────────────────────────────────────────────┘
```

## Performance Targets

### Speed (1000 stocks):
- Data download: 20-60 seconds
- Quantitative analysis: 30-90 seconds
- Sentiment analysis: 10-30 seconds
- ML prediction: 5-15 seconds
- **Total: 1-3 minutes**

### Accuracy:
- Directional accuracy: 55-65% (above random 50%)
- Sharpe ratio: >1.5
- Win rate: >55%
- Max drawdown: <25%

### Memory:
- Peak usage: <4GB for 1000 stocks
- Streaming mode for 5000+ stocks

## Technology Stack

**Core:**
- Python 3.10+
- NumPy, Pandas for data processing
- scikit-learn for ML

**Data Sources:**
- Finnhub (primary)
- Alpaca (intraday data)
- yfinance (backup)
- Alpha Vantage (news)

**ML/DL:**
- XGBoost, LightGBM
- TensorFlow/Keras (LSTM)
- Transformers (FinBERT)

**Storage:**
- PostgreSQL + TimescaleDB
- Redis (caching)

**Performance:**
- asyncio + aiohttp (async I/O)
- multiprocessing (CPU-bound)
- Numba (JIT compilation)
- CuPy (GPU, optional)

**Visualization:**
- Plotly for charts
- Rich for CLI formatting
- tabulate for tables

## Configuration

**config.yaml:**
```yaml
data:
  sources: [finnhub, alpaca, yfinance]
  api_keys_file: .env
  cache_ttl: 3600
  max_download_workers: 50

analysis:
  technical_indicators: [rsi, macd, bbands, atr, vwap, obv]
  lookback_periods: [7, 14, 20, 50, 200]
  max_compute_workers: 8

sentiment:
  model: finbert
  fallback: vader
  sources: [news, reddit]
  decay_lambda: 0.3

ml:
  models: [xgboost, lstm, ensemble]
  walk_forward_train: 252
  walk_forward_test: 63
  retrain_frequency: 21

filtering:
  min_market_cap: 500000000
  min_volume: 1000000
  min_price: 5
  max_price: 1000

prediction:
  top_n_gainers: 10
  top_n_losers: 10
  confidence_threshold: 0.6

backtesting:
  transaction_cost: 0.005
  slippage: 0.001
  monte_carlo_runs: 1000
```

## Academic Foundation

Based on 50+ peer-reviewed papers including:
- Gao, Han, Li, Zhou (2018) - Market Intraday Momentum
- Bailey & López de Prado (2015) - Probability of Backtest Overfitting
- Harvey, Liu, Zhu (2016) - Factor Zoo analysis
- Zarattini et al. (2024) - ORB profitability study
- Lo, Mamaysky, Wang - Foundations of Technical Analysis

## Deployment

**Development:**
```bash
python main.py --mode predict
```

**Production:**
```bash
# Daily cron job (pre-market)
0 8 * * 1-5 cd /app && python main.py --mode predict --output predictions.csv

# Post-market comparison
0 17 * * 1-5 cd /app && python main.py --mode validate
```

## Future Enhancements

1. **Real-time execution** via Alpaca/IBKR APIs
2. **Deep reinforcement learning** (PPO, DQN)
3. **Alternative data** (satellite imagery, credit card data)
4. **Options pricing** integration
5. **Multi-asset** support (crypto, forex, futures)
6. **Web dashboard** with real-time updates
7. **Mobile alerts** via Telegram/SMS
