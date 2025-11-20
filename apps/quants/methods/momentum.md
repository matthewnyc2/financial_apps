# Momentum and Trend Following Strategies

## Overview

Momentum trading strategies exploit the tendency of prices to continue moving in the same direction, while trend following strategies identify and profit from established market trends. This document outlines five key approaches implemented in the momentum trading system.

---

## 1. Dual Moving Average Crossover

### Strategy Overview
The simplest and most widely used trend-following approach. Uses two moving averages of different periods to identify trend changes.

### How It Works
- **Short-term MA**: Faster, more responsive to recent prices (default: 20 periods)
- **Long-term MA**: Slower, reflects longer-term trend (default: 50 periods)

### Trading Signals

**Buy Signal:** When short-term MA crosses **above** long-term MA
```
Condition: MA_short(t-1) ≤ MA_long(t-1) AND MA_short(t) > MA_long(t)
```

**Sell Signal:** When short-term MA crosses **below** long-term MA
```
Condition: MA_short(t-1) ≥ MA_long(t-1) AND MA_short(t) < MA_long(t)
```

### Formula

```
MA_short(t) = Σ(price[i]) / N_short  where i ∈ [t-N_short+1, t]
MA_long(t)  = Σ(price[i]) / N_long   where i ∈ [t-N_long+1, t]
```

### Advantages
- Simple to understand and implement
- Fast execution with minimal lag
- Effective in trending markets
- Low false signal rate when properly tuned

### Disadvantages
- Whipsaws in sideways/ranging markets
- Late entries and exits
- Requires proper period selection

### Recommended Parameters
- Short Period: 20-30 days
- Long Period: 50-200 days
- Best for: Intraday to weekly timeframes

---

## 2. Triple Moving Average System

### Strategy Overview
An enhanced version using three moving averages for stronger trend confirmation. Eliminates false signals by requiring alignment across all three MAs.

### How It Works
- **Fast MA**: 20-period (most responsive)
- **Medium MA**: 50-period
- **Slow MA**: 200-period (trend anchor)

### Trading Signals

**Buy Signal:** Triple bullish alignment + fast MA crosses medium MA
```
Conditions:
1. MA_fast(t-1) ≤ MA_medium(t-1) AND MA_fast(t) > MA_medium(t)
2. MA_fast(t) > MA_medium(t) > MA_slow(t)
```

**Sell Signal:** Triple bearish alignment + fast MA crosses medium MA
```
Conditions:
1. MA_fast(t-1) ≥ MA_medium(t-1) AND MA_fast(t) < MA_medium(t)
2. MA_fast(t) < MA_medium(t) < MA_slow(t)
```

### Formula

```
Trend Strength Score = (MA_fast - MA_slow) / MA_slow
Signal Strength = min(1.0, Trend Strength Score)
```

### Advantages
- Reduces false signals significantly
- Aligns with multiple timeframe trends
- Better for longer-term positions
- Clear trend confirmation

### Disadvantages
- Slower signal generation (misses some moves)
- Requires sustained trends
- More complex to optimize

### Recommended Parameters
- Fast: 10-20 periods
- Medium: 40-60 periods
- Slow: 150-250 periods
- Best for: Swing to position trading

---

## 3. MACD (Moving Average Convergence Divergence)

### Strategy Overview
A momentum indicator that combines trend-following and momentum signals. Shows the relationship between two exponential moving averages and momentum oscillations.

### Components

**1. MACD Line**
```
MACD(t) = EMA_12(t) - EMA_26(t)
```

**2. Signal Line**
```
Signal(t) = EMA_9(MACD)
```

**3. MACD Histogram**
```
Histogram(t) = MACD(t) - Signal(t)
```

### Formula for EMA

```
EMA(t) = Price(t) × Multiplier + EMA(t-1) × (1 - Multiplier)
where Multiplier = 2 / (Period + 1)

For MACD:
- Multiplier_12 = 2/13 ≈ 0.1538
- Multiplier_26 = 2/27 ≈ 0.0741
- Multiplier_9  = 2/10 = 0.2
```

### Trading Signals

**Buy Signal:**
```
1. MACD crosses above Signal line
2. Histogram turns positive
3. Momentum increasing (histogram bars growing)
```

**Sell Signal:**
```
1. MACD crosses below Signal line
2. Histogram turns negative
3. Momentum decreasing (histogram bars shrinking)
```

### Interpretation

