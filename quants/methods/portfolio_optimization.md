# Portfolio Optimization Methods

## Overview

This document describes five core portfolio optimization methodologies implemented in `portfolio_optimization.py`. Each method represents a different approach to constructing optimal asset allocations.

---

## 1. Mean-Variance Optimization (Markowitz)

### Theory

The Markowitz Mean-Variance model is the foundational portfolio optimization framework. It constructs portfolios that either:
- **Minimize variance** for a target return, or
- **Maximize Sharpe ratio** for optimal risk-adjusted returns

**Mathematical Formulation:**

```
Minimize: w^T * Σ * w
Subject to:
  w^T * μ = R_target  (target return constraint)
  Σ w_i = 1           (weights sum to 1)
  w_i >= 0            (long-only constraint, optional)
```

Where:
- `w` = portfolio weights
- `Σ` = covariance matrix
- `μ` = expected returns vector
- `R_target` = target portfolio return

**Sharpe Ratio Maximization:**

```
Maximize: (w^T * μ - r_f) / √(w^T * Σ * w)
Where r_f = risk-free rate
```

### Implementation Details

- Uses Sequential Least Squares Programming (SLSQP) optimizer
- Can enforce long-only constraints (weights ≥ 0)
- Generates efficient frontier by optimizing multiple target returns
- Returns Sharpe ratio as metric of risk-adjusted performance

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `target_return` | None | Target portfolio return; if None, maximizes Sharpe ratio |
| `risk_free_rate` | 0.02 | Risk-free rate for Sharpe calculation |
| `long_only` | True | Enforce non-negative weights |

### Usage Example

```python
from portfolio_optimization import MeanVarianceOptimizer

# Create optimizer with historical returns
mv = MeanVarianceOptimizer(returns, asset_names)

# Maximize Sharpe ratio
result = mv.optimize()
print(result['weights'])           # Optimal weights dict
print(result['sharpe_ratio'])      # Sharpe ratio

# Generate efficient frontier
frontier = mv.efficient_frontier(n_points=50)
```

---

## 2. Black-Litterman Model

### Theory

The Black-Litterman model addresses a key limitation of Markowitz optimization: extreme concentration in risky assets. It combines:
1. **Market equilibrium returns** (derived from market weights via reverse optimization)
2. **Investor views** (subjective forecasts with confidence levels)

**Key Insight:** Instead of using raw historical returns (which may be unstable), BL uses market-implied returns from equilibrium as the starting point.

**Reverse Optimization:**

```
π = δ * Σ * w_market

Where:
- π = market-implied excess returns
- δ = risk aversion coefficient (typically 2-4)
- Σ = covariance matrix
- w_market = market capitalization weights
```

**View Incorporation:**

The posterior expected returns combine market equilibrium with investor views:

```
Posterior Return = Confidence * View_Return + (1 - Confidence) * Market_Return
```

### Implementation Details

- Initializes with market-implied returns (equal weight if no market caps provided)
- Incorporates multiple investor views with confidence levels
- Performs final optimization on posterior returns
- More stable than raw Markowitz, less concentrated allocations

### Key Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `market_cap_weights` | None | Market capitalization weights; equal weight if None |
| `risk_free_rate` | 0.02 | Risk-free rate |
| `views` | None | List of dicts with 'assets' and 'return' keys |
| `confidence` | 0.5 | Confidence in views (0-1 scale) |

### Usage Example

```python
from portfolio_optimization import BlackLittermanOptimizer

bl = BlackLittermanOptimizer(returns, asset_names=asset_names)

# Define views: assets 0,1 expected to return 12%
views = [
    {'assets': [0, 1], 'return': 0.12}
]

result = bl.update_with_views(views, confidence=0.6)
print(result['posterior_returns'])  # Updated expected returns
print(result['weights'])            # BL-optimized weights
```

---

## 3. Risk Parity Allocation

### Theory

Risk Parity constructs portfolios where each asset contributes **equally to total portfolio risk**, regardless of individual asset volatility. This approach addresses the tendency of Markowitz portfolios to be heavily concentrated in low-volatility assets.

**Core Principle:**

