# Market Microstructure Analysis Guide

## Overview

Market microstructure is the study of how financial markets operate, focusing on transaction costs, order flow, and their impact on prices. Understanding microstructure is essential for:

- **Algorithmic Trading**: Optimizing execution to minimize price impact
- **Liquidity Analysis**: Assessing asset liquidity and trading costs
- **Risk Management**: Quantifying transaction cost risks
- **Market Making**: Understanding spread dynamics and inventory management

**Key Question**: How do trades (order flow) transmit information to prices?

---

## 1. Kyle's Lambda (Price Impact Parameter)

### 1.1 Conceptual Foundation

Kyle's lambda measures the **permanent price impact of order flow** - how much prices move in response to trading activity.

**Definition**: Kyle's lambda (λ) is the slope of the price impact function.

$$\lambda = \frac{|\Delta P_t|}{|Q_t|}$$

Where:
- **ΔP_t**: Price change from time t to t+1
- **Q_t**: Order flow (signed or unsigned volume)

### 1.2 Interpretation

| λ Value | Interpretation | Asset Type |
|---------|---|---|
| **Low λ** | Small price impact | Highly liquid (large cap, high volume) |
| **High λ** | Large price impact | Illiquid (small cap, low volume) |
| **λ → 0** | Perfectly liquid (frictionless) | Hypothetical ideal |
| **λ → ∞** | Infinitely illiquid | Extreme case (no trading) |

### 1.3 Economic Interpretation

Kyle's lambda captures:
1. **Inventory costs**: Market makers' unwillingness to hold large positions
2. **Adverse selection**: Cost of trading with informed traders
3. **Order processing**: Direct transaction costs

### 1.4 Calculation Example

```python
from market_microstructure import MarketMicrostructure
import pandas as pd

# Sample data
prices = pd.Series([100, 101, 102, 101.5, 103])
volumes = pd.Series([1000, 1500, 2000, 1200, 2500])

# Initialize
mm = MarketMicrostructure(prices, volumes)

# Calculate Kyle's lambda
kylos = mm.kylos_lambda(window=20)
print(f"Kyle's lambda (rolling): {kylos}")

# High lambda indicates illiquidity
```

### 1.5 Empirical Properties

- **Cross-sectional**: Small caps have higher λ than large caps
- **Time-series**: λ increases during market stress
- **Persistence**: Relatively stable over time (good for prediction)
- **Reversal during crises**: Breaks down during flash crashes

---

## 2. Amihud Illiquidity Ratio

### 2.1 Definition

The **Amihud illiquidity measure** (ILLIQ) quantifies the price impact of trading volume.

$$\text{ILLIQ}_t = \frac{|R_t|}{V_t}$$

Where:
- **R_t**: Absolute return at time t
- **V_t**: Trading volume (or dollar volume: P_t × V_t)

**Rolling average** (typically 20-30 days):

$$\text{ILLIQ} = \frac{1}{N} \sum_{t=1}^{N} \frac{|R_t|}{V_t}$$

### 2.2 Interpretation

| ILLIQ | Liquidity Assessment |
|-------|---|
| **< 0.001** | Highly liquid (e.g., large-cap stocks) |
| **0.001 - 0.01** | Moderately liquid (e.g., mid-cap stocks) |
| **> 0.01** | Illiquid (e.g., small-cap, thinly traded) |

### 2.3 Intuition

High ILLIQ means:
- A 1% return requires small volume → illiquid
- A 1% return requires large volume → liquid

### 2.4 Calculation

```python
# Calculate Amihud illiquidity
amihud = mm.amihud_illiquidity(window=20)
print(f"Amihud ILLIQ: {amihud}")

# Identify illiquid periods
illiquid_threshold = amihud.quantile(0.75)
illiquid_dates = amihud[amihud > illiquid_threshold].index
```

### 2.5 Applications

