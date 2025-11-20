# Quantitative Trading Analysis Suite

Comprehensive collection of quantitative trading strategies, analysis methods, and historical market data.

## 📁 Directory Structure

```
apps/quants/
├── programs/           # 20 Python programs implementing trading strategies
├── methods/           # 20 Markdown files with theory and formulas
├── data/              # Historical stock market data (10 years)
├── models/            # Trained models and saved parameters
├── backtests/         # Backtesting results and reports
└── results/           # Analysis outputs and visualizations
```

## 🔬 Research Areas Covered (20 Programs)

### 1. Statistical Arbitrage (`statistical_arbitrage.py`)
- Pairs trading with cointegration
- Basket arbitrage
- Index arbitrage
- Statistical mean reversion

### 2. Mean Reversion (`mean_reversion.py`)
- Bollinger Bands strategy
- RSI oversold/overbought
- Z-score based entries
- Ornstein-Uhlenbeck process

### 3. Momentum & Trend Following (`momentum.py`)
- Dual/Triple moving average crossovers
- MACD with histogram
- ADX trend strength
- Turtle Trading system

### 4. Pairs Trading (`pairs_trading.py`)
- Engle-Granger cointegration test
- Johansen test
- Spread calculation and z-score
- Half-life estimation

### 5. Machine Learning (`ml_trading.py`)
- Random Forest classifier
- XGBoost regressor
- Feature engineering
- Walk-forward validation

### 6. Volatility Modeling (`volatility_models.py`)
- GARCH/EGARCH/GJR-GARCH
- Realized volatility
- Volatility forecasting
- VIX-based strategies

### 7. Factor Models (`factor_models.py`)
- Fama-French 3/5 factor models
- Factor construction (SMB, HML, RMW, CMA, MOM)
- Factor regression analysis
- Alpha and beta estimation

### 8. Portfolio Optimization (`portfolio_optimization.py`)
- Mean-Variance (Markowitz)
- Black-Litterman model
- Risk Parity
- Hierarchical Risk Parity
- Kelly Criterion

### 9. Options Pricing (`options_pricing.py`)
- Black-Scholes pricing
- Greeks (Delta, Gamma, Theta, Vega, Rho)
- Implied volatility solver
- Binomial tree pricing
- Monte Carlo simulation

### 10. High-Frequency Trading (`hft_strategies.py`)
- Bid-ask spread analysis
- Order book imbalance
- Microstructure features
- VWAP/TWAP execution

### 11. Market Microstructure (`market_microstructure.py`)
- Kyle's lambda
- Amihud illiquidity ratio
- Price impact estimation
- Roll's bid-ask estimator

### 12. Sentiment Analysis (`sentiment_analysis.py`)
- News sentiment scoring
- Social media sentiment
- FinBERT integration
- Aggregate sentiment indices

### 13. Regime Detection (`regime_detection.py`)
- Hidden Markov Models
- Viterbi algorithm
- Change point detection (PELT, CUSUM)
- Volatility regime classification

### 14. Risk Management (`risk_management.py`)
- Value at Risk (VaR) - 6 methods
- CVaR/Expected Shortfall
- Stress testing
- Scenario analysis
- Correlation analysis

### 15. Event-Driven Strategies (`event_driven.py`)
- Earnings momentum
- Post-earnings announcement drift
- Dividend capture
- M&A arbitrage
- Event study analysis

### 16. Calendar Effects (`calendar_effects.py`)
- Day-of-week effect
- January effect
- Turn-of-month strategy
- Holiday effect
- Seasonality decomposition

### 17. Technical Patterns (`technical_patterns.py`)
- Candlestick pattern recognition
- Support/resistance identification
- Fibonacci retracements
- Chart pattern detection

### 18. Order Flow Analysis (`order_flow.py`)
- VPIN calculation
- Order book imbalance
- Buy/sell pressure metrics
- Market maker spread optimization
- Inventory risk management

### 19. Deep Learning (`deep_learning.py`)
- LSTM price prediction
- GRU architecture
- Temporal attention mechanism
- CNN for pattern recognition
- Multi-task learning

### 20. Reinforcement Learning (`reinforcement_learning.py`)
- Trading environment (Gym-compatible)
- Q-learning trader
- Deep Q-Network (DQN)
- Actor-Critic methods
- Reward shaping

## 📊 Historical Data

### Data Coverage
- **S&P 500**: All 500 constituents + index (10 years daily)
- **NASDAQ 100**: Top 100 tech stocks + index (10 years daily)
- **Russell 2000**: Sample small-cap stocks + index (10 years daily)
- **Dow Jones 30**: All 30 components + index (10 years daily)
- **VIX**: Volatility index (10 years daily)

### Data Downloader

Download all historical data:

