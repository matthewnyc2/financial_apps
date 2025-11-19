# Volatility Modeling Guide

## Overview

Volatility is a critical input for pricing derivatives, risk management, and portfolio optimization. This guide covers the most important volatility modeling techniques: GARCH variants, realized volatility, and volatility-based trading strategies.

**Key Concept**: Volatility is not constant - it exhibits clustering (high volatility today tends to follow high volatility yesterday) and mean reversion.

---

## 1. GARCH Models

### 1.1 GARCH(1,1) - Standard Model

**Definition**: Generalized Autoregressive Conditional Heteroscedasticity

$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

Where:
- **ω (omega)**: Long-run variance component (constant)
- **α (alpha)**: ARCH effect - reaction to past shocks, immediate impact
- **β (beta)**: GARCH effect - persistence of volatility, memory effect
- **σ²_t**: Conditional variance at time t
- **ε_t**: Standardized returns (residuals)

**Interpretation**:
- Larger **α**: Volatility is more sensitive to recent surprises (shocks)
- Larger **β**: Volatility persistence; impact of past volatility lasts longer
- **α + β** (persistence):
  - If < 1: Mean-reverting (stable)
  - If ≥ 1: Explosive or unit root (unstable)
  - Typical value: 0.95-0.99 (highly persistent)

**Estimation Method**: Maximum Likelihood Estimation (MLE)

**Code**:
```python
from volatility_models import VolatilityModels

vol_model = VolatilityModels(returns_data)
garch_fit = vol_model.fit_garch11_normal()
garch_fit.summary()
```

---

### 1.2 GARCH(1,1) with Student's t Distribution

**Motivation**: Equity returns exhibit fat tails (kurtosis > 3)
- Normal distribution underestimates tail risk
- Student's t distribution better captures extreme events

**Code**:
```python
garch_t = vol_model.fit_garch11_studentt()
```

**Advantage**: More robust to large price movements

---

### 1.3 GARCH(p,q) Extensions

**GARCH(2,1)**: Higher-order ARCH terms capture more complex dynamics
$$\sigma_t^2 = \omega + \alpha_1 \epsilon_{t-1}^2 + \alpha_2 \epsilon_{t-2}^2 + \beta \sigma_{t-1}^2$$

**Trade-off**: More parameters → better fit but higher estimation error and overfitting risk

---

## 2. EGARCH - Exponential GARCH

### 2.1 Motivation for Asymmetry

**Problem with GARCH**: Treats positive and negative shocks identically
- Reality: Negative shocks (bad news) → larger volatility increase
- This is the **leverage effect**

**EGARCH Solution**: Asymmetric volatility response

$$\log(\sigma_t^2) = \omega + \beta \log(\sigma_{t-1}^2) + \gamma \left[\frac{\epsilon_{t-1}}{\sigma_{t-1}}\right] + \lambda \left[\left|\frac{\epsilon_{t-1}}{\sigma_{t-1}}\right| - E\left|\frac{\epsilon_{t-1}}{\sigma_{t-1}}\right|\right]$$

### 2.2 Key Parameters

- **γ (gamma)**: Leverage effect coefficient
  - γ < 0: Negative shocks increase volatility more
  - Typical value: -0.1 to -0.3

- **λ (lambda)**: Size effect (symmetric shock response)
  - Positive λ: Larger absolute shocks → higher volatility

- **β (beta)**: Persistence of log-volatility

### 2.3 Advantages Over GARCH

1. **No positivity constraints** on parameters
2. **Captures asymmetry** inherent in financial data
3. **Leverage effect** modeled explicitly
4. **Usually lower AIC/BIC** than GARCH(1,1)

**Code**:
```python
egarch_fit = vol_model.fit_egarch()
```

---

## 3. GJR-GARCH - The Glosten-Jagannathan-Runkle Model

### 3.1 Leverage Effect Modeling

$$\sigma_t^2 = \omega + (\alpha + \gamma I_{t-1}) \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$

Where $I_{t-1} = 1$ if $\epsilon_{t-1} < 0$ (bad news), else 0

### 3.2 Interpretation

- **Bad news impact**: $(\alpha + \gamma)$ coefficient
- **Good news impact**: $\alpha$ coefficient
- **Asymmetry measure**: $\gamma$ > 0
  - Typically: 0.05-0.15 (bad news has 5-15% larger impact)

### 3.3 Advantages

- Intuitive: directly separates good/bad news
- Computationally simpler than EGARCH
- No log transformation needed

