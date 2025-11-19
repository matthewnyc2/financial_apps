# Mean Reversion Trading Strategies

## Overview

Mean reversion is a fundamental concept in quantitative finance that assumes asset prices tend to revert to their average over time. This document covers five major mean reversion trading strategies with mathematical foundations and practical implementations.

---

## 1. BOLLINGER BANDS

### Theory

Bollinger Bands are volatility-based bands placed above and below a moving average.

**Mathematical Formula:**

```
MA(t) = SMA(Price, period)
σ(t) = Standard Deviation(Price, period)
Upper Band = MA(t) + (k × σ(t))
Lower Band = MA(t) - (k × σ(t))
```

Where:
- `MA(t)` = Simple Moving Average at time t
- `σ(t)` = Standard deviation of prices over the period
- `k` = Number of standard deviations (typically 2)
- `period` = Window length (typically 20 days)

**Signal Generation:**

- **BUY Signal**: Price closes below the Lower Band (oversold condition)
- **SELL Signal**: Price closes above the Upper Band (overbought condition)
- **%B Indicator**: `%B = (Price - Lower Band) / (Upper Band - Lower Band)`
  - %B = 0: Price at lower band
  - %B = 1: Price at upper band
  - %B = 0.5: Price at middle band

### Trading Logic

1. Monitor the %B value for extreme readings
2. Buy when price bounces off lower band (oversold, %B < 0.2)
3. Sell when price bounces off upper band (overbought, %B > 0.8)
4. Use band width to assess volatility regime changes

### Example

```
Price: $100
20-day SMA: $101
20-day Std Dev: $2

Upper Band = 101 + (2 × 2) = $105
Lower Band = 101 - (2 × 2) = $97

If Price = $95 (below lower band) → BUY SIGNAL
If Price = $106 (above upper band) → SELL SIGNAL
```

### Advantages
- Simple to implement
- Volatility-adaptive
- Clear visual identification of extremes

### Limitations
- Trending markets generate false signals
- Doesn't account for fundamental changes
- Lag in moving average calculation

---

## 2. RSI (Relative Strength Index)

### Theory

RSI measures the magnitude of recent price changes to evaluate overbought/oversold conditions on a scale of 0-100.

**Mathematical Formula:**

```
ΔPrice = Price(t) - Price(t-1)

Gains(t) = ΔPrice if ΔPrice > 0, else 0
Losses(t) = |ΔPrice| if ΔPrice < 0, else 0

EMA_Gains = EMA(Gains, period)
EMA_Losses = EMA(Losses, period)

RS = EMA_Gains / EMA_Losses
RSI = 100 - (100 / (1 + RS))
```

Where:
- `period` = RSI calculation period (typically 14)
- EMA = Exponential Moving Average
- RS = Relative Strength ratio

**Signal Thresholds:**

- RSI > 70: Overbought (potential sell signal)
- RSI < 30: Oversold (potential buy signal)
- RSI 30-70: Neutral zone

### Trading Logic

1. Enter long position when RSI drops below 30 (oversold)
2. Enter short position when RSI rises above 70 (overbought)
3. Close position when RSI returns to 50 (midpoint)
4. Confirm signals with price action patterns

### Example

```
14-day Average Gain: $0.45
14-day Average Loss: $0.30

RS = 0.45 / 0.30 = 1.5
RSI = 100 - (100 / (1 + 1.5)) = 100 - 40 = 60

If RSI > 70: Overbought, consider selling
If RSI < 30: Oversold, consider buying
```

### Advantages
- Normalized 0-100 scale for easy interpretation
- Identifies extremes well in range-bound markets
- Popular and widely understood

### Limitations
- Oscillates during strong trends
- High RSI doesn't always mean price will fall
- Period selection affects sensitivity

### Divergence Strategy

- **Bullish Divergence**: Price makes lower low, RSI makes higher low → Buy signal
- **Bearish Divergence**: Price makes higher high, RSI makes lower high → Sell signal

---