```bash
# Download all indices with constituents
python programs/data_downloader.py --indices all --period 10y --constituents

# Download specific index
python programs/data_downloader.py --indices SP500 --period 10y --constituents

# Download indices only (no constituents)
python programs/data_downloader.py --indices SP500 NASDAQ100 --period 10y

# Download with limit on number of stocks
python programs/data_downloader.py --indices SP500 --period 10y --constituents --max-stocks 50
```

### Data Format

All data is saved as CSV files with columns:
- Date (index)
- Open
- High
- Low
- Close
- Volume
- Dividends
- Stock Splits
- Ticker

## 🚀 Quick Start

### Installation

```bash
cd apps/quants/
pip install -r requirements.txt
```

### Download Data

```bash
# Download all historical data (this may take 30-60 minutes)
python programs/data_downloader.py --indices all --period 10y --constituents
```

### Run Example Strategy

```python
import pandas as pd
from programs.momentum import MomentumStrategy

# Load data
df = pd.read_csv('data/stocks/sp500/AAPL_10y_1d.csv', index_col=0, parse_dates=True)

# Initialize strategy
strategy = MomentumStrategy()

# Generate signals
signals = strategy.dual_ma_crossover(df['Close'], fast=20, slow=50)

# Backtest
results = strategy.backtest(df, signals)
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

## 📖 Documentation

Each program has a corresponding documentation file in `methods/`:

- `methods/statistical_arbitrage.md` - Theory and implementation details
- `methods/mean_reversion.md` - Mathematical formulas and examples
- ... (20 total)

All documentation includes:
- Mathematical formulas
- Trading logic
- Parameter recommendations
- Risk considerations
- Code examples
- References

## 🧪 Testing & Validation

All programs include:
- Working example code at the bottom
- Synthetic data generation for testing
- Statistical significance tests
- Performance metrics (Sharpe, Sortino, Calmar ratios)

## ⚠️ Disclaimer

This software is for educational and research purposes only. All trading strategies involve risk of financial loss. Past performance does not guarantee future results. Always perform thorough backtesting and understand the risks before deploying any strategy with real capital.

## 📚 References

Each method file includes academic references and research papers. Key sources include:

- Fama & French (1992, 2015) - Factor models
- Black & Scholes (1973) - Options pricing
- Kyle (1985) - Market microstructure
- Engle (1982), Bollerslev (1986) - GARCH models
- And 50+ additional academic papers

## 🔧 Development

### Adding New Strategies

1. Create program file: `programs/new_strategy.py`
2. Create documentation: `methods/new_strategy.md`
3. Follow existing pattern with mathematical formulas in docstrings
4. Include working example at the bottom
5. Add to this README

### Code Style

- Use type hints
- Include comprehensive docstrings
- Add mathematical formulas as comments
- Provide working examples
- Handle edge cases gracefully

## 📊 Performance Expectations

Based on academic literature and industry benchmarks:

- **Statistical Arbitrage**: Sharpe 1.5-3.0 (pairs trading)
- **Momentum**: Sharpe 0.5-1.5 (trend following)
- **Mean Reversion**: Sharpe 1.0-2.0 (short-term)
- **Factor Models**: Sharpe 0.8-1.2 (long-only)
- **Options Strategies**: Highly variable, theta decay vs. gamma
- **HFT**: Sharpe 3.0+ but requires low latency

All strategies degrade when:
- Transaction costs increase
- Market regimes change
- Liquidity decreases
- Competition increases

## 🎯 Use Cases

### Pre-Market Trading
- Overnight gap analysis
- News sentiment before open
- Options pricing for earnings
- Futures-based predictions

### Quantitative Research
- Factor exposure analysis
- Strategy correlation studies
- Risk decomposition
- Performance attribution

### Risk Management
- Portfolio VaR calculation
- Stress testing scenarios
- Correlation monitoring
- Regime detection

### Algorithmic Execution
- VWAP/TWAP algorithms
- Smart order routing
- Market making strategies
- Liquidity analysis

## 🔗 Integration

All programs are designed to work together:

```python
from programs import (
    regime_detection,
    volatility_models,
    portfolio_optimization,
    risk_management
)

# Detect current market regime
regime = regime_detection.detect_current_regime(prices)

# Adjust volatility forecast based on regime
vol_forecast = volatility_models.forecast_volatility(returns, regime)

# Optimize portfolio with regime-adjusted risk
weights = portfolio_optimization.optimize(returns, vol_forecast)

# Calculate risk metrics
var = risk_management.calculate_var(weights, returns)
```

## 📈 Future Enhancements

- [ ] Real-time data streaming
- [ ] Live trading integration (Alpaca, Interactive Brokers)
- [ ] Web dashboard for monitoring
- [ ] Automated backtesting framework
- [ ] Parameter optimization
- [ ] Multi-asset support (crypto, forex, futures)
- [ ] Cloud deployment (AWS, GCP)
- [ ] Distributed computing for large-scale backtests

---

**Created**: 2025-11-19
**Total Programs**: 20
**Total Documentation**: 20 files
**Lines of Code**: 15,000+
**Data Coverage**: 10 years, 500+ stocks