1. **Portfolio Construction**: Avoid highly illiquid assets
2. **Risk Management**: Adjust position sizes for illiquidity
3. **Pricing**: Liquidity discount for illiquid assets
4. **Rebalancing**: Schedule trades during liquid periods

---

## 3. Bid-Ask Spread Models

### 3.1 Effective Spread

**Definition**: The actual cost of trading, measured as deviation from midpoint.

$$\text{Effective Spread} = \frac{\text{Ask} - \text{Bid}}{\text{Midpoint}}$$

$$\text{Midpoint} = \frac{\text{Bid} + \text{Ask}}{2}$$

**Economic Components**:
- **Inventory cost**: Market maker compensation for holding risk
- **Adverse selection**: Cost of trading with informed traders
- **Order processing**: Direct operational costs

### 3.2 Roll's Bid-Ask Estimator

**Roll (1984)** developed an elegant method to estimate bid-ask spread from price changes alone.

**Key Insight**: Price changes have two components:
1. **Permanent**: New information (fundamental price move)
2. **Transitory**: Order processing (spread bounce-back)

**Mathematical Model**:

Assume prices follow:
$$P_t = M_t + \frac{S}{2} \cdot I_t$$

Where:
- **M_t**: Unobserved fundamental midpoint
- **S**: Bid-ask spread
- **I_t**: Order indicator (±1 for buy/sell)

**Price changes**:
$$\Delta P_t = \Delta M_t + \frac{S}{2}(\Delta I_t)$$

**Covariance property**:
$$\text{Cov}(\Delta P_t, \Delta P_{t-1}) = -\frac{S^2}{4}$$

This is negative because:
- If trade t-1 was a buy (push price up), trade t likely contracts (price down)
- Order flow mean-reverts from spread bounce

**Solving for spread**:
$$S = 2\sqrt{-\text{Cov}(\Delta P_t, \Delta P_{t-1})}$$

### 3.3 Roll's Estimator Calculation

```python
# Calculate Roll's bid-ask spread estimator
rolls_spread = mm.rolls_estimator(window=20)
print(f"Estimated bid-ask spread (bps): {rolls_spread * 100}")

# Rolling window allows spread estimation over time
# Identifies illiquid periods (high spread)
```

**Advantages**:
- No need for actual bid/ask quotes
- Works with closing prices only
- Robust to stock splits and dividends

**Limitations**:
- Assumes efficient market hypothesis
- Fails if true spread is zero (very liquid stocks)
- Sensitive to estimation window length

### 3.4 High-Low Spread Estimator

Simple alternative using intraday highs and lows:

$$\text{Spread} \approx \frac{\text{High} - \text{Low}}{\text{Midpoint}}$$

**Assumption**: High executed at ask, low at bid

**Advantages**:
- Simple and intuitive
- Requires only OHLC data

**Disadvantages**:
- Less accurate than Roll's method
- Assumes no price discovery within spread

---

## 4. Price Impact Models

### 4.1 Linear Price Impact

**Simple regression model**:

$$\Delta P_t = \alpha + \lambda \cdot |Q_t| + \epsilon_t$$

Where:
- **λ**: Price impact coefficient
- **Q_t**: Order flow (volume or signed volume)
- **ε_t**: Noise term

**Calculation**:

$$\lambda = \frac{\text{Cov}(\Delta P, |Q|)}{\text{Var}(|Q|)}$$

**OLS Estimation**:

```python
# Linear price impact
impact_linear = mm.price_impact_linear(lookback=50)
print(f"Price impact (linear): {impact_linear['price_impact']:.6f}")
print(f"R-squared: {impact_linear['r_squared']:.4f}")
print(f"Significance (t-stat): {impact_linear['t_stat_impact']:.3f}")
```

**Interpretation**:
- λ = 0.001 means: 1% volume increase → 0.1% price impact
- R² = 0.30 means: Volume explains 30% of price changes

### 4.2 Nonlinear Price Impact (Power Law)

Empirical evidence shows price impact follows a **power law**:

$$\Delta P = \alpha \cdot |Q|^{\beta}$$