| MACD vs Signal | Histogram | Meaning |
|---|---|---|
| MACD > Signal | Positive | Bullish momentum |
| MACD < Signal | Negative | Bearish momentum |
| Histogram growing | Positive → ↑ | Increasing bullish momentum |
| Histogram shrinking | Positive → ↓ | Decreasing bullish momentum |

### Advantages
- Works in both trending and range-bound markets
- Combines trend and momentum
- Crossover signals are clear
- Histogram visualizes momentum change
- Good for position entry/exit timing

### Disadvantages
- Lagging indicator (based on moving averages)
- False signals in choppy markets
- Can produce whipsaw trades
- Requires confirmation from other indicators

### Recommended Usage
- Best for: Medium-term trading (4-hour to daily)
- Confirm with: Price action, support/resistance, volume
- Filter: Use in direction of 200-day MA trend

---

## 4. ADX (Average Directional Index) - Trend Strength

### Strategy Overview
Measures the strength of a trend, separate from its direction. Critical for distinguishing between strong trending markets and choppy range-bound conditions.

### Components

**1. Directional Movement**
```
High Diff(t) = High(t) - High(t-1)
Low Diff(t)  = Low(t-1) - Low(t)

+DM(t) = High Diff(t) if High Diff > Low Diff AND High Diff > 0, else 0
-DM(t) = Low Diff(t)  if Low Diff > High Diff AND Low Diff > 0, else 0
```

**2. True Range (ATR Component)**
```
TR(t) = max(
    High(t) - Low(t),
    |High(t) - Close(t-1)|,
    |Low(t) - Close(t-1)|
)
```

**3. Directional Indicators**
```
Smoothed +DM = Wilder's Smoothing of +DM (14 periods)
Smoothed -DM = Wilder's Smoothing of -DM (14 periods)
Smoothed TR  = Wilder's Smoothing of TR (14 periods)

+DI(t) = 100 × (Smoothed +DM(t) / Smoothed TR(t))
-DI(t) = 100 × (Smoothed -DM(t) / Smoothed TR(t))
```

**4. ADX Line**
```
DX(t) = 100 × |+DI(t) - -DI(t)| / (+DI(t) + -DI(t))

ADX(t) = EMA(DX, period=14)
        = EMA_9(DX) for first calculation
        = 0.926 × ADX(t-1) + 0.074 × DX(t) for subsequent
```

### Trading Signals

**Buy Signal:**
```
Condition 1: +DI(t-1) ≤ -DI(t-1) AND +DI(t) > -DI(t)
Condition 2: ADX(t) > 20 (confirms trend strength)
Signal Strength = min(1.0, ADX(t) / 50)
```

**Sell Signal:**
```
Condition 1: +DI(t-1) ≥ -DI(t-1) AND +DI(t) < -DI(t)
Condition 2: ADX(t) > 20 (confirms trend strength)
Signal Strength = min(1.0, ADX(t) / 50)
```

### ADX Interpretation

| ADX Value | Trend Strength | Trading Action |
|-----------|---|---|
| ADX > 40 | Very strong | Follow trend with confidence |
| ADX 25-40 | Strong | Reliable trend signals |
| ADX 20-25 | Moderate | Valid but use caution |
| ADX < 20 | Weak/Ranging | Avoid breakout/trend trades |
| ADX < 10 | No trend | Trade ranges, not trends |

### Advantages
- Measures trend strength objectively
- Filters out whipsaw trades
- Works across all markets
- Prevents trading in choppy markets
- +DI/-DI shows trend direction

### Disadvantages
- Requires two conditions (direction + strength)
- Slower to react to trend changes
- Not suitable for range trading
- Needs minimum ADX level to trade

### Recommended Usage
- ADX threshold: 20-25 for signal reliability
- Best for: Volatility filtering before trend trades
- Combine with: Moving averages for direction, MACD for timing
- Exit when: ADX drops below 20 (trend weakening)

---

## 5. Turtle Trading System (Breakout Strategy)

### Strategy Overview
The famous Turtle Trading System uses breakout-based entries and exits. Traders Richard Dennis' experiment with the Turtles proved that mechanical breakout trading could generate consistent profits.

### Core Rules

**1. Entry Rules**

Long Entry (Buy):
```
Condition: Close(t) > max(High[t-20:t-1])
This is the highest high of the previous 20 periods
```

Short Entry (Sell):
```
Condition: Close(t) < min(Low[t-20:t-1])
This is the lowest low of the previous 20 periods
```

**2. Exit Rules**

Exit Long (Stop Loss):
```
Condition: Close(t) < min(Low[t-10:t-1])
Exit when price falls below 10-day low
```

