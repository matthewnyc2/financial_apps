# Stock Filtering Quick Reference Guide

**Last Updated:** 2025-11-19

## 5-Stage Progressive Filtering Framework

```
3000 stocks → 1500 → 1000 → 200 → 50 → 10 stocks
  Stage 1    Stage 2  Stage 3  Stage 4  Stage 5
```

---

## Stage 1: Exclusion Filters (O(n) - Linear)

**Goal**: Remove obviously unsuitable stocks

**Filters**:
- Market cap > $500M
- Avg daily volume > $1M
- Price > $5
- Complete 252-day history
- Sector/industry exclusions

**Expected Reduction**: 50% (3000 → 1500)

**Python**:
```python
mask = (
    (df['market_cap'] >= 500e6) &
    (df['avg_daily_volume'] >= 1e6) &
    (df['price'] >= 5) &
    (df['history_days'] >= 252)
)
df_filtered = df[mask]
```

---

## Stage 2: Outlier Detection (O(n·p²))

**Goal**: Remove statistical outliers using robust methods

**Method**: Minimum Covariance Determinant (MCD) with robust Mahalanobis distance

**Key Insight**: "Neither winsorizing nor trimming mitigates multivariate outliers"

**Expected Reduction**: 33% (1500 → 1000)

**Python**:
```python
from sklearn.covariance import MinCovDet
from scipy.stats import chi2

mcd = MinCovDet(support_fraction=0.75, random_state=42)
mcd.fit(X)
mahal_dist = mcd.mahalanobis(X)
threshold = chi2.ppf(0.975, df=n_features)
df_clean = df[mahal_dist < threshold]
```

---

## Stage 3: Clustering & Factor Scoring (O(n·k·i·p))

**Goal**: Group similar stocks, select diverse top performers

**Method**: K-means clustering + composite factor scoring

**Factors** (Fama-French inspired):
1. **Value** (30%): Book-to-market, earnings yield, P/S
2. **Momentum** (30%): 12m return, 6m return
3. **Quality** (20%): ROE, ROA, debt-to-equity
4. **Low Volatility** (20%): Inverse volatility ranking

**Expected Reduction**: 80% (1000 → 200)

**Python**:
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Calculate factor scores (percentile ranks 0-1)
df['value_score'] = (
    df['book_to_market'].rank(pct=True) +
    df['earnings_yield'].rank(pct=True) +
    (1 - df['price_to_sales'].rank(pct=True))
) / 3

df['composite_score'] = (
    0.3 * df['value_score'] +
    0.3 * df['momentum_score'] +
    0.2 * df['quality_score'] +
    0.2 * (1 - df['volatility'].rank(pct=True))
)

# Cluster and select top from each
kmeans = KMeans(n_clusters=10, random_state=42)
df['cluster'] = kmeans.fit_predict(X_scaled)

selected = []
for cluster_id in range(10):
    cluster_stocks = df[df['cluster'] == cluster_id]
    top_stocks = cluster_stocks.nlargest(int(len(cluster_stocks) * 0.20), 'composite_score')
    selected.append(top_stocks)
```

---

## Stage 4: PCA & Advanced Ranking (O(min(n²p, np²)))

**Goal**: Dimension reduction and robust composite scoring

**Method**: PCA + cross-sectional percentile ranking

**Expected Reduction**: 75% (200 → 50)

**Python**:
```python
from sklearn.decomposition import PCA

# PCA for dimension reduction
pca = PCA(n_components=10)
components = pca.fit_transform(X_scaled)
print(f"Variance explained: {pca.explained_variance_ratio_.cumsum()[-1]:.2%}")

# Percentile ranking (0-100)
df['value_pctile'] = df['value_score'].rank(pct=True) * 100
df['momentum_pctile'] = df['momentum_score'].rank(pct=True) * 100
df['quality_pctile'] = df['quality_score'].rank(pct=True) * 100

# Final composite rank
df['final_rank'] = (
    0.35 * df['value_pctile'] +
    0.35 * df['momentum_pctile'] +
    0.30 * df['quality_pctile']
)

top_50 = df.nlargest(50, 'final_rank')
```

---

## Stage 5: Portfolio Optimization (O(n³))

**Goal**: Final selection with optimal weights

**Method**: Ledoit-Wolf covariance + Mean-Variance Optimization + Kelly Criterion

**Expected Reduction**: 80-90% (50 → 10-20)

**Python**:
```python
from sklearn.covariance import LedoitWolf
from scipy.optimize import minimize

# Robust covariance estimation
lw = LedoitWolf()
cov_matrix = lw.fit(returns).covariance_

# Expected returns
expected_returns = returns.mean() * 252

# Maximum Sharpe Ratio
def neg_sharpe(weights):
    port_return = np.sum(expected_returns * weights)
    port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
    return -(port_return - 0.02) / port_vol

constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1}]
bounds = tuple((0, 0.20) for _ in range(n_assets))  # Max 20% per position
initial = np.array([1/n_assets] * n_assets)

result = minimize(neg_sharpe, initial, method='SLSQP',
                 bounds=bounds, constraints=constraints)
optimal_weights = result.x

# Apply fractional Kelly criterion (0.25x recommended)
kelly_adjusted_weights = optimal_weights * 0.25
final_selection = df[kelly_adjusted_weights > 0.01]
```

---

## Critical Research Findings

### 1. Harvey-Liu-Zhu (2016): Factor Zoo
**Finding**: Of 316 published factors, only 2 survived rigorous testing (value & momentum)

**Implication**: Raise t-ratio threshold from 2.0 → 3.0

**Application**: Apply Bonferroni correction for multiple testing
```python
adjusted_alpha = 0.05 / n_factors
```

### 2. Ledoit-Wolf Shrinkage
**Finding**: Sample covariance poorly estimated when n_stocks ≫ n_observations

**Implication**: Use shrinkage estimator for robust covariance

**Performance**: "Significantly lower out-of-sample variance than multifactor models"

### 3. Fractional Kelly Criterion
**Finding**: Full Kelly has excessive volatility

**Recommendation**:
- Professional managers: 0.10x - 0.15x Kelly
- Individual traders: 0.25x - 0.50x Kelly

**Impact**: 0.5x Kelly reduces 80% drawdown probability from 1-in-5 to 1-in-213

### 4. Walk-Forward Analysis
**Finding**: "Gold standard" for strategy validation

**Method**: Rolling window optimization and out-of-sample testing

**Parameters**:
- Training period: 252 days (1 year)
- Testing period: 63 days (1 quarter)
- Step size: 21 days (1 month)

---

## Risk-Adjusted Performance Metrics

### Sharpe Ratio
```python
sharpe = np.sqrt(252) * (returns.mean() - rf_rate) / returns.std()
```
**Benchmarks**: >1.0 good, >2.0 excellent, >3.0 exceptional

### Sortino Ratio (preferred over Sharpe)
```python
downside_std = np.sqrt((returns[returns < 0]**2).mean())
sortino = np.sqrt(252) * returns.mean() / downside_std
```
**Benchmarks**: >2.0 good

### Calmar Ratio
```python
max_dd = abs((cumulative / cumulative.expanding().max() - 1).min())
calmar = annual_return / max_dd
```
**Benchmarks**: >0.5 good, >3.0 excellent

---

## Computational Complexity Cheat Sheet

| Stage | Method | Complexity | Time (1000 stocks) |
|-------|--------|------------|-------------------|
| 1 | Exclusion | O(n) | <1ms |
| 2 | MCD Outliers | O(p²·n·log n) | ~100ms |
| 3 | K-means | O(n·k·i·p) | ~500ms |
| 4 | PCA | O(min(n²p, np²)) | ~200ms |
| 5 | Mean-Var Opt | O(n³) | ~50ms |
| **Total** | | | **~1 second** |

**Scalability**: All methods scale to 1000+ stocks efficiently with vectorization

---

## Factor Definitions (Fama-French)

### Three-Factor Model (1993)
```
R_i - R_f = α + β(R_m - R_f) + s·SMB + h·HML + ε

MKT: Market excess return
SMB: Small Minus Big (size)
HML: High Minus Low (value)
```

### Five-Factor Model (2015)
Adds:
```
RMW: Robust Minus Weak (profitability)
CMA: Conservative Minus Aggressive (investment)
```

**Performance**: Explains 90%+ of portfolio variance vs. 70% for CAPM

---

## Machine Learning Methods

### Best Performers for Stock Selection

1. **LambdaMART** (gradient boosted trees for ranking)
   - Best across profitability, accuracy, risk metrics
   - Complexity: O(n·log n·d·t)

2. **Random Forest**
   - Outperforms GBT and DNN in some applications
   - Robust to overfitting
   - Built-in feature importance

3. **Ensemble Methods**
   - Combining RF + XGBoost + LightGBM
   - 0.45% daily return vs. 0.43% for RF alone

**Warning**: Machine learning prone to overfitting - always use walk-forward validation

---

## Data Preprocessing Best Practices

### 1. Cross-Sectional Z-Score
```python
# Normalize across stocks at each time point
df['factor_zscore'] = df.groupby('date')['factor'].transform(
    lambda x: (x - x.mean()) / x.std()
)
```

### 2. Percentile Ranking (robust to outliers)
```python
df['factor_pctile'] = df['factor'].rank(pct=True) * 100
```

### 3. Winsorization (use cautiously)
```python
from scipy.stats.mstats import winsorize
df['factor_winsorized'] = winsorize(df['factor'], limits=(0.05, 0.05))
```

**Warning**: "Winsorizing exacerbates multivariate outlier problem" - use MCD instead

---

## Overfitting Detection

### Warning Signs
1. Sharpe degradation > 50% (in-sample to out-of-sample)
2. In-sample/out-of-sample return correlation < 0.3
3. In-sample Sharpe > 3.0 with out-of-sample Sharpe < 1.0

### Prevention
1. Use walk-forward analysis
2. Limit number of optimized parameters
3. Apply Bonferroni/FDR correction
4. Test on multiple time periods
5. Use simple models when possible

---

## Python Libraries Required

```bash
# Core
pip install numpy pandas scipy