```
Risk Contribution_i = w_i * (Σ * w)_i / √(w^T * Σ * w)
Target: Risk Contribution_i = 1/N for all assets
```

**Inverse Volatility Starting Point:**

```
w_i^initial = (1 / σ_i) / Σ(1 / σ_j)
```

### Implementation Details

- Starts with inverse volatility approximation
- Iteratively refines weights to equalize risk contributions
- Converges within 10-20 iterations typically
- Produces well-diversified portfolios resistant to volatility shocks

### Key Advantages

✓ Avoids concentration in low-volatility assets
✓ Provides diversification across risk factors
✓ Robust to estimation errors in returns
✓ Simple to compute and rebalance

### Usage Example

```python
from portfolio_optimization import RiskParityOptimizer

rp = RiskParityOptimizer(returns, asset_names)
result = rp.optimize()

print(result['weights'])            # Risk parity weights
print(result['risk_contributions']) # Risk contribution per asset
```

---

## 4. Hierarchical Risk Parity (HRP)

### Theory

Hierarchical Risk Parity (HRP) uses hierarchical clustering on asset correlations to build the portfolio from the "top down". This method combines the diversification benefits of risk parity with the portfolio construction discipline of hierarchical clustering.

**Algorithm:**

```
1. Compute distance matrix: D_ij = √((1 - ρ_ij) / 2)
   Where ρ_ij = correlation between assets i,j

2. Perform hierarchical clustering (Ward linkage):
   Group similar assets together based on correlations

3. Recursive bisection:
   - Start with all assets as one cluster
   - Recursively split into sub-clusters
   - Allocate capital inversely proportional to sub-cluster volatility
   - Repeat until individual assets reached
```

### Implementation Details

- Uses Ward linkage for hierarchical clustering
- Allocates weights recursively from portfolio root
- More stable than risk parity to correlation shocks
- Produces diversified portfolios without quadratic programming

### Key Advantages

✓ No optimization needed (non-parametric)
✓ Avoids concentration from correlation matrix estimation errors
✓ Naturally diversifies across correlation structures
✓ Computationally efficient
✓ Produces more stable allocations than Markowitz

### Usage Example

```python
from portfolio_optimization import HierarchicalRiskParityOptimizer

hrp = HierarchicalRiskParityOptimizer(returns, asset_names)
result = hrp.optimize()

print(result['weights'])       # HRP-optimized weights
print(result['linkage_matrix']) # Clustering structure
```

---

## 5. Kelly Criterion Position Sizing

### Theory

The Kelly Criterion determines optimal bet sizing to maximize long-term portfolio growth. Originally developed for gambling, it applies directly to portfolio management by determining what fraction of capital should be allocated to each asset.

**Kelly Criterion Formula:**

```
f* = (p * E[R] - (1-p)) / E[R]^2

Or for portfolios:
f_i = Kelly Fraction for Asset i
    = (p_i * E[R_i] / σ_i) / 1

Where:
- p_i = probability of positive return
- E[R_i] = expected return
- σ_i = volatility (standard deviation)
```

**Equivalent to:**

```
f* = (Expected Payoff) / (Odds)
   = (p * b - q) / b

Where:
- p = win probability
- q = 1 - p = loss probability
- b = payoff ratio
```

### Implementation Details

- Estimates win probability from historical frequency of positive returns
- Computes Kelly fractions for each asset
- Applies maximum position constraints (typically 0.25 per asset)
- Normalizes fractions to portfolio weights
- Maximizes expected logarithmic utility

### Key Considerations

⚠️ **Fractional Kelly:** Often use 0.25-0.5 * Kelly to reduce volatility
⚠️ **Estimation Risk:** Requires accurate estimates of probabilities and payoffs
⚠️ **Leverage Risk:** Full Kelly can produce concentrated, leveraged portfolios
⚠️ **Regime Changes:** Assumes stable win probabilities over time

### Usage Example

```python
from portfolio_optimization import KellyCriterionOptimizer

kc = KellyCriterionOptimizer(returns, asset_names)
result = kc.optimize(max_position=0.25)

print(result['weights'])            # Kelly-optimized weights
print(result['kelly_fractions'])    # Full Kelly fractions
print(result['win_probabilities'])  # Estimated win probabilities
```

