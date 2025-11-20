# Risk Management Guide

## Overview

Risk management is the quantitative framework for measuring and controlling portfolio losses. This guide covers the most important risk metrics: Value-at-Risk (VaR), Conditional Value-at-Risk (CVaR), Expected Shortfall, stress testing, scenario analysis, and correlation analysis.

**Key Concept**: Risk measurement bridges the gap between historical data and future uncertainty. No single metric is perfect; multiple complementary approaches are essential.

---

## Table of Contents

1. [Value-at-Risk (VaR)](#var-methods)
2. [CVaR and Expected Shortfall](#cvar)
3. [Stress Testing](#stress-testing)
4. [Scenario Analysis](#scenario-analysis)
5. [Correlation Analysis](#correlation-analysis)
6. [Advanced Topics](#advanced-topics)

---

## 1. Value-at-Risk (VaR) {#var-methods}

### 1.1 Definition and Interpretation

**Value-at-Risk (VaR)** answers the question: "What is the maximum loss with α% confidence over a time horizon?"

$$VaR_α = -\text{quantile}_α(R)$$

Where:
- α = significance level (e.g., 0.05 for 95% VaR)
- R = returns distribution
- Interpretation: With 95% confidence, daily loss will not exceed VaR

**Key Insight**: VaR is NOT an expected loss; it's a percentile of the loss distribution.

**Example**:
- Portfolio: $1,000,000
- 95% Daily VaR: 2%
- Dollar VaR: $20,000
- **Meaning**: 95% of the time, daily loss is less than $20,000; 5% of the time it's worse

---

### 1.2 Historical VaR

**Method**: Use empirical distribution of historical returns

$$VaR_α = -\text{quantile}_α(R_{\text{historical}})$$

**Advantages**:
- Makes no distribution assumptions
- Uses actual observed returns
- Captures empirical fat tails and skewness
- Easy to implement

**Disadvantages**:
- Requires large dataset (typically 500+ observations)
- Assumes past = future (regime changes?)
- Extreme events may not be in sample
- Quantile estimation error at tails

**Code**:
```python
from risk_management import RiskMetrics

risk = RiskMetrics(returns_data, confidence_level=0.95)
var_hist = risk.var_historical(portfolio_value=1000000)
print(f"95% Daily VaR: ${var_hist['Dollar_Loss']:.2f}")
```

**Mathematical Formula**:
```
1. Sort historical returns: R₁ ≤ R₂ ≤ ... ≤ Rₙ
2. Calculate index: i = ceil(n × α)
3. VaR = -Rᵢ
```

---

### 1.3 Parametric VaR - Normal Distribution

**Method**: Assume returns follow normal distribution N(μ, σ²)

$$VaR_{\text{normal}}(α) = -(\mu + σ × Φ^{-1}(α))$$

Where:
- μ = mean return
- σ = standard deviation
- Φ⁻¹(α) = inverse standard normal CDF at α

**Key Z-scores**:
| Confidence | α | Z-score |
|-----------|---|---------|
| 90% | 0.10 | -1.28 |
| 95% | 0.05 | -1.645 |
| 99% | 0.01 | -2.326 |
| 99.9% | 0.001 | -3.090 |

**Advantages**:
- Simple closed-form solution
- Fast computation
- Clear interpretation
- Works with limited data

**Disadvantages**:
- Assumes normality (fat tails underestimated)
- Ignores skewness and kurtosis
- Poor for extreme returns

**Code**:
```python
var_param = risk.var_parametric_normal(portfolio_value=1000000, period=1)
print(f"95% Daily Parametric VaR (Normal): ${var_param['Dollar_Loss']:.2f}")
```

**Comparison: Normal vs Historical**:
- Normal VaR < Historical VaR when data has fat tails (typical for equities)
- Normal distribution systematically underestimates tail risk

---

### 1.4 Parametric VaR - Student's t Distribution

**Method**: Assume returns follow Student's t distribution
Captures fat tails better than normal distribution

$$VaR_t(α) = -(\mu + σ × t_α^{-1}(df))$$

Where:
- t_α⁻¹(df) = inverse Student's t CDF with df degrees of freedom
- df estimated from kurtosis: $df = 6/K + 4$

**Key Features**:
- Extra parameter (df) captures tail heaviness
- Kurtosis (K) indicates departure from normality:
  - K = 3: normal distribution (df → ∞)
  - K = 4: heavy tails (df ≈ 6)
  - K = 8: very heavy tails (df ≈ 2.75)
- Typical equity returns: K = 5-8

**Advantages**:
- Better captures fat tails
- Adjusts automatically for kurtosis
- More accurate for extreme events

**Disadvantages**:
- More complex than normal
- df estimation introduces uncertainty
- Still assumes symmetric distribution

**Code**:
```python
var_t = risk.var_parametric_student_t(portfolio_value=1000000)
print(f"Student's t VaR: ${var_t['Dollar_Loss']:.2f}")
print(f"Degrees of Freedom: {var_t['Degrees_of_Freedom']}")
```

---

### 1.5 Parametric VaR - Cornish-Fisher

**Method**: Adjust normal VaR for skewness and kurtosis

$$z_{CF} = z_α + \frac{1}{6}z_α^2 S + \frac{1}{24}(z_α^3 - 3z_α)(K - 3) - \frac{1}{36}z_α^3 S^2$$

$$VaR_{CF} = -(\mu + σ × z_{CF})$$

Where:
- S = skewness (asymmetry of distribution)
- K = excess kurtosis (tail weight)
- z_α = standard normal quantile

**Interpretation**:
- **Positive skewness (S > 0)**: Right tail heavier → higher downside VaR
- **Negative skewness (S < 0)**: Left tail heavier → even higher downside VaR
- **High kurtosis (K > 0)**: Fat tails → higher VaR

**Typical Equity Returns**:
- S ≈ -0.5 to -0.3 (negative skew from crashes)
- K ≈ 3-8 (fat tails)

**Advantages**:
- Incorporates all higher moments
- More accurate than normal VaR for non-normal data
- Closed-form solution

**Disadvantages**:
- Assumes higher moments are stable (they're not)
- Higher moment estimation error with small samples
- More complex interpretation

**Code**:
```python
var_cf = risk.var_parametric_cornish_fisher(portfolio_value=1000000)
print(f"Cornish-Fisher VaR: ${var_cf['Dollar_Loss']:.2f}")
print(f"Skewness: {var_cf['Skewness']}, Kurtosis: {var_cf['Kurtosis']}")
```

---

### 1.6 Monte Carlo VaR

**Method**: Simulate future returns using geometric Brownian motion

$$dS/S = \mu dt + \sigma dW$$

$$S_T = S_0 × \exp\left((\mu - \sigma^2/2)T + \sigma\sqrt{T}Z\right)$$

Where Z ~ N(0,1) standard normal random variable

**Algorithm**:
1. Estimate μ and σ from historical data
2. Generate N random standard normal variables
3. Simulate returns: $R_i = \exp((\mu - \sigma^2/2)T + \sigma\sqrt{T}Z_i) - 1$
4. Calculate VaR as α-quantile of simulated returns

**Advantages**:
- Flexible: can model complex dynamics
- Can incorporate correlation between assets
- Captures path-dependent features
- Can add jumps, stochastic volatility, etc.

**Disadvantages**:
- Computationally intensive
- Results depend on μ and σ estimation
- Assumes GBM (not always realistic)
- Simulation error decreases as 1/√N

**Parameters**:
- **Number of simulations**: 10,000 typical, 100,000+ for high precision
- **Time horizon**: 1 day, 10 days, or 1 month common

**Code**:
```python
var_mc = risk.var_monte_carlo(
    portfolio_value=1000000,
    period=1,
    num_simulations=10000,
    seed=42
)
print(f"Monte Carlo VaR: ${var_mc['Dollar_Loss']:.2f}")
print(f"Simulated Mean: {var_mc['Mean_Simulated']:.4f}")
print(f"Simulated Std: {var_mc['Std_Simulated']:.4f}")
```

**Simulation Accuracy**:
- Standard error: $\sigma_{VaR}/\sqrt{N}$
- For 10,000 sims: ~1% of standard deviation
- For 100,000 sims: ~0.3% of standard deviation

---

### 1.7 Monte Carlo VaR with Historical Bootstrap

**Method**: Resample historical returns with replacement (non-parametric)

**Algorithm**:
1. Sample 'period' returns randomly from historical data with replacement
2. Compound returns: $R = \prod(1 + r_i) - 1$
3. Repeat N times to get distribution
4. Calculate VaR as α-quantile

**Advantages**:
- Non-parametric: no distribution assumptions
- Captures actual historical dependence
- No parameter estimation needed
- Robust to structural breaks

**Disadvantages**:
- Limited by historical data range
- Extreme new events not captured
- Assumes future = past distribution
- Can't extrapolate beyond historical extremes

**Code**:
```python
var_boot = risk.var_monte_carlo_historical_bootstrap(
    portfolio_value=1000000,
    period=1,
    num_simulations=10000
)
print(f"Bootstrap VaR: ${var_boot['Dollar_Loss']:.2f}")
```

---

### 1.8 Comparison of VaR Methods

| Method | Distribution | Pros | Cons | Use Case |
|--------|---|------|------|----------|
| **Historical** | Empirical | Non-param, fat tails | Needs data, no extrapolation | Baseline |
| **Normal** | Normal | Fast, simple | Ignores skew/kurt | Quick estimates |
| **Student's t** | Student's t | Fat tails | More complex | High kurtosis assets |
| **Cornish-Fisher** | Adjusted normal | Higher moments | Estimation error | Non-normal distributions |
| **Monte Carlo** | Custom | Flexible, copulas | Slow, estimation error | Complex portfolios |
| **Bootstrap** | Empirical | Non-param, realistic | Limited data | Robust estimates |

**Typical Finding**: Historical VaR > Parametric (normal) VaR > Student's t > Cornish-Fisher

---

## 2. CVaR and Expected Shortfall {#cvar}

### 2.1 Definition

**Conditional Value-at-Risk (CVaR)** or **Expected Shortfall (ES)** answers: "What is the average loss GIVEN that loss exceeds VaR?"

$$CVaR_α = E[L | L > VaR_α]$$

**Key Insight**: VaR says "90% chance loss < $100k"; CVaR says "if we're in that bad 10%, average loss is $150k"

**Advantages over VaR**:
1. **Coherent risk measure**: satisfies axioms of proper risk metrics
2. **Captures tail risk**: focuses on tail of distribution, not just quantile
3. **Subadditive**: $CVaR(A+B) ≤ CVaR(A) + CVaR(B)$ (diversification benefit)
4. **Better optimization**: convex, suitable for portfolio optimization

**Disadvantages**:
1. Harder to understand than VaR
2. More estimation error than VaR
3. More computationally intensive

---

### 2.2 Historical CVaR

**Method**: Average of returns worse than historical VaR

$$CVaR_α = \frac{1}{m} \sum_{i=1}^{m} R_i$$

Where $R_i$ are returns ≤ VaR (worst m observations)

**Algorithm**:
1. Calculate historical VaR at level α
2. Find all returns worse (more negative) than VaR
3. Calculate average of those tail returns

**Code**:
```python
cvar_hist = risk.cvar_historical(portfolio_value=1000000)
print(f"95% CVaR (Historical): ${cvar_hist['Dollar_Loss']:.2f}")
print(f"vs VaR: ${cvar_hist['VaR']:.4f}")
print(f"Tail observations: {cvar_hist['Observations_in_Tail']}")
```

**Typical CVaR/VaR Ratio**: 1.2-1.5 (CVaR is 20-50% worse than VaR)

---

### 2.3 Parametric CVaR - Normal Distribution

**Method**: Use theoretical relationship for normal distribution

$$CVaR_{\text{normal}}(α) = -\left(\mu + σ \frac{\phi(z_α)}{α}\right)$$

Where:
- φ(z_α) = standard normal PDF at z_α
- α = significance level

**Key Formula**: $\phi(z) = \frac{1}{\sqrt{2\pi}} \exp(-z^2/2)$

**Advantages**:
- Closed-form solution
- Fast computation
- Stable estimates

**Disadvantages**:
- Assumes normality (underestimates for fat tails)
- Same issues as normal VaR

**Code**:
```python
cvar_param = risk.cvar_parametric_normal(portfolio_value=1000000)
print(f"CVaR (Normal): ${cvar_param['Dollar_Loss']:.2f}")
```

---

### 2.4 Parametric CVaR - Student's t Distribution

**Method**: Use theoretical relationship for Student's t

$$CVaR_t(α) = -\left(\mu + σ \frac{t_{df}(t_α)}{α}\right)$$

Where:
- t_df(t_α) = Student's t PDF at t_α with df degrees of freedom
- More appropriate for fat-tailed data

**Code**:
```python
cvar_t = risk.cvar_parametric_student_t(portfolio_value=1000000)
print(f"CVaR (Student's t): ${cvar_t['Dollar_Loss']:.2f}")
```

---

### 2.5 Monte Carlo CVaR

**Method**: Average of Monte Carlo simulation tail returns

```python
cvar_mc = risk.cvar_monte_carlo(
    portfolio_value=1000000,
    num_simulations=10000
)
print(f"CVaR (Monte Carlo): ${cvar_mc['Dollar_Loss']:.2f}")
```

---

### 2.6 Expected Shortfall Properties

**Coherent Risk Measure**: A risk measure R is coherent if:

1. **Monotonicity**: If X ≤ Y, then R(X) ≥ R(Y)
   - Worse returns → higher risk
2. **Subadditivity**: R(X+Y) ≤ R(X) + R(Y)
   - Diversification reduces risk
3. **Positive Homogeneity**: R(λX) = λR(X) for λ > 0
   - Risk scales with portfolio size
4. **Translation Invariant**: R(X + r) = R(X) - r
   - Risk of cash-adjusted portfolio decreases

**VaR Properties**:
- ✓ Monotonicity
- ✗ Subadditivity (can increase with diversification!)
- ✓ Positive Homogeneity
- ✓ Translation Invariant

**CVaR/ES Properties**:
- ✓ Monotonicity
- ✓ Subadditivity ← Key advantage
- ✓ Positive Homogeneity
- ✓ Translation Invariant

---

## 3. Stress Testing {#stress-testing}

### 3.1 Absolute Shock Stress Test

**Question**: What is portfolio loss if market moves by X%?

$$\text{Loss} = \text{Portfolio Value} × \text{Shock Return}$$

**Common Scenarios**:
- Stock market: ±10%, ±20%, ±30%
- Bond market: ±100bp, ±200bp, ±300bp
- Currency: ±5%, ±10%, ±15%

**Code**:
```python
stress = risk.stress_test_absolute(
    stress_return=-0.10,  # -10% market move
    portfolio_value=1000000
)
print(f"Loss from -10% market move: ${stress['Loss']:.2f}")
```

---

### 3.2 Relative Stress Test (Sigma Multiples)

**Method**: Express stress as multiple of historical volatility

$$\text{Stress Return} = -k × \sigma$$

**Common Multiples**:
| Event | Sigma | Frequency |
|-------|-------|-----------|
| Normal day | 1σ | ~68% of time |
| Unusual day | 2σ | ~5% of time |
| Extreme event | 3σ | ~0.3% of time |
| Rare tail event | 4σ | ~0.003% of time |
| Historic crisis | 5-10σ | 2008, 1987 |

**Code**:
```python
stress = risk.stress_test_relative_to_historical(
    stress_multiple=3.0,  # 3-sigma event
    portfolio_value=1000000
)
print(f"3-sigma stress loss: ${stress['Loss']:.2f}")
print(f"Stress return: {stress['Stress_Return']:.4f}")
```

---

### 3.3 Historical Scenario Stress Test

**Method**: Analyze impact of worst historical days

**Common Scenarios**:
- Worst single day in sample
- 2008 Financial Crisis returns
- 2020 COVID crash
- 1987 Black Monday
- 2011 Flash Crash

**Code**:
```python
stress = risk.stress_test_historical_scenarios(
    portfolio_value=1000000,
    percentile_losses=[5, 10, 25]  # Worst 5%, 10%, 25%
)
for scenario, data in stress['Scenarios'].items():
    print(f"{scenario}: Loss ${data['Loss']:.2f}")
```

---

### 3.4 Correlation Breakdown Stress Test

**Concept**: During crisis, correlations increase (everything falls together)

**Typical Changes**:
- Normal correlation (stocks-bonds): -0.2 → -0.1 (less diversification)
- Normal correlation (stocks-stocks): 0.5 → 0.8 (increased systemic risk)
- Volatility increase: 1.5-3x normal (uncertainty rises)

**Code**:
```python
# Define normal and crisis correlations
normal_corr = np.array([
    [1.0, 0.3, 0.1],
    [0.3, 1.0, 0.0],
    [0.1, 0.0, 1.0]
])

crisis_corr = np.array([
    [1.0, 0.8, 0.5],
    [0.8, 1.0, 0.6],
    [0.5, 0.6, 1.0]
])

stress = risk.stress_test_correlation_breakdown(
    correlation_matrix=normal_corr,
    correlations_under_stress=crisis_corr,
    portfolio_weights=[0.4, 0.3, 0.3],
    stress_volatility_multiplier=2.0
)

print(f"Normal Portfolio Vol: {stress['Normal_Portfolio_Vol']:.4f}")
print(f"Stressed Portfolio Vol: {stress['Stressed_Portfolio_Vol']:.4f}")
```

---

### 3.5 Reverse Stress Test

**Question**: How bad must market move to hit acceptable loss limit?

$$\text{Required Return} = -\frac{\text{Acceptable Loss}}{\text{Portfolio Value}}$$

**Code**:
```python
reverse = risk.reverse_stress_test(
    acceptable_loss=50000,  # Max $50k loss
    portfolio_value=1000000
)
print(f"Required market move: {reverse['Required_Return_Percentage']:.2f}%")
print(f"In sigma terms: {reverse['Sigma_Move']:.2f}σ")
```

---

## 4. Scenario Analysis {#scenario-analysis}

### 4.1 Basic Scenario Analysis

**Method**: Define discrete scenarios and calculate portfolio impact

**Example Scenarios** (for stock portfolio):
```
Bull Case (30% probability):
  - GDP growth: 3%
  - Interest rates: ↑ 50bp
  - Stock return: +15%
  - Loss: -$150,000

Base Case (50% probability):
  - GDP growth: 2%
  - Interest rates: →
  - Stock return: +5%
  - Loss: -$50,000

Bear Case (20% probability):
  - Recession: -1% GDP
  - Interest rates: ↓ 100bp
  - Stock return: -15%
  - Loss: +$150,000
```

**Code**:
```python
scenarios = {
    'Bull_Case': 0.15,      # +15% return
    'Base_Case': 0.05,      # +5% return
    'Bear_Case': -0.15      # -15% return
}

analysis = risk.scenario_analysis(
    scenarios_dict=scenarios,
    portfolio_value=1000000
)

for scenario, details in analysis['Scenarios'].items():
    print(f"{scenario}: P&L = ${details['P&L']:.2f}")

print(f"Best case: ${analysis['Best_Case']:.2f}")
print(f"Worst case: ${analysis['Worst_Case']:.2f}")
print(f"Range: ${analysis['Case_Range']:.2f}")
```

---

### 4.2 Macro Scenario Analysis

**Method**: Combine macro drivers with asset sensitivities

**Framework**:
1. Define macro scenarios (recession, expansion, stagflation, etc.)
2. Assign probabilities to each scenario
3. Specify how each asset responds to each scenario
4. Calculate expected portfolio return

**Code**:
```python
macro_scenarios = {
    'Recession': 0.20,      # 20% probability
    'Slow_Growth': 0.50,    # 50% probability
    'Expansion': 0.30       # 30% probability
}

asset_sensitivities = {
    'Recession': {
        'Stocks': -0.20,    # Stocks down 20%
        'Bonds': 0.05,      # Bonds up 5%
        'Gold': 0.10        # Gold up 10%
    },
    'Slow_Growth': {
        'Stocks': 0.00,     # Neutral
        'Bonds': 0.02,      # Bonds up 2%
        'Gold': 0.01        # Gold up 1%
    },
    'Expansion': {
        'Stocks': 0.15,     # Stocks up 15%
        'Bonds': -0.03,     # Bonds down 3%
        'Gold': -0.05       # Gold down 5%
    }
}

macro_analysis = risk.scenario_analysis_macro(
    macro_scenarios_dict=macro_scenarios,
    asset_sensitivities=asset_sensitivities
)

print(f"Expected return: {macro_analysis['Expected_Return']:.4f}")
```

---

## 5. Correlation Analysis {#correlation-analysis}

### 5.1 Correlation Matrix and Covariance

**Key Metric**: How assets move together

$$\rho_{XY} = \frac{\text{Cov}(X,Y)}{\sigma_X \sigma_Y}$$

**Interpretation**:
- ρ = 1: Perfect positive correlation (move together)
- ρ = 0: No correlation (independent)
- ρ = -1: Perfect negative correlation (move opposite)

**Typical Correlations**:
| Pair | Normal | Crisis |
|------|--------|--------|
| Stock-Stock | 0.4-0.6 | 0.7-0.9 |
| Stock-Bond | -0.2-0.0 | -0.1-0.1 |
| Stock-Gold | -0.1-0.1 | 0.0-0.2 |
| Bond-Gold | 0.0-0.1 | 0.2-0.4 |

**Code**:
```python
asset_returns = {
    'Stock': returns_stock,
    'Bond': returns_bond,
    'Gold': returns_gold
}

corr_analysis = risk.correlation_analysis(asset_returns)

print("Correlation Matrix:")
print(corr_analysis['Correlation_Matrix'])
print(f"\nMean correlation: {corr_analysis['Mean_Correlation']:.4f}")
print(f"Min correlation: {corr_analysis['Min_Correlation']:.4f}")
print(f"Max correlation: {corr_analysis['Max_Correlation']:.4f}")
```

---

### 5.2 Correlation Breakdown During Crisis

**Phenomenon**: Correlations increase during market stress

**Evidence**:
- 2008 Financial Crisis: correlations jumped to 0.9+
- COVID-19: stock-bond correlation became positive
- 2011 Debt Crisis: European stocks highly correlated

**Code**:
```python
breakdown = risk.correlation_breakdown_analysis(
    asset_returns_dict=asset_returns,
    crisis_period_start='2008-08-01',
    crisis_period_end='2009-03-31'
)

print(f"Normal avg correlation: {breakdown['Normal_Correlation_Mean']:.4f}")
print(f"Crisis avg correlation: {breakdown['Crisis_Correlation_Mean']:.4f}")
print(f"Increase: {breakdown['Correlation_Increase']:.4f}")
```

---

### 5.3 Portfolio Risk Decomposition

**Question**: Which assets contribute most to portfolio risk?

$$\text{Risk Contribution}_i = w_i × \frac{\partial \sigma_p}{\partial w_i}$$

Where:
- w_i = weight of asset i
- σ_p = portfolio volatility

**Three Concepts**:
1. **Marginal Contribution to Risk (MCR)**: How much risk increases if we add 1% to asset
2. **Component Contribution to Risk (CCR)**: Weight × MCR
3. **Risk Contribution %**: Percentage of total portfolio risk

**Code**:
```python
decomp = risk.portfolio_risk_decomposition(
    asset_returns_dict=asset_returns,
    portfolio_weights={'Stock': 0.6, 'Bond': 0.3, 'Gold': 0.1}
)

print(f"Portfolio annual volatility: {decomp['Portfolio_Volatility']:.4f}")
print("\nRisk contribution by asset:")
for asset, contrib in decomp['Asset_Risk_Decomposition'].items():
    print(f"{asset}:")
    print(f"  Weight: {contrib['Weight']:.1%}")
    print(f"  Risk contribution: {contrib['Risk_Contribution_Pct']:.1f}%")
```

---

## 6. Advanced Topics {#advanced-topics}

### 6.1 VaR Backtesting

**Purpose**: Validate that VaR model is accurate

**Basel III Requirement**: Backtest VaR estimates against actual returns

**Procedure**:
1. Calculate 1-day 99% VaR each day (using data up to that point)
2. Compare to actual next-day return
3. Count "exceptions" (days when loss > VaR)
4. For 250 trading days at 99% confidence: expect ~2.5 exceptions

**Zones**:
| Exceptions | Assessment | Action |
|-----------|-----------|--------|
| 0-4 | Green | Model acceptable |
| 5-9 | Yellow | Investigate model |
| 10+ | Red | Model failure, increase capital |

---

### 6.2 Incremental VaR and Marginal VaR

**Marginal VaR**: Risk reduction from removing 1% of asset

$$\text{Marginal VaR}_i = \frac{\partial VaR_p}{\partial w_i}$$

**Incremental VaR**: Actual VaR change from position increase

$$\text{Incremental VaR} = VaR(\text{portfolio + position}) - VaR(\text{portfolio})$$

---

### 6.3 Factor-Based Risk

**Concept**: Decompose portfolio risk by risk factors

**Factors**: Market beta, value, size, momentum, quality, volatility

**Benefits**:
- Understand risk sources
- Hedge systematically
- Integrate with performance attribution

---

### 6.4 Tail Risk and Extreme Value Theory

**Concept**: Model extreme events using extreme value theory (EVT)

**Methods**:
1. Peak-Over-Threshold (POT): Model returns above threshold
2. Generalized Pareto Distribution (GPD): Fit distribution to tail

**Application**: Better estimates of tail quantiles (VaR) for rare events

---

## 7. Practical Implementation Guide

### 7.1 Workflow for Daily Risk Reporting

```python
from risk_management import RiskMetrics

# 1. Load data
returns = pd.read_csv('daily_returns.csv', index_col='Date')['Return']

# 2. Initialize risk metrics
risk = RiskMetrics(returns, confidence_level=0.95)

# 3. Calculate risk metrics
var_h = risk.var_historical(portfolio_value=100_000_000)
cvar_h = risk.cvar_historical(portfolio_value=100_000_000)

# 4. Generate report
summary = risk.risk_metrics_summary(portfolio_value=100_000_000)

# 5. Format output
print(f"Portfolio Value: ${100_000_000:,.0f}")
print(f"95% Daily VaR: ${var_h['Dollar_Loss']:,.0f}")
print(f"95% Daily CVaR: ${cvar_h['Dollar_Loss']:,.0f}")
print(f"Annual Volatility: {summary['Annual_Volatility']:.2%}")
print(f"Sharpe Ratio: {summary['Sharpe_Ratio']:.2f}")
```

---

### 7.2 Multi-Asset Portfolio Risk

```python
from risk_management import calculate_portfolio_var

# Asset returns
returns_dict = {
    'SPY': returns_stocks,
    'AGG': returns_bonds,
    'GLD': returns_gold
}

# Portfolio weights
weights = {
    'SPY': 0.60,
    'AGG': 0.30,
    'GLD': 0.10
}

# Calculate portfolio VaR
portfolio_risk = calculate_portfolio_var(
    returns_dict=returns_dict,
    weights=weights,
    confidence_level=0.95
)

print(f"Portfolio VaR: {portfolio_risk['Portfolio_VaR_Historical']:.4f}")
print(f"Portfolio CVaR: {portfolio_risk['Portfolio_CVaR_Historical']:.4f}")
```

---

### 7.3 Comparison of VaR Methods

```python
from risk_management import compare_var_methods

comparison = compare_var_methods(
    returns_data=returns,
    portfolio_value=1000000,
    confidence_level=0.95
)

print(comparison)
```

---

## 8. Model Selection and Best Practices

### 8.1 Which VaR Method to Use?

| Situation | Recommended Method | Reasoning |
|-----------|-------------------|-----------|
| Quick estimate | Parametric Normal | Fast, simple |
| Non-normal data | Cornish-Fisher | Adjusts for higher moments |
| Fat tails | Student's t or Historical | Captures tail risk |
| Complex portfolio | Monte Carlo | Flexible, handles correlations |
| Limited data | Bootstrap | Non-parametric, robust |
| Production system | Multiple methods | Compare for validation |

---

### 8.2 Best Practices

**Data**:
- Use at least 250-500 observations (1-2 years)
- Handle outliers carefully (investigate, don't remove)
- Account for structural breaks (regime changes)

**Estimation**:
- Update models regularly (daily, weekly, or monthly)
- Use rolling windows for time-varying parameters
- Backtest against actual returns

**Reporting**:
- Report multiple VaR estimates, not just one
- Include confidence intervals
- Explain limitations and assumptions
- Compare to historical extremes

**Risk Management**:
- Use CVaR/ES in addition to VaR
- Combine with stress testing
- Include scenario analysis
- Monitor correlations and tail risk

---

## 9. Key References

### Foundational Papers

1. **Jorion, P. (2007)** - "Value at Risk: The New Benchmark for Managing Financial Risk"
   - Comprehensive textbook on VaR

2. **Rockafellar, R. T., & Uryasev, S. (2000)** - "Optimization of Conditional Value-at-Risk"
   - CVaR optimization theory

3. **Embrechts, P., Klüppelberg, C., & Mikosch, T. (1997)** - "Modelling Extremal Events"
   - Extreme value theory for tails

4. **Basel Committee (2006)** - "International Convergence of Capital Measurement and Capital Standards"
   - Basel II, VaR for regulatory capital

5. **Basel Committee (2019)** - "Minimum Capital Requirements for Market Risk"
   - Basel III, updated VaR framework

### Key Concepts

- **Coherent Risk Measures**: Artzner et al. (1999)
- **Conditional VaR**: Rockafellar & Uryasev (2000)
- **Expected Shortfall**: Acerbi & Tasche (2002)
- **Correlation Breakdown**: Longin & Solnik (2001)

---

## 10. Limitations and Warnings

### Known Issues

1. **VaR is not tail-focused**: Ignores severity beyond quantile
2. **Parameter estimation error**: Small-sample bias, especially in tails
3. **Model risk**: Wrong model choice → wrong risk estimate
4. **Correlation assumptions**: Often unstable, especially in crisis
5. **Back-testing challenges**: Need many years of extreme event data
6. **Regime changes**: Past relationships break during structural changes

### When VaR Fails

- **2008 Financial Crisis**: VaR models severely underestimated risk
- **COVID-19 Crash (March 2020)**: Correlations jumped; diversification failed
- **Flash Crashes**: Sudden liquidity events not captured by models
- **Leverage effects**: When portfolios are levered, losses exceed expectations

### Solution: Multi-Method Approach

Always use:
1. Historical VaR (actual observed losses)
2. Parametric VaR (distribution-based)
3. CVaR/ES (tail-focused)
4. Stress testing (scenario-based)
5. Back-testing (validation)

---

## 11. Implementation Checklist

- [ ] Calculate historical returns
- [ ] Check for outliers and data quality
- [ ] Calculate VaR using multiple methods
- [ ] Calculate CVaR/ES
- [ ] Perform stress tests (historical scenarios)
- [ ] Analyze correlation structure
- [ ] Check for correlation breakdown in crisis periods
- [ ] Run scenario analysis
- [ ] Back-test VaR estimates
- [ ] Document assumptions and limitations
- [ ] Set up monitoring and alerts
- [ ] Update models periodically

---

## 12. Quick Start Example

```python
import pandas as pd
from risk_management import RiskMetrics

# Load returns data
returns = pd.read_csv('data.csv')['returns']

# Initialize with 95% confidence
risk = RiskMetrics(returns, confidence_level=0.95)

# Calculate comprehensive metrics
summary = risk.risk_metrics_summary(portfolio_value=1_000_000)

# Stress tests
stress1 = risk.stress_test_absolute(stress_return=-0.10)
stress2 = risk.stress_test_relative_to_historical(stress_multiple=2.0)

# Scenario analysis
scenarios = {
    'Downturn': -0.15,
    'Normal': 0.05,
    'Rally': 0.15
}
scenario = risk.scenario_analysis(scenarios)

print(summary)
print(stress1)
print(scenario)
```

---

**Last Updated**: 2024
**Author**: Quantitative Risk Management
**Status**: Production-Ready