# Machine Learning
pip install scikit-learn xgboost lightgbm

# Optimization
pip install cvxpy

# Parallel Processing
pip install joblib dask

# Visualization
pip install matplotlib seaborn

# Financial Data
pip install yfinance pandas-datareader
```

---

## Complete Minimal Example

```python
import pandas as pd
import numpy as np
from sklearn.covariance import MinCovDet, LedoitWolf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.optimize import minimize
from scipy.stats import chi2

# Stage 1: Exclusion
df = df[(df['market_cap'] >= 500e6) & (df['price'] >= 5)]

# Stage 2: Outlier removal
features = ['return_12m', 'volatility', 'book_to_market', 'roe']
X = df[features].values
mcd = MinCovDet().fit(X)
df = df[mcd.mahalanobis(X) < chi2.ppf(0.975, len(features))]

# Stage 3: Factor scoring + clustering
df['value'] = df['book_to_market'].rank(pct=True)
df['momentum'] = df['return_12m'].rank(pct=True)
df['score'] = 0.5 * df['value'] + 0.5 * df['momentum']

X_scaled = StandardScaler().fit_transform(X)
df['cluster'] = KMeans(n_clusters=10).fit_predict(X_scaled)

selected = []
for c in range(10):
    cluster_df = df[df['cluster'] == c]
    selected.append(cluster_df.nlargest(int(len(cluster_df)*0.2), 'score'))
df = pd.concat(selected)

# Stage 4: PCA + ranking
pca = PCA(n_components=5).fit_transform(X_scaled)
df['final_rank'] = df['score'].rank(pct=True) * 100
df = df.nlargest(50, 'final_rank')

# Stage 5: Portfolio optimization
returns = returns_df[df['ticker']]
cov = LedoitWolf().fit(returns).covariance_
expected_ret = returns.mean() * 252

def neg_sharpe(w):
    return -(w @ expected_ret - 0.02) / np.sqrt(w @ cov @ w)

result = minimize(
    neg_sharpe,
    np.ones(len(df))/len(df),
    method='SLSQP',
    bounds=[(0, 0.2)] * len(df),
    constraints=[{'type': 'eq', 'fun': lambda w: w.sum() - 1}]
)

final_stocks = df[result.x > 0.01]
print(f"Final selection: {len(final_stocks)} stocks")
```

---

## Key Papers to Read

1. **Harvey, Liu & Zhu (2016)** - "...and the Cross-Section of Expected Returns"
   - Multiple testing framework for factors

2. **Ledoit & Wolf (2003)** - "Improved Estimation of the Covariance Matrix"
   - Shrinkage covariance estimation

3. **Fama & French (2015)** - "A Five-Factor Asset Pricing Model"
   - Modern factor framework

4. **Kelly (1956)** - "A New Interpretation of Information Rate"
   - Optimal position sizing

5. **Markowitz (1952)** - "Portfolio Selection"
   - Mean-variance optimization foundation

---

## Common Pitfalls to Avoid

1. **Using sample covariance with limited data**
   - Solution: Ledoit-Wolf shrinkage

2. **Not correcting for multiple testing**
   - Solution: Bonferroni or FDR correction

3. **Optimizing on entire dataset**
   - Solution: Walk-forward analysis

4. **Full Kelly sizing**
   - Solution: Use 0.25x fractional Kelly

5. **Univariate outlier detection only**
   - Solution: Use robust Mahalanobis distance (MCD)

6. **Ignoring transaction costs**
   - Solution: Include slippage and commissions in backtest

7. **Too many optimized parameters**
   - Solution: Keep it simple, use regularization

8. **Look-ahead bias**
   - Solution: Strict time-series data splitting

---

## Performance Benchmarks

### Good Strategy Metrics
- Sharpe Ratio: > 1.5
- Sortino Ratio: > 2.0
- Calmar Ratio: > 1.0
- Win Rate: > 55%
- Max Drawdown: < 25%
- Annual Return: > 15%
- Volatility: < 20%

### Overfitting Indicators
- IS/OOS Sharpe degradation: > 50%
- IS/OOS correlation: < 0.3
- Excessive parameters: > n_features / 10
- Perfect or near-perfect training performance

---

**End of Quick Reference Guide**

For detailed explanations, mathematical foundations, and additional implementation examples, see the complete research document: `STOCK_FILTERING_RESEARCH.md`