Exit Short (Take Profit):
```
Condition: Close(t) > max(High[t-10:t-1])
Exit when price rises above 10-day high
```

**3. Position Sizing (Risk Management)**
```
Unit Size = Account Risk / (2 × ATR(14))

Where:
- Account Risk = 2% of account per trade
- ATR(14) = 14-period Average True Range
- Stop Loss = Entry Price ± 2 × ATR
- Take Profit = Entry Price ± 3 × ATR (optional)
```

### Trading Logic

```
1. System waits for quiet market (low volatility)
2. Price breaks out of consolidation range
3. Enter on breakout of 20-day high/low
4. Place stop loss at 2×ATR from entry
5. Exit on 10-day high/low breakout
6. Position sizing based on volatility (ATR)
```

### Formula Summary

```
Entry Breakout = max(High[t-N:t-1]) where N=20
Exit Breakout   = min(Low[t-M:t-1])  where M=10

Breakout Strength = (Entry - Low_Min) / (High_Max - Low_Min)
Signal Strength = min(1.0, Breakout Strength)

ATR(t) = EMA(TrueRange, 14)
Stop Distance = 2 × ATR(t)
Target Distance = 3 × ATR(t)
```

### Advantages
- Rules-based and mechanical (removes emotion)
- Works in trending markets
- Simple to understand and implement
- Position size adapts to volatility
- Proven by real trading results

### Disadvantages
- Whipsaws in choppy markets
- Many false breakouts
- Requires sufficient capital for position sizing
- Can be slow to re-enter after stops

### Recommended Parameters
- Entry Breakout: 20 days (adjust to volatility)
- Exit Breakout: 10 days
- ATR Period: 14 days
- Risk per Trade: 2% of account
- Best for: Highly liquid, trending markets

### Variations
- **Long-term Turtle**: Entry 55-day, Exit 20-day
- **Short-term Turtle**: Entry 10-day, Exit 5-day
- **Volatility-adjusted**: Scale periods by current ATR vs. average ATR

---

## Strategy Comparison Matrix

| Strategy | Signal Speed | Whipsaw Risk | Best Market | Trend Confirmation |
|----------|---|---|---|---|
| Dual MA | Medium | Medium | Trending | Moving Average Cross |
| Triple MA | Slow | Low | Trending | Triple Alignment |
| MACD | Medium | Medium | Trending/Range | Histogram + Cross |
| ADX | Slow | Low | Trending | Strength + Direction |
| Turtle | Fast | High | Trending | Volatility Adjusted |

---

## Implementation Recommendations

### Best Practices

1. **Signal Confirmation**
   - Combine multiple strategies for consensus
   - Require 2+ strategies to agree for higher confidence
   - Use ADX to filter weak trends

2. **Risk Management**
   - Always use stop losses
   - Scale position size inversely to volatility
   - Risk only 1-2% per trade

3. **Market Conditions**
   - Adjust parameters by timeframe
   - Monitor volatility changes
   - Exit when ADX drops below 20

4. **Backtesting**
   - Test on 10+ years of data
   - Include transaction costs
   - Optimize for drawdown, not just returns

### Parameter Optimization Guide

```
Short Timeframe (5-min to 1-hour):
- Reduce all periods by 50-75%
- Use tighter stops
- Higher trade frequency

Medium Timeframe (4-hour to Daily):
- Use standard parameters
- Balanced risk/reward
- Moderate trade frequency

Long Timeframe (Weekly to Monthly):
- Increase all periods by 50-100%
- Wider stops
- Lower trade frequency
```

---

## Code Usage

All five strategies are implemented in `momentum.py`:

```python
from momentum import MomentumStrategy
import numpy as np

# Initialize strategy manager
momentum = MomentumStrategy()

# Analyze with all strategies
results = momentum.analyze(prices, high, low)

# Get consensus signals
consensus = momentum.get_consensus_signal(prices, high, low)

# Individual strategy access
from momentum import DualMovingAverageCrossover, MACD, ADXTrendStrength

# Custom strategy instance
macd = MACDIndicator(fast=12, slow=26, signal=9)
macd_results = macd.calculate(prices)
```

---

## References

- Wilder Jr., J. W. (1978). New Concepts in Technical Trading Systems
- Faith, C. (2007). The Way of the Turtle
- Murphy, J. (1999). Technical Analysis of the Financial Markets
- Pring, M. (2002). Technical Analysis Explained

---

## Disclaimer

This information is for educational purposes only. Past performance does not guarantee future results. Always backtest strategies on historical data before live trading. Consult with a financial advisor before implementing any trading strategy.