**Code**:
```python
gjr_fit = vol_model.fit_gjr_garch()
```

---

## 4. Realized Volatility

### 4.1 Simple Realized Volatility

$$RV_t = \sqrt{\sum_{i=1}^{n} r_{t,i}^2}$$

Where r_{t,i} are high-frequency returns (e.g., 5-minute returns)

**Advantages**:
- Model-free, observable from actual returns
- More accurate than close-to-close volatility
- Captures intraday price movements

**Code**:
```python
rv = vol_model.realized_volatility_simple(window=20)
```

---

### 4.2 Parkinson (1980) Estimator

$$RV_{Parkinson} = \sqrt{\frac{1}{4 \ln(2)} \ln\left(\frac{H}{L}\right)^2}$$

**Advantages**:
- Uses intraday high-low prices
- 4-5x more efficient than close-to-close
- No need for high-frequency data

**Best For**: Daily volatility estimation when only OHLC available

**Code**:
```python
rv_park = vol_model.realized_volatility_parkinson(high_low_data)
```

---

### 4.3 Garman-Klass (1980) Estimator

$$RV_{GK} = \sqrt{0.5 \ln\left(\frac{H}{L}\right)^2 - (2 \ln 2 - 1) \ln\left(\frac{C}{O}\right)^2}$$

**Advantages**:
- Even more efficient than Parkinson
- Handles opening gaps
- 7-8x more efficient than close-to-close

**Best For**: Maximum precision with OHLC data

**Code**:
```python
rv_gk = vol_model.realized_volatility_garman_klass(ohlc_data)
```

---

### 4.4 Rogers-Satchell (1991) Estimator

$$RV_{RS} = \sqrt{HO \cdot LC + HO^2 + LC^2}$$

Where HO = ln(H/O), LC = ln(L/C)

**Key Feature**: Unaffected by opening gaps and jumps
**Use Case**: Assets with significant overnight gaps (e.g., commodities)

---

## 5. Implied Volatility

### 5.1 Definition

Volatility implied by option prices using the Black-Scholes model

$$C = S_0 N(d_1) - K e^{-rT} N(d_2)$$

**Inverse Problem**: Given option price, solve for σ that produces that price

**Key Insight**: Implied vol is market's expectation of future realized volatility

---

### 5.2 VIX Index

- **Definition**: 30-day implied volatility of S&P 500
- **Calculation**: Weighted average of put and call option IVs
- **Range**: Typically 10-50 (measured in percentage points)
- **Interpretation**:
  - VIX > 30: Elevated fear/stress
  - VIX < 15: Complacency, low expected volatility
  - Mean: ~19 (historically)

---

## 6. Realized vs Implied Volatility

### 6.1 Key Differences

| Aspect | Realized Volatility | Implied Volatility |
|--------|-------------------|-------------------|
| **Source** | Historical prices | Option prices |
| **Type** | Backward-looking | Forward-looking |
| **Information** | What happened | What market expects |
| **Lag** | Real-time available | Depends on liquid options |
| **Efficiency** | Observable | Market expectation |

### 6.2 IV-RV Spread

**Definition**: $\text{IV Risk Premium} = IV - RV$

**Trading Implications**:
- **IV > RV**: Market fears more volatility than history suggests → **Sell volatility**
- **IV < RV**: Market underestimating volatility → **Buy volatility**

---

## 7. Volatility Forecasting

### 7.1 One-Step Ahead Forecast

$$\hat{\sigma}_{t+1|t}^2 = \omega + \alpha \epsilon_t^2 + \beta \sigma_t^2$$

Simply plug in current values to get tomorrow's expected variance

**Code**:
```python
forecast = vol_model.forecast_volatility(garch_fit, horizon=1)
```

---

### 7.2 Multi-Step Ahead Forecast

$$\hat{\sigma}_{t+h|t}^2 = \omega(1 - \beta^{h-1}) + \beta^{h-1} \sigma_{t+1|t}^2$$

As h → ∞, forecast converges to long-run variance $\bar{\sigma}^2 = \omega/(1-\alpha-\beta)$

**Characteristics**:
- **Mean reversion**: Variance forecasts converge to steady-state
- **Uncertainty increases** with forecast horizon
- **Useful for**: Derivative pricing, VaR estimation

**Code**:
```python
forecast_5day = vol_model.forecast_volatility_parametric(garch_fit, horizon=5)
```

---

## 8. VIX-Based Trading Strategies

### 8.1 Volatility Mean Reversion Strategy