## 3. Z-SCORE METHOD

### Theory

Z-score measures how many standard deviations a value is from the mean. For mean reversion, extreme Z-scores indicate prices far from their average.

**Mathematical Formula:**

```
Mean = MA(Price, period)
Std Dev = StdDev(Price, period)

Z-Score = (Price - Mean) / Std Dev
```

**Interpretation:**

- Z-Score = 0: Price at mean
- Z-Score > 2: Price is 2 standard deviations above mean (95% confidence)
- Z-Score < -2: Price is 2 standard deviations below mean (95% confidence)

### Trading Logic

```
Entry Threshold = 2.0
Exit Threshold = 1.0

BUY Signal:  Z-Score < -2.0 (significantly oversold)
SELL Signal: Z-Score > 2.0  (significantly overbought)
EXIT Signal: |Z-Score| < 1.0 (return toward mean)
```

### Example

```
Current Price: $98
20-day MA: $100
20-day Std Dev: $2

Z-Score = (98 - 100) / 2 = -1.0

This indicates the price is 1 standard deviation below the mean.
For mean reversion entry, we'd typically wait for Z-Score < -2.0

If Z-Score = -2.5: Strong BUY signal (deeply oversold)
If Z-Score = +2.5: Strong SELL signal (deeply overbought)
```

### Advantages
- Statistically rigorous
- Clear quantitative thresholds
- Works well in stationary price regimes