---

## Comparison of Methods

| Criterion | Mean-Variance | Black-Litterman | Risk Parity | HRP | Kelly Criterion |
|-----------|---------------|-----------------|-------------|-----|-----------------|
| **Optimization** | Quadratic Programming | Quadratic Programming | Iterative | Clustering | Analytical/Constrained |
| **Key Focus** | Return/Risk Tradeoff | Views + Market Equilibrium | Risk Diversification | Correlation Structure | Growth Rate Maximization |
| **Estimation Needed** | Returns, Covariance | Returns, Views | Covariance | Correlations | Win Prob., Payoffs |
| **Concentration** | High | Moderate | Low | Low | Variable |
| **Stability** | Sensitive to inputs | Robust to views | Robust | Robust | Needs good prob. estimates |
| **Computational Cost** | Low-Moderate | Low-Moderate | Low | Very Low | Very Low |
| **Best For** | Efficient frontiers | Expert views | Diversification | Large universes | Growth-focused investors |

---

## Implementation Notes

### Portfolio Statistics

All methods return standardized statistics:

```python
result = {
    'weights': dict(zip(asset_names, weights)),  # Allocation dict
    'optimal_weights': weights,                   # NumPy array
    'return': portfolio_return,                   # Expected return
    'volatility': portfolio_volatility,           # Standard deviation
    'sharpe_ratio': sharpe_ratio,                # Risk-adjusted return
    # Method-specific fields...
}
```

### Input Requirements

All optimizers accept:
- **returns:** (n_assets, n_periods) NumPy array or pandas DataFrame
- **asset_names:** Optional list of asset names

### Dependencies

```
NumPy >= 1.20          # Numerical computing
Pandas >= 1.3          # Data structures
SciPy >= 1.7           # Optimization and clustering
```

### Validation

- All weight vectors are normalized to sum to 1.0
- Weights respect long-only and position constraints
- Covariance matrices are symmetric positive semi-definite
- Correlation matrices are bounded to [-1, 1]

---

## References

1. **Markowitz, H. M.** (1952). "Portfolio Selection." *Journal of Finance*, 7(1), 77-91.

2. **Black, F., & Litterman, R.** (1992). "Global Portfolio Optimization." *Financial Analysts Journal*, 48(5), 28-43.

3. **Bender, J., Sun, X., Thomas, R., & Zdorovtsov, V.** (2013). "The Properties of Equally Weighted Risk Contribution Portfolios." *Journal of Portfolio Management*, 40(11), 89-99.

4. **López de Prado, M.** (2016). *Building Diversified Portfolios that Outperform out-of-Sample*. Journal of Portfolio Management.

5. **Kelly, J. L.** (1956). "A New Interpretation of Information Rate." *Bell System Technical Journal*, 35(4), 917-926.

---

## Performance Characteristics

### Mean-Variance
- **Time Complexity:** O(n³) due to matrix inversion in optimization
- **Space Complexity:** O(n²) for covariance matrix storage
- **Best When:** Return estimates are reliable, explicit risk constraints desired

### Black-Litterman
- **Time Complexity:** O(n³) similar to mean-variance
- **Space Complexity:** O(n²)
- **Best When:** Market weights available, subjective views to incorporate

### Risk Parity
- **Time Complexity:** O(n²) per iteration, converges in ~10-20 iterations
- **Space Complexity:** O(n²)
- **Best When:** Diversification more important than return maximization

### Hierarchical Risk Parity
- **Time Complexity:** O(n²) for clustering, O(n log n) for bisection
- **Space Complexity:** O(n²) for distance matrix
- **Best When:** Large universes (100+ assets), robustness to correlation estimates

### Kelly Criterion
- **Time Complexity:** O(n) for probability estimation
- **Space Complexity:** O(n)
- **Best When:** Growth maximization is primary objective, good probability estimates available

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-19 | Initial implementation of 5 portfolio optimization methods |

---

**Author:** Financial Quants Team
**Last Updated:** 2025-11-19
**Status:** Production Ready