**Taking logarithms** (log-linear model):

$$\log(\Delta P) = \log(\alpha) + \beta \log(|Q|) + \epsilon$$

**Typical parameter range**:
- **β = 0.5**: Impact ∝ √Volume (many empirical studies)
- **β = 1.0**: Impact ∝ Volume (perfect proportionality)
- **β > 1**: Impact accelerates with volume (rare)

**Advantage**: More realistic than linear model
- Small trades have less impact
- Large trades disproportionately move prices

**Calculation**:

```python
# Nonlinear (power law) price impact
impact_nonlinear = mm.price_impact_nonlinear(lookback=50)
print(f"Power law exponent β: {impact_nonlinear['power_law_exponent']:.3f}")
print(f"Elasticity: {impact_nonlinear['elasticity']:.3f}")

# β = 0.5 means 10% volume increase → 5% price impact
# β = 1.0 means 10% volume increase → 10% price impact
```

---

## 5. Volume-Weighted Metrics

### 5.1 Volume-Weighted Average Price (VWAP)

**Definition**:

$$\text{VWAP} = \frac{\sum_i P_i \cdot V_i}{\sum_i V_i}$$

**Use Cases**:
- Evaluate execution quality
- Algo trading benchmarks
- Identify fair value during trading

**Calculation**:

```python
# Calculate VWAP
vwap = mm.volume_weighted_average_price(window=20)
print(f"VWAP: {vwap}")

# Compare execution price to VWAP
# VWAP > execution price → good execution (bought below average)
```

---

## 6. Liquidity Report

### 6.1 Integrated Liquidity Metrics

Generate comprehensive report with all liquidity measures:

```python
# Generate full liquidity report
report = mm.liquidity_report(window=20)
print(report.head(10))

# Columns included:
# - Kyle's lambda (price impact)
# - Amihud illiquidity ratio
# - Roll's spread estimator
# - VWAP
# - Price impact coefficient
# - Effective spread (if bid/ask available)
# - Realized spread (if bid/ask available)
```

### 6.2 Interpretation Strategy

1. **High Kyle's lambda + High Amihud**: Asset is very illiquid
2. **Increasing spreads over time**: Market stress period
3. **Price impact β < 0.5**: Highly efficient market
4. **VWAP > Price**: Large informed traders active

---

## 7. Order Flow Dynamics

### 7.1 Order Flow Properties

```python
# Analyze order flow characteristics
order_flow = mm.order_flow_analysis()
print(order_flow.describe())

# Key metrics:
# - Volume clusters: High vol periods
# - Price-volume correlation: Information flow
# - Volume spikes: Large block trades
```

### 7.2 Order Flow Interpretation

| Pattern | Interpretation | Trading Implication |
|---------|---|---|
| **Vol spike + small price change** | Informed traders present | Expect reversal |
| **Vol spike + large price change** | News event | Trend likely to continue |
| **Low vol + stable price** | Quiet market | Low execution costs |
| **High vol + high volatility** | Market stress | Avoid large trades |

---

## 8. Practical Applications

### 8.1 Execution Optimization

**Problem**: Minimize transaction costs for large trades

**Solution Framework**:
1. Calculate real-time Kyle's lambda
2. Estimate price impact for order size
3. Optimize execution: split into smaller orders, spread over time
4. Monitor realized spread against benchmark

```python
# For a 100,000 share order
order_size = 100000
avg_volume = mm.volume.mean()
ratio = order_size / avg_volume

# Estimate total price impact
linear_impact = impact['price_impact'] * order_size
estimated_cost_bps = (linear_impact / mm.price.iloc[-1]) * 10000

print(f"Estimated execution cost: {estimated_cost_bps:.2f} basis points")
```

### 8.2 Liquidity Screening

**Application**: Select liquid assets for algo trading