**Intuition**: Volatility reverts to long-term mean; extremes are trading opportunities

**Signal Generation**:
```
IF IV/RV Ratio is HIGH (>75th percentile):
  → Market pricing in too much vol → SELL VOLATILITY
  → Long positions: VXX puts, short straddles, short calls

IF IV/RV Ratio is LOW (<25th percentile):
  → Market underpricing vol → BUY VOLATILITY
  → Long positions: VXX calls, long straddles, long calls
```

**Historical Performance**: Profitable in normal markets; losses during crisis periods

**Code**:
```python
signals = vol_model.vol_mean_reversion_strategy(
    realized_vol, implied_vol,
    long_threshold=0.25,
    short_threshold=0.75
)
```

---

### 8.2 Volatility Clustering Strategy

**Intuition**: High volatility today → High volatility tomorrow (persistence)

**Signal Generation**:
```
IF Conditional Volatility > 75th percentile:
  → Expect continued high volatility
  → BUY VOLATILITY

IF Conditional Volatility < 25th percentile:
  → Expect low volatility to persist
  → SELL VOLATILITY
```

**Implementation**:
- Use GARCH-forecast volatility as signal
- Trade VIX products or volatility-sensitive assets
- Exit when volatility mean-reverts

**Code**:
```python
signals = vol_model.vol_clustering_strategy(
    garch_fit, threshold_percentile=75
)
```

---

### 8.3 Volatility Surface Strategies

**Concept**: Analyze IV across different maturities and strikes

**Calendar Spread**: Trade near-term vs far-term volatility
```
IF Near-term IV >> Far-term IV:
  → Short near-term vol / Long far-term vol
  → Profit if near-term vol mean-reverts down

IF Near-term IV << Far-term IV:
  → Long near-term vol / Short far-term vol
  → Profit if near-term vol rises toward term structure
```

---

## 9. Model Selection

### 9.1 Information Criteria

**AIC (Akaike Information Criterion)**:
$$\text{AIC} = 2k - 2 \ln(L)$$

**BIC (Bayesian Information Criterion)**:
$$\text{BIC} = k \ln(n) - 2 \ln(L)$$

Where k = parameters, n = observations, L = likelihood

**Decision Rule**: Lower AIC/BIC = better model

**Code**:
```python
results, comparison = compare_garch_variants(returns_pct)
# Compare AIC, BIC across models
```

---

### 9.2 Selection Guidelines

| Model | Best For | Complexity |
|-------|----------|-----------|
| **GARCH(1,1) Normal** | Baseline, large datasets | Simple |
| **GARCH(1,1) StudentT** | Fat-tail data, tail risk | Low |
| **EGARCH(1,1)** | Leverage effects, asymmetry | Medium |
| **GJR-GARCH(1,1,1)** | Leverage with simplicity | Medium |
| **GARCH(2,1)** | Complex dynamics, more data | Higher |

---

## 10. Model Diagnostics

### 10.1 Standardized Residuals Tests

**Properties of Good Model**:
1. Mean ≈ 0 (no bias)
2. Std Dev ≈ 1 (properly scaled)
3. Uncorrelated (no remaining serial correlation)
4. No remaining ARCH effects
5. Normally distributed (ideally)

**Code**:
```python
diagnostics = vol_model.residuals_analysis(garch_fit)
# Mean, Std Dev, Skewness, Kurtosis, Jarque-Bera
```

### 10.2 Persistence Check

$$\alpha + \beta < 1 \quad \text{(Stability condition)}$$

If **α + β ≥ 1**: Model implies explosive volatility (unrealistic)

**Code**:
```python
vol_model.model_diagnostics(garch_fit)
# Prints persistence and stability assessment
```

---

## 11. Practical Implementation

### 11.1 Step-by-Step Workflow

```python
from volatility_models import VolatilityModels
import pandas as pd

# 1. Load returns data
returns = pd.read_csv('returns.csv', index_col='Date')['Return']

# 2. Initialize model
vol_model = VolatilityModels(returns)

# 3. Fit multiple models
garch_fit = vol_model.fit_garch11_normal()
egarch_fit = vol_model.fit_egarch()
gjr_fit = vol_model.fit_gjr_garch()

# 4. Compare models
vol_model.model_diagnostics(garch_fit)
vol_model.residuals_analysis(garch_fit)

# 5. Generate forecasts
forecast_vol = vol_model.forecast_volatility(garch_fit, horizon=5)
cond_vol = vol_model.conditional_volatility(garch_fit)

# 6. Calculate realized vol
realized_vol = vol_model.realized_volatility_simple(window=20)

# 7. Build trading signals
signals = vol_model.vol_clustering_strategy(garch_fit)
```