### Limitations
- Assumes normal distribution (doesn't account for fat tails)
- Sensitive to period selection
- Struggles in trending markets

---

## 4. HALF-LIFE CALCULATION

### Theory

Half-life measures how quickly a mean-reverting series returns to its long-term mean. It's crucial for identifying whether an asset is truly mean-reverting and estimating expected reversion time.

**Mathematical Formula:**

For an AR(1) process: `X(t) = μ + φ(X(t-1) - μ) + ε(t)`

```
Regression: X(t) = constant + φ × X(t-1) + error

Half-Life = ln(2) / |ln(φ)|
          = 0.693 / |ln(φ)|
```

Where:
- `φ (phi)` = Autocorrelation coefficient from AR(1) regression
- `ln(2)` ≈ 0.693 (natural logarithm of 2)
- If φ < 0.5: Half-life < period, asset reverts quickly
- If φ > 0.9: Half-life > 10×period, weak mean reversion

### Interpretation

```
Half-Life = 5 days  → Asset reverts to mean in ~5 days
Half-Life = 30 days → Asset reverts to mean in ~30 days
Half-Life = 250 days → Weak mean reversion (almost random walk)
```

### Example Calculation

```
Regression over 252-day window:
Price(t) = 100 + 0.95 × Price(t-1) + error

φ = 0.95
Half-Life = ln(2) / |ln(0.95)|
          = 0.693 / 0.0513
          = 13.5 trading days
```

### Alternative Formula (Speed of Reversion)

```
For model: dX = λ(μ - X)dt + σdW

λ = -ln(φ)  (mean reversion speed)
Half-Life = ln(2) / λ
```

### Trading Applications

1. **Pairs Trading**: Select pairs with short half-life
2. **Position Sizing**: Longer half-life → smaller position size
3. **Exit Timing**: Use half-life to set profit-taking targets
4. **Strategy Selection**: Only trade assets with HLF < 252 days

### Advantages
- Quantifies reversion speed
- Helps select best mean-reverting assets
- Informs optimal holding periods

### Limitations
- Assumes AR(1) process (may not hold)
- Changes over time (requires rolling calculation)
- Assumes linear mean reversion

---

## 5. ORNSTEIN-UHLENBECK (OU) PROCESS

### Theory

The Ornstein-Uhlenbeck process is a continuous-time model that explicitly captures mean-reverting behavior. It's widely used in quantitative finance for modeling interest rates, spreads, and mean-reverting assets.

**Continuous-Time Model:**

```
dX(t) = θ(μ - X(t))dt + σ dW(t)
```

Where:
- `X(t)` = Price or value at time t
- `θ (theta)` = Mean reversion speed (kappa) [units: 1/time]
- `μ (mu)` = Long-term mean
- `σ (sigma)` = Volatility of shocks
- `dW(t)` = Wiener process (Brownian motion increment)

**Discrete-Time Approximation (Euler Scheme):**

```
X(t+Δt) = X(t) + θ(μ - X(t))Δt + σ√Δt × Z(t)

Where Z(t) ~ N(0,1) (standard normal random variable)
```

**Parameter Estimation:**

Using OLS regression:

```
X(t) = X(t-1) + θ(μ - X(t-1)) + ε(t)

Rewrite as:
ΔX(t) = -θ×X(t-1) + θμ + ε(t)

OLS yields:
θ = -ln(coefficient of X(t-1))
μ = intercept / θ
σ = std(residuals)
```

### Key Parameters

| Parameter | Interpretation | Example |
|-----------|-----------------|---------|
| θ | Mean reversion speed | 0.1 = 10% convergence per period |
| μ | Long-term equilibrium | $100 for a stock |
| σ | Volatility/noise | $2 for $100 stock |

### Expected Half-Life

```
Half-Life = ln(2) / θ
```

**Example:**

```
If θ = 0.05 (5% mean reversion per day):
Half-Life = 0.693 / 0.05 = 13.86 days
```

### Trading Strategy (OU-Based)

```
1. Estimate μ, θ, σ from historical data
2. Calculate normalized distance: Z = (X - μ) / σ
3. BUY when Z < -1.5  (1.5σ below mean)
4. SELL when Z > 1.5  (1.5σ above mean)
5. EXIT when Z crosses 0 (returns to mean)
```

### Example Simulation

```
Parameters:
  θ = 0.10    (10% mean reversion speed)
  μ = $100    (target price)
  σ = $2      (volatility)
  X(0) = $95  (starting price)

Step 1: Expected reversion amount = 0.10 × ($100 - $95) = $0.50
Step 2: Add random shock: ε = 0.02 (from N(0, $2²))
Step 3: X(1) = $95 + $0.50 + $0.02 = $95.52

After 1 day: Price moves toward mean by $0.50
After 14 days (half-life): Price reverts to ~$97.50
```

### Advantages
- Theoretically sound for continuous trading
- Captures mean-reverting dynamics explicitly
- Allows for stochastic simulation and forecasting

### Limitations
- Parameter estimation requires sufficient data
- Assumes constant parameters (may change over time)
- Not ideal for discrete trading with transaction costs

---

## BONUS: PAIRS TRADING WITH Z-SCORE

### Theory

Pairs trading exploits mean reversion of the spread between two correlated assets.

**Mathematical Framework:**

```
Spread = Price1 - β × Price2

where β = Cov(Price1, Price2) / Var(Price2)

Spread_Z = (Spread - Mean(Spread)) / StdDev(Spread)
```

### Trading Logic

```
Long Pair (Buy 1, Short 2):   Spread_Z > 2.0
Short Pair (Short 1, Buy 2):  Spread_Z < -2.0
Exit:                         Spread_Z ≈ 0
```

### Advantages
- Market-neutral (hedged) strategy
- Reduces systematic market risk
- Profits from relative pricing inefficiencies

---

## STRATEGY COMPARISON TABLE

| Strategy | Period | Entry Signal | Exit Signal | Best Market | Complexity |
|----------|--------|--------------|------------|-------------|-----------|
| Bollinger Bands | 20 | Price < LBand | Price > MBand | Range-bound | Low |
| RSI | 14 | RSI < 30 | RSI > 50 | Range-bound | Low |
| Z-Score | 20 | Z < -2.0 | Z = 0 | Stationary | Low |
| Half-Life | 252 | HLF < 30 days | N/A (analysis) | Any | Medium |
| OU Process | 100 | Z < -1.5 | Z = 0 | Mean-reverting | High |

---

## PRACTICAL IMPLEMENTATION GUIDE

### Step 1: Data Preparation

```python
import pandas as pd
import numpy as np

# Load price data
df = pd.read_csv('prices.csv')
prices = df['close'].values
```

### Step 2: Calculate Indicators

```python
from mean_reversion import MeanReversionStrategies

mr = MeanReversionStrategies(df)

# Calculate Bollinger Bands
bb_result = mr.bollinger_bands(period=20, num_std=2.0)

# Calculate RSI
rsi_result = mr.rsi_strategy(period=14)

# Calculate Z-Score
zscore_result = mr.zscore_strategy(period=20)

# Calculate Half-Life
hl_result = mr.calculate_half_life(window=252)

# Calculate OU parameters
ou_result = mr.ornstein_uhlenbeck_analysis(window=252)
```

### Step 3: Generate Trading Signals

```python
# Extract signals
bb_signals = bb_result['signals']
rsi_signals = rsi_result['signals']
zscore_signals = zscore_result['signals']
ou_signals = ou_result['signals']

# Combine signals (voting system)
combined_signal = (bb_signals + rsi_signals + zscore_signals + ou_signals) / 4
```

### Step 4: Backtest Strategy

```python
# Calculate returns
returns = np.diff(np.log(prices))

# Strategy returns (assuming 1x leverage)
strategy_returns = np.sign(combined_signal[:-1]) * returns

# Calculate metrics
total_return = np.sum(strategy_returns)
sharpe_ratio = np.mean(strategy_returns) / np.std(strategy_returns) * np.sqrt(252)
max_drawdown = calculate_max_drawdown(strategy_returns)
```

---

## RISK MANAGEMENT

### Position Sizing

```
Position Size = Account Risk / Indicator Risk

Example:
- Account Risk: 1% of account
- BB Band Width: $5
- Position Size: 0.01 × Account / 5
```

### Stop Loss Placement

```
For Bollinger Bands:
  Stop Loss = Mid Band (SMA) + std_dev

For Z-Score:
  Stop Loss = Mean + 3 × StdDev
```

### Profit Targets

```
For Bollinger Bands:
  Target = Mid Band (mean reversion point)

For Z-Score:
  Target = Mean (Z = 0)

For OU Process:
  Target = μ (long-term mean)
```

---

## MARKET REGIMES

### When Mean Reversion Works Well

1. **Range-Bound Markets**: Prices oscillate between support/resistance
2. **Commodity Markets**: Reversion around production costs
3. **FX Markets**: PPP-driven reversion
4. **Pairs/Spreads**: Correlated assets drifting apart
5. **Short Time Horizons**: Minutes to days

### When Mean Reversion Fails

1. **Strong Trends**: Clear directional bias
2. **Low Liquidity**: Wide spreads
3. **Regime Changes**: Structural breaks
4. **High Volatility**: Whipsaw risk
5. **Single Stocks**: Company-specific news

---

## CONCLUSION

Mean reversion strategies form a powerful toolkit for quantitative traders:

- **Bollinger Bands**: Visual, volatility-adaptive approach
- **RSI**: Momentum extremes identification
- **Z-Score**: Statistically rigorous entries
- **Half-Life**: Analytical framework for asset selection
- **OU Process**: Sophisticated continuous-time modeling

**Best Practice**: Combine multiple methods (ensemble approach) to reduce false signals and improve robustness.

---

## References

1. Bollinger, J. (1992). "Bollinger on Bollinger Bands"
2. Wilder, J. W. (1978). "New Concepts in Technical Trading Systems"
3. Vasicek, O. (1977). "An Equilibrium Characterization of the Term Structure"
4. Ornstein, L., & Uhlenbeck, G. (1930). "On the theory of Brownian motion"
5. Vidyamurthy, G. (2004). "Pairs Trading: Quantitative Methods and Analysis"

---

**File Location**: `/home/user/financial_apps/quants/methods/mean_reversion.md`
**Code Implementation**: `/home/user/financial_apps/quants/programs/mean_reversion.py`