```python
# Liquidity thresholds
amihud_threshold = 0.001  # ILLIQ < 0.001
spread_threshold = 0.01    # Effective spread < 1 bp
min_daily_volume = 1e6     # $1M daily volume

# Screen portfolio
is_liquid = (report['amihud_illiq'] < amihud_threshold) & \
            (report['rolls_spread_pct'] < spread_threshold)

liquid_assets = is_liquid[is_liquid].index
```

### 8.3 Risk Management

**Add liquidity adjustment to position sizing**:

```python
# Base risk limit: 1% of NAV per position
base_limit = 0.01 * portfolio_nav

# Adjust for illiquidity
amihud_z_score = (amihud - amihud.mean()) / amihud.std()
liquidity_discount = 1 - (0.1 * np.clip(amihud_z_score, 0, 2))

adjusted_limit = base_limit * liquidity_discount

# Result: Smaller positions in illiquid assets
```

---

## 9. Model Selection Guide

### 9.1 When to Use Each Metric

| Metric | Best For | Data Required |
|--------|----------|---|
| **Kyle's Lambda** | Quick liquidity screening | Prices, volumes |
| **Amihud ILLIQ** | Portfolio construction, rebalancing | Prices, volumes, returns |
| **Roll's Spread** | Bid-ask estimation without quotes | Prices only |
| **Effective Spread** | Execution quality tracking | Bid/ask quotes |
| **Price Impact Model** | Execution optimization | Prices, volumes, trades |

### 9.2 Recommended Workflow

```python
from market_microstructure import MarketMicrostructure

# 1. Initialize with available data
mm = MarketMicrostructure(prices, volumes, bid_data, ask_data)

# 2. Calculate all metrics
report = mm.liquidity_report(window=20)

# 3. Compare spread methods
from market_microstructure import compare_spread_methods
spread_comparison = compare_spread_methods(prices, volumes,
                                          bid_prices, ask_prices,
                                          high_prices, low_prices)

# 4. Estimate price impact
impact_lin = mm.price_impact_linear(lookback=50)
impact_nonlin = mm.price_impact_nonlinear(lookback=50)

# 5. Decision: Use nonlinear model if β significant
if impact_nonlin['r_squared'] > 0.2:
    use_power_law = True
else:
    use_linear = True

# 6. Implementation
print(f"Price impact coefficient: {impact_lin['price_impact']:.6f}")
print(f"Bid-ask spread (Roll): {report['rolls_spread_pct'].mean():.2f}%")
```

---

## 10. Advanced Topics

### 10.1 Dynamic Spreads

Spreads change with market conditions:

```python
# Spread widens during volatility
volatility = returns.rolling(20).std()
spread_volatility_correlation = \
    report['rolls_spread_pct'].rolling(20).corr(volatility)

print(f"Spread-vol correlation: {spread_volatility_correlation.mean():.3f}")
```

### 10.2 Intertemporal Effects

Large trades impact prices over time:

```python
# Immediate impact: execution at ask/bid
immediate_impact = spread / 2

# Temporary impact: short-term mean reversion
temporary_impact = order_size / avg_volume * lambda_param

# Permanent impact: information leakage
permanent_impact = information_content * order_size
```

### 10.3 Volatility-Liquidity Relation

Empirical pattern:

$$\text{Liquidity} \propto \frac{1}{\sqrt{\text{Volatility}}}$$

High volatility → Low liquidity (wider spreads, lower volume)

---

## 11. Key References

### Academic Papers

1. **Kyle, A. S. (1985)** - "Continuous Auctions and Insider Trading"
   - Foundational model for price impact and adverse selection
   - Introduces Kyle's lambda

2. **Roll, R. (1984)** - "A Simple Implicit Measure of the Effective Bid-Ask Spread"
   - Roll's spread estimator from price changes
   - Classic paper on microstructure measurement

3. **Amihud, Y. (2002)** - "Illiquidity and Stock Returns: Cross-Section and Time-Series Effects"
   - Amihud's ILLIQ measure
   - Evidence for liquidity premium