---

### 11.2 Backtesting Framework

```python
# 1. Generate signal
signal = signals['Signal'].shift(1)  # Use yesterday's signal today

# 2. Calculate forward returns
forward_returns = returns.shift(-1)

# 3. Calculate PnL
pnl = signal * forward_returns

# 4. Evaluate
total_return = pnl.sum()
sharpe = pnl.mean() / pnl.std() * np.sqrt(252)
max_dd = (pnl.cumsum()).min()
```

---

## 12. Key References

### Papers

1. **Bollerslev, T. (1986)** - "Generalized autoregressive conditional heteroskedasticity"
   - Original GARCH paper, foundational work

2. **Nelson, D. B. (1991)** - "Conditional heteroskedasticity in asset returns: A new approach"
   - Original EGARCH paper, leverage effects

3. **Glosten, L. R., Jagannathan, R., & Runkle, D. E. (1993)** - "On the relation between expected value and the volatility of the nominal excess return on stocks"
   - GJR-GARCH model

4. **Parkinson, M. (1980)** - "The extreme value method for estimating the variance of the rate of return"
   - Parkinson volatility estimator

5. **Garman, M. B., & Klass, M. J. (1980)** - "On the estimation of security price volatilities from historical data"
   - Garman-Klass estimator

6. **Rogers, L. C., & Satchell, S. E. (1991)** - "Estimating variance from high, low and closing prices"
   - Rogers-Satchell estimator

### Textbooks

- **Francq, C., & Zakoïan, J. M. (2019)** - "GARCH Models: Structure, Statistical Inference and Financial Applications" (2nd Ed.)
- **Hamilton, J. D. (1994)** - "Time Series Analysis" (chapters on heteroscedasticity)

---

## 13. Implementation Best Practices

### 13.1 Data Preparation

- **Frequency**: Use daily closing prices for GARCH fitting
- **Minimum observations**: 500+ data points (2+ years) for stability
- **Missing data**: Handle appropriately (forward fill or remove)
- **Outliers**: Investigate extreme returns; don't automatically remove

### 13.2 Model Fitting

- **Scale consistency**: arch library expects returns in percentages
- **Optimization**: Use robust initial values; check convergence
- **Constraints**: Ensure positivity for GARCH, stability for all models

### 13.3 Forecasting

- **Update frequency**: Refit model periodically (weekly/monthly)
- **Rolling window**: Use expanding or rolling window estimation
- **Uncertainty**: Report confidence intervals, not just point estimates

### 13.4 Trading Implementation

- **Slippage**: Account for transaction costs in backtests
- **Look-ahead bias**: Use only information available at signal time
- **Regime changes**: Monitor for structural breaks in vol behavior
- **Leverage**: Volatility strategies often require leverage (managed carefully)

---

## 14. Limitations and Considerations

### GARCH Limitations

1. **Assumes normal/t distribution**: Real returns have more complex distributions
2. **Parameter instability**: Relationships change over time
3. **Slow reaction to structural breaks**: Takes time to adapt to new regimes
4. **Estimation risk**: With many parameters, small-sample errors are large

### Forecasting Challenges

1. **Mean reversion speed**: Varies with economic regime
2. **Extreme events**: Models typically underestimate tail probabilities
3. **Regime changes**: Volatility behavior during crises differs markedly

### Trading Strategy Risks

1. **Crowded trades**: If many use same signals, less profitable
2. **Crisis periods**: Volatility strategies often underperform in crises
3. **Liquidity**: VIX products can be illiquid
4. **Jump risk**: Continuous models don't capture sudden jumps well

---

## 15. Extensions and Future Work

### Advanced Topics

- **Multivariate GARCH**: Model correlation dynamics between assets
- **Jump models**: Combine GARCH with jump processes
- **Realized GARCH**: Combine realized volatility with model volatility
- **Machine Learning**: Neural networks for volatility prediction
- **Copula models**: Non-linear dependence structures

### Recent Developments

- **High-frequency data**: Use tick-level data for better estimates
- **Cryptocurrency volatility**: Adapt models for 24/7 trading
- **Options-implied**: Fusion of implied and realized approaches

---

**Last Updated**: 2024
**Author**: Quantitative Analytics
**Status**: Production-Ready
