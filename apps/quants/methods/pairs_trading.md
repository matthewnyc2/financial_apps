# Pairs Trading and Cointegration Analysis

## Table of Contents
1. [Introduction](#introduction)
2. [Pair Selection Methods](#pair-selection-methods)
3. [Cointegration Testing](#cointegration-testing)
4. [Spread Analysis](#spread-analysis)
5. [Half-Life Estimation](#half-life-estimation)
6. [Signal Generation](#signal-generation)
7. [Portfolio Construction](#portfolio-construction)
8. [Implementation Details](#implementation-details)

---

## Introduction

Pairs trading is a market-neutral statistical arbitrage strategy that exploits the mean-reverting relationship between two correlated assets. The core premise is that historically related assets will continue to move together, and when they diverge, they will eventually reconverge.

### Key Concepts

- **Cointegration**: Two non-stationary series (I(1)) that form a stationary linear combination
- **Mean Reversion**: Spreads deviate from equilibrium and revert back over time
- **Market Neutral**: Equal and opposite positions eliminate systematic market risk
- **Statistical Arbitrage**: Profits from temporary price deviations based on statistical relationships

### Strategy Advantages

- Market neutral: Uncorrelated with broad market movements
- Low correlation with other strategies
- Systematic entry/exit rules
- Defined risk parameters
- Works in bull and bear markets

---

## Pair Selection Methods

### 1. Distance Method

The distance method identifies pairs by minimizing the sum of squared price differences over a lookback period.

#### Formula
```
Distance = Σ(P1_t - P2_t)² for t ∈ [T-lookback, T]

Normalized Distance = Distance / mean(P2)
```

#### Interpretation
- **Lower distance** = Better pair candidates
- Assumes similar magnitude and movement patterns
- Simple but requires price normalization

#### Implementation
```python
distance = pt.distance_method(prices1, prices2, lookback=60)
# Lower values indicate better potential pairs
```

#### Advantages
- Simple computation
- Intuitive interpretation
- Quick screening across many pairs

#### Disadvantages
- Ignores statistical properties
- Sensitive to price scaling
- Doesn't test stationarity

---

### 2. Correlation Method

The correlation method selects pairs with high historical correlation, indicating strong co-movement.

#### Formula
```
r = cov(R1, R2) / (σ₁ × σ₂)

where R_i = log(P_i,t / P_i,t-1) are log returns
```

#### Interpretation
- **r = 1**: Perfect positive correlation
- **r = 0**: No correlation
- **r = -1**: Perfect negative correlation
- Target: **r > 0.7** or **r > 0.8** for pairs trading

#### Implementation
```python
correlation = pt.correlation_method(prices1, prices2, lookback=60)
# Higher correlations indicate better pairs
```

#### Advantages
- Statistical foundation
- Captures co-movement
- Easy to interpret

#### Disadvantages
- Correlation ≠ Cointegration
- Non-stationary series can have spurious correlation
- Ignores long-term relationship

---

### Comparison: Distance vs. Correlation

| Metric | Distance | Correlation |
|--------|----------|-------------|
| **Basis** | Price differences | Return co-movement |
| **Normalization** | Price magnitude | Volatility |
| **Interpretation** | Lower is better | Higher is better |
| **Threshold** | Domain-specific | r > 0.7 |
| **Lookback** | Recent behavior | Historical patterns |

---

## Cointegration Testing

### Why Cointegration Matters

Two non-stationary series (I(1)) are cointegrated if they form a stationary linear combination. This is crucial because:

1. Regular correlation between non-stationary series is spurious
2. Cointegrated pairs exhibit mean reversion
3. Provides theoretical foundation for pairs trading

### 1. Engle-Granger Two-Step Test

The Engle-Granger test determines if two series are cointegrated using a two-step procedure.

#### Formula

**Step 1: OLS Regression**
```
Y_t = α + β × X_t + u_t
```

**Step 2: ADF Test on Residuals**
```
ΔY_t = γ × Y_t-1 + Σ δ_i × ΔY_t-i + ε_t

H₀: γ = 0 (unit root, non-stationary residuals)
H₁: γ < 0 (stationary residuals, cointegrated)
```

#### Critical Values (MacKinnon)
| Significance | Critical Value |
|-------------|----------------|
| 90% | -3.37 |
| 95% | -3.37 |
| 99% | -4.03 |

#### Interpretation
- If test statistic < critical value: **Reject H₀** → Cointegrated
- If test statistic > critical value: **Fail to reject H₀** → Not cointegrated

#### Implementation
```python
eg_result = pt.engle_granger_test(prices1, prices2)

# Results dictionary contains:
# - test_statistic: ADF test statistic
# - critical_value: Critical value at 95% confidence
# - is_cointegrated: Boolean result
# - hedge_ratio (beta): Hedging ratio
# - residuals: Spread series (Y - beta * X)
# - p_value: Approximate p-value
```

#### Advantages
- Simple two-step procedure
- Well-established critical values
- Produces hedge ratio
- Standard test in academic literature

#### Disadvantages
- Asymmetric (order-dependent)
- Only identifies one cointegrating relationship
- Limited to bivariate relationships
- Requires specification of dependent/independent variable

---

### 2. Johansen Cointegration Test

The Johansen test is a multivariate approach that identifies all cointegrating relationships in a system.

#### Formula

**VAR Model Specification**
```
dX_t = α × β' × X_t-1 + ε_t
```

where:
- α: Adjustment coefficients (n × r)
- β: Cointegrating vectors (n × r)
- r: Number of cointegrating relationships

**Trace Test Statistic**
```
Trace = -T × Σ ln(1 - λᵢ) for i = r+1 to n

H₀: At most r cointegrating relationships
H₁: More than r cointegrating relationships
```

**Eigenvalue (Max Eigenvalue) Test**
```
λ_max = -T × ln(1 - λ_r+1)

H₀: Exactly r cointegrating relationships
H₁: Exactly r+1 cointegrating relationships
```

#### Critical Values (95% Confidence)
| Test | n=2 | n=3 | n=4 |
|------|-----|-----|-----|
| Trace | 15.495 | 29.797 | 47.856 |
| Eigenvalue | 14.264 | 21.131 | 27.584 |

#### Interpretation

For a 2-asset system:

| Trace Test | Eigenvalue Test | Interpretation |
|-----------|-----------------|-----------------|
| < 15.495 | < 14.264 | No cointegration |
| > 15.495 | < 14.264 | One cointegrating relationship |
| > 15.495 | > 14.264 | Two cointegrating relationships (fully integrated) |

#### Implementation
```python
prices_array = np.column_stack([prices1, prices2])
joh_result = pt.johansen_test(prices_array)

# Results dictionary contains:
# - test_statistic: Trace test statistic
# - eigenvalues: Eigenvalues (sorted descending)
# - eigenvectors: Cointegrating vectors
# - n_cointegrating: Number of cointegrating relationships
# - is_cointegrated: Boolean result
```

#### Advantages
- Multivariate: Handles multiple assets
- Identifies all cointegrating relationships
- No order-dependence
- Provides eigenvectors (cointegrating weights)

#### Disadvantages
- More complex computation
- Requires stable VAR model
- Sensitive to lag length specification
- More degrees of freedom required

---

### Comparison: Engle-Granger vs. Johansen

| Aspect | Engle-Granger | Johansen |
|--------|---------------|----------|
| **Variables** | Bivariate only | Multivariate |
| **Relationships** | One | All |
| **Order** | Dependent (asymmetric) | Independent |
| **Simplicity** | High | Medium |
| **Test Type** | Sequential | Simultaneous |
| **Eigenvectors** | No | Yes |
| **Application** | Pairs trading | Portfolio cointegration |

---

## Spread Analysis

### Spread Definition

The spread is the stationary combination of the two cointegrated series, representing the mean-reverting trading signal.

#### Formula
```
Spread_t = Y_t - β × X_t

where:
- Y_t: Price of asset 1
- X_t: Price of asset 2
- β: Hedge ratio from cointegration regression
```

#### Properties of Stationary Spread

1. **Mean-reverting**: Deviations from mean are temporary
2. **Ergodic**: Time averages = ensemble averages
3. **Invertible**: Not affected by price inflation
4. **Dollar-neutral**: Equal long/short positions by construction

### Z-Score Normalization

To generate comparable signals across different pairs, normalize the spread using z-score.

#### Formula
```
Z_t = (Spread_t - μ) / σ

where:
- μ = E[Spread] (lookback mean)
- σ = σ[Spread] (lookback standard deviation)
```

#### Interpretation
- **Z = 0**: Spread at mean (fair value)
- **Z > 2**: Spread 2 std devs above mean (potential short)
- **Z < -2**: Spread 2 std devs below mean (potential long)
- **Z > 3**: Extreme deviation (consider entry)

#### Implementation
```python
spread, hedge_ratio = pt.calculate_spread(prices1, prices2)
zscore = pt.calculate_zscore(spread, lookback=20)

# Use zscore for signal generation
```

### Spread Quality Metrics

| Metric | Calculation | Interpretation |
|--------|-------------|-----------------|
| **Mean** | E[Spread] | Should be near 0 (demeaned) |
| **Std Dev** | σ[Spread] | Typical deviation magnitude |
| **Skewness** | E[(X-μ)³]/σ³ | Asymmetry (should be near 0) |
| **Kurtosis** | E[(X-μ)⁴]/σ⁴ - 3 | Tail behavior (should be near 0) |
| **Min/Max** | Extreme values | Range of spread |

---

## Half-Life Estimation

Half-life measures how long it takes for deviations from the mean to decay to 50% of their initial value. This is critical for position management.

### Method 1: AR(1) Autoregressive Model

The AR(1) model assumes the spread follows a mean-reverting process.

#### Formula
```
dS_t = -λ × (S_t-1 - μ) + ε_t

or equivalently (demeaned):

dS_t = -λ × S_t-1 + ε_t

Half-life = ln(2) / λ
```

#### Derivation
```
For AR(1) process: S_t = (1 - λ) × μ + (1 - λ) × S_t-1 + ε_t

Solution: S_t = μ + (1 - λ)^t × (S_0 - μ)

At half-life: 0.5 = (1 - λ)^(HL)
Taking ln: ln(0.5) = HL × ln(1 - λ)
HL = ln(0.5) / ln(1 - λ) ≈ ln(2) / λ (for small λ)
```

#### Implementation
```python
halflife = pt.estimate_halflife(spread, method='ar1')
print(f"Half-life: {halflife:.2f} days")
```

#### Interpretation
- **HL < 5 days**: Very fast mean reversion (high frequency trading)
- **HL = 5-20 days**: Medium speed (typical pairs trading)
- **HL > 20 days**: Slow mean reversion (structural relationship)
- **HL = ∞**: Non-mean-reverting (broken cointegration)

---

### Method 2: Log-Decay Exponential Model

An alternative approach using exponential decay of spread magnitude.

#### Formula
```
|S_t| = A × exp(-b × t)

Taking ln: ln(|S_t|) = ln(A) - b × t

Half-life = ln(2) / b
```

#### Regression
```
ln(|S_t|) = α + β × t + ε_t

where β = -b, so:
Half-life = ln(2) / |β|
```

#### Implementation
```python
halflife = pt.estimate_halflife(spread, method='log_decay')
```

---

### Comparison of Methods

| Aspect | AR(1) | Log-Decay |
|--------|-------|-----------|
| **Model** | Autoregressive | Exponential |
| **Assumption** | Linear mean reversion | Exponential decay |
| **Robustness** | Sensitive to outliers | Robust |
| **Interpretation** | Probability-based | Direct decay rate |
| **Use Case** | Quick analysis | Detailed modeling |

---

## Signal Generation

### Trading Rules

Entry and exit signals are generated using z-score thresholds.

#### Entry Rules

**Long Entry Signal**
```
Position = LONG when Z_t < -Entry_Threshold

Interpretation: Spread below mean (Asset 1 cheap, Asset 2 expensive)
Expected: Mean reversion upward → Asset 1 price up, Asset 2 price down
```

**Short Entry Signal**
```
Position = SHORT when Z_t > Entry_Threshold

Interpretation: Spread above mean (Asset 1 expensive, Asset 2 cheap)
Expected: Mean reversion downward → Asset 1 price down, Asset 2 price up
```

#### Exit Rules

**Exit Signal**
```
Exit when |Z_t| < Exit_Threshold

Interpretation: Spread returned to mean or near equilibrium
Action: Close position to lock in profits or reduce losses
```

#### Typical Parameters

| Parameter | Recommended | Range | Meaning |
|-----------|-------------|-------|---------|
| **Entry Threshold** | 2.0 | 1.5 - 3.0 | Std devs to trigger entry |
| **Exit Threshold** | 0.5 | 0.2 - 1.0 | Std devs to trigger exit |
| **Stop Loss** | 3.0 | 2.5 - 4.0 | Std devs for forced exit |

### Implementation
```python
signals = pt.generate_signals(zscore,
                               entry_threshold=2.0,
                               exit_threshold=0.5)

# Returns:
# - long_entry: Boolean array of long entry signals
# - short_entry: Boolean array of short entry signals
# - exit: Boolean array of exit signals
```

### Signal Quality Metrics

| Metric | Calculation | Target |
|--------|-------------|--------|
| **Hit Ratio** | Winning trades / Total trades | > 50% |
| **Profit Factor** | Gross profit / Gross loss | > 1.5 |
| **Payoff Ratio** | Avg win / Avg loss | > 1.0 |
| **Signal Frequency** | Trades per year | Depends on HL |

---

## Portfolio Construction

### Market-Neutral Construction

A pairs trading portfolio is constructed to be market-neutral: equal long/short exposure.

#### Formula
```
Portfolio = Long(position_size × Asset1) + Short(hedge_ratio × position_size × Asset2)

Dollar Neutrality:
position_size × P1 = hedge_ratio × position_size × P2
```

#### Example
```
If P1 = $50, P2 = $100, hedge_ratio = 0.5, position_size = 100

Portfolio:
- Long 100 units of Asset 1 = $5,000
- Short 50 units of Asset 2 = $5,000

Net exposure = 0 (market neutral)
```

### Implementation
```python
portfolio = pt.construct_portfolio(prices1, prices2, hedge_ratio,
                                   position_size=1.0)

# Returns dictionary with:
# - asset1: Long position details
# - asset2: Short position details
# - net_value: Portfolio P&L
# - is_neutral: Whether portfolio is market neutral
```

### Risk Management

#### Position Sizing
```
position_size = capital × max_leverage / max(P1, P2)
```

#### Stop Loss
```
Exit if |Z_t| > 3.0 (3 standard deviations)
or if profit/loss exceeds pre-set limits
```

#### Correlation Monitoring
```
If correlation(Asset1_returns, Asset2_returns) < 0.5:
- Relationship may have broken
- Consider closing positions
```

---

## Implementation Details

### Data Requirements

1. **Minimum Data Length**: 2 × half-life (at least 40-100 observations)
2. **Data Frequency**: Daily or intraday (consistent)
3. **Data Quality**: No gaps, dividends adjusted
4. **Stationarity**: Both assets should be I(1) (non-stationary)

### Step-by-Step Implementation

```python
from pairs_trading import PairsTrading
import numpy as np

# 1. Initialize
pt = PairsTrading(confidence_level=0.95)

# 2. Pair Selection
distance = pt.distance_method(prices1, prices2)
correlation = pt.correlation_method(prices1, prices2)

if distance < threshold and correlation > 0.7:
    # 3. Cointegration Testing
    eg_result = pt.engle_granger_test(prices1, prices2)

    if eg_result['is_cointegrated']:
        # 4. Spread Analysis
        spread, hedge_ratio = pt.calculate_spread(prices1, prices2)
        zscore = pt.calculate_zscore(spread, lookback=20)

        # 5. Half-Life Estimation
        halflife = pt.estimate_halflife(spread)

        # 6. Signal Generation
        signals = pt.generate_signals(zscore, entry_threshold=2.0)

        # 7. Portfolio Construction
        portfolio = pt.construct_portfolio(prices1, prices2, hedge_ratio)

        # 8. Backtesting
        backtest = pt.backtest_strategy(prices1, prices2, signals, hedge_ratio)
```

### Performance Metrics

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| **Total Return** | (Final Value - Initial Value) / Initial Value | Overall P&L |
| **Sharpe Ratio** | (μ_r - r_f) / σ_r × √252 | Risk-adjusted return |
| **Max Drawdown** | min((Value - Peak) / Peak) | Worst loss period |
| **Win Rate** | Winning trades / Total trades | Consistency |
| **Profit Factor** | Gross profit / Gross loss | Profitability |

---

## Common Pitfalls and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| **Spurious correlation** | Non-stationary series | Test cointegration first |
| **Stale relationship** | Market regime change | Monitor correlation/halflife |
| **High transaction costs** | Frequent trading | Increase entry threshold |
| **Overfitting** | Too many parameters | Use validation set |
| **Look-ahead bias** | Using future data | Use walk-forward analysis |

---

## References

1. **Engle, R. F., & Granger, C. W. (1987)** - "Co-integration and Error Correction: Representation, Estimation and Testing"
2. **Johansen, S. (1988)** - "Statistical Analysis of Cointegration Vectors"
3. **Vidyamurthy, G. (2004)** - "Pairs Trading: Quantitative Methods and Analysis"
4. **Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006)** - "Pairs Trading: Performance of a Relative-Value Arbitrage Rule"

---

## Appendix: Statistical Tables

### MacKinnon Critical Values for ADF Test

| Confidence | n=25 | n=50 | n=100 | n=∞ |
|-----------|------|------|-------|-----|
| 90% | -2.63 | -2.60 | -2.58 | -2.57 |
| 95% | -2.95 | -2.93 | -2.89 | -2.86 |
| 99% | -3.58 | -3.50 | -3.45 | -3.43 |

### Johansen Critical Values (2 Assets)

| Significance | Trace | Eigenvalue |
|-------------|-------|-----------|
| 90% | 13.429 | 12.297 |
| 95% | 15.495 | 14.264 |
| 99% | 19.935 | 18.52 |

---

**Last Updated**: November 2025
**Module**: financial_apps/apps/quants/programs/pairs_trading.py
**Documentation**: financial_apps/apps/quants/methods/pairs_trading.md