4. **Almgren, R., & Chriss, N. (2001)** - "Optimal Execution of Portfolio Transactions"
   - Execution optimization framework
   - Temporal execution strategies

5. **Hasbrouck, J. (2007)** - "Empirical Market Microstructure"
   - Comprehensive reference for microstructure models
   - Information decomposition

### Textbooks

- **Harris, L. (2003)** - "Trading and Exchanges: Market Microstructure for Practitioners"
- **Glosten, L. R., & Harris, L. E. (1988)** - "Estimating the Components of the Bid/Ask Spread"

---

## 12. Limitations and Caveats

### Model Limitations

1. **Roll's estimator**: Fails in perfectly liquid markets (zero true spread)
2. **Linear price impact**: Oversimplifies complex order flow dynamics
3. **Amihud ILLIQ**: High volatility days inflate illiquidity measures
4. **Assumptions**: Assumes rational behavior and no manipulation

### Data Quality Issues

1. **Bid-ask bounce**: Artificial spread widening from last-minute trades
2. **Large block trades**: May not execute at quoted prices
3. **Overnight gaps**: Create covariance distortions for Roll's method
4. **Corporate actions**: Splits/dividends affect historical prices

### Market Regime Considerations

- **Normal times**: Microstructure models perform well
- **Market stress**: Spreads widen dramatically (model breaks down)
- **Flash crashes**: Price impact nonlinearities become extreme
- **After hours**: Different liquidity profiles not captured

---

## 13. Implementation Best Practices

### 13.1 Data Requirements

- **Minimum history**: 1+ year for stable estimates
- **Frequency**: Daily sufficient; higher frequency (5-min) improves accuracy
- **Quality checks**:
  - No missing prices
  - Bid < Price < Ask (if available)
  - Positive volumes
  - Handle splits/dividends

### 13.2 Parameter Selection

```python
# Window size selection
short_window = 5   # Daily updates (noisy)
medium_window = 20 # 1 month (balanced)
long_window = 60   # 3 months (stable)

# Use medium window for most applications
# Short for responsive signals
# Long for stable estimates
```

### 13.3 Validation

```python
# Cross-validate estimates
# 1. Compare Roll's spread vs. effective spread (should correlate)
# 2. Check Kyle's lambda temporal stability (should be persistent)
# 3. Verify Amihud behavior (should spike during stress)
# 4. Backtest price impact predictions

correlation = report['rolls_spread_pct'].corr(report['effective_spread_pct'])
print(f"Spread method correlation: {correlation:.3f}")  # Should be > 0.5
```

---

## 14. Example: Complete Microstructure Analysis

```python
from market_microstructure import MarketMicrostructure
import pandas as pd
import numpy as np

# Load data
data = pd.read_csv('market_data.csv', parse_dates=['Date'])
mm = MarketMicrostructure(
    prices=data['Close'],
    volumes=data['Volume'],
    bid_data=data['Bid'],
    ask_data=data['Ask'],
)

# 1. Generate report
report = mm.liquidity_report(window=20)

# 2. Analyze spreads
spread_stats = mm.bid_ask_statistics()
print(f"Average spread: {spread_stats['mean_spread_bps']:.2f} bps")

# 3. Price impact
impact = mm.price_impact_nonlinear(lookback=50)
print(f"Price impact elasticity: {impact['elasticity']:.3f}")

# 4. Identify liquidity regimes
amihud_high = report['amihud_illiq'] > report['amihud_illiq'].quantile(0.75)
print(f"Illiquid periods: {amihud_high.sum()} days")

# 5. Execution guidance
execution_cost_bps = (impact['power_law_exponent'] *
                     (order_size / mm.volume.mean()) ** impact['power_law_exponent'] * 100)
print(f"Estimated execution cost: {execution_cost_bps:.2f} bps")

# 6. Track improvements
report['date'] = data['Date']
report.to_csv('liquidity_report.csv')
```

---

**Last Updated**: November 2024
**Status**: Production-Ready
**Author**: Quantitative Finance Analytics
