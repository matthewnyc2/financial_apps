# Statistical Methods for Stock Filtering and Ranking: Comprehensive Research

**Research Date:** 2025-11-19
**Scope:** PhD-level statistical techniques for filtering 1000+ stocks to top 10 candidates

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Progressive Filtering Framework](#progressive-filtering-framework)
3. [Multi-Stage Filtering Approaches](#multi-stage-filtering-approaches)
4. [Scoring and Ranking Algorithms](#scoring-and-ranking-algorithms)
5. [Statistical Significance Testing](#statistical-significance-testing)
6. [Outlier Detection Methods](#outlier-detection-methods)
7. [Clustering Algorithms](#clustering-algorithms)
8. [Principal Component Analysis](#principal-component-analysis)
9. [Factor Analysis and Models](#factor-analysis-and-models)
10. [Risk-Adjusted Performance Metrics](#risk-adjusted-performance-metrics)
11. [Position Sizing Methods](#position-sizing-methods)
12. [Portfolio Optimization](#portfolio-optimization)
13. [Data Preprocessing and Normalization](#data-preprocessing-and-normalization)
14. [Backtesting and Validation](#backtesting-and-validation)
15. [Machine Learning Integration](#machine-learning-integration)
16. [Computational Considerations](#computational-considerations)
17. [Implementation Guide](#implementation-guide)

---

## Executive Summary

This research document provides comprehensive coverage of statistical methods for filtering and ranking large stock universes (1000+ stocks) down to top candidates. The methodology emphasizes:

- **Computational efficiency**: Methods scalable to large datasets
- **Statistical rigor**: PhD-level techniques with solid mathematical foundations
- **Practical implementation**: Python-based approaches with clear algorithms
- **Progressive filtering**: Multi-stage funnel from thousands to final selection

**Key Finding from Harvey, Liu & Zhu (2016)**: Among 316 published factors, only 2 (value and momentum) survived rigorous multiple testing correction with t-ratio threshold of 3.0 (vs. traditional 2.0).

---

## Progressive Filtering Framework

### Overview: 5-Stage Funnel Approach

```
Universe: ~3000 stocks
    ↓ Stage 1: Exclusion & Basic Filters
~1500 stocks (50% reduction)
    ↓ Stage 2: Outlier Detection & Data Quality
~1000 stocks (33% reduction)
    ↓ Stage 3: Factor Scoring & Clustering
~200 stocks (80% reduction)
    ↓ Stage 4: Composite Ranking & PCA
~50 stocks (75% reduction)
    ↓ Stage 5: Portfolio Optimization
10-20 stocks (80-90% reduction)
```

### Stage 1: Exclusion and Basic Filters (3000 → 1500 stocks)
**Purpose**: Eliminate clearly unsuitable candidates
**Computational Complexity**: O(n) - Linear

**Filters:**
1. **Market Cap**: Minimum $500M (reduces liquidity risk)
2. **Average Daily Volume**: > $1M (ensures tradability)
3. **Price Filter**: > $5 (avoids penny stocks)
4. **Data Quality**: Complete 252-day history minimum
5. **Sector/Industry Exclusions**: Based on investment mandate

**Python Implementation:**
```python
import pandas as pd
import numpy as np

def stage1_exclusion_filter(df, min_market_cap=500e6, min_avg_volume=1e6,
                            min_price=5, min_history_days=252):
    """
    Stage 1: Basic exclusion filters
    O(n) complexity - vectorized operations
    """
    mask = (
        (df['market_cap'] >= min_market_cap) &
        (df['avg_daily_volume'] >= min_avg_volume) &
        (df['price'] >= min_price) &
        (df['history_days'] >= min_history_days) &
        (df['data_complete'] == True)
    )
    return df[mask]
```

### Stage 2: Outlier Detection & Data Quality (1500 → 1000 stocks)
**Purpose**: Remove statistical outliers and questionable data
**Computational Complexity**: O(n·p²) for Mahalanobis distance where p = features

**Methods:**
1. **Robust Mahalanobis Distance** with MCD estimator
2. **Winsorization** at 5th/95th percentiles
3. **Z-score filtering** for extreme values

**Python Implementation:**
```python
from sklearn.covariance import MinCovDet
from scipy.stats import chi2

def stage2_outlier_detection(df, features, contamination=0.33):
    """
    Stage 2: Robust multivariate outlier detection
    Uses Minimum Covariance Determinant (MCD) for robustness
    """
    # Extract feature matrix
    X = df[features].values

    # Fit robust covariance estimator
    mcd = MinCovDet(support_fraction=1-contamination, random_state=42)
    mcd.fit(X)

    # Calculate robust Mahalanobis distances
    mahal_dist = mcd.mahalanobis(X)

    # Chi-square threshold for outlier detection
    threshold = chi2.ppf(0.975, df=len(features))

    # Keep non-outliers
    mask = mahal_dist < threshold
    return df[mask]

def winsorize_features(df, features, limits=(0.05, 0.05)):
    """
    Winsorize features at specified percentiles
    Caps extreme values rather than removing them
    """
    from scipy.stats.mstats import winsorize

    df_clean = df.copy()
    for feature in features:
        df_clean[feature] = winsorize(df[feature], limits=limits)

    return df_clean
```

### Stage 3: Factor Scoring & Clustering (1000 → 200 stocks)
**Purpose**: Group similar stocks and score by factors
**Computational Complexity**:
- K-means: O(n·k·i·p) where k=clusters, i=iterations, p=features
- Factor scoring: O(n·p)

**Approach:**
1. **Calculate factor scores** (value, momentum, quality, size)
2. **Cluster analysis** to identify regime groups
3. **Select top percentiles** from each cluster

**Python Implementation:**
```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def calculate_factor_scores(df):
    """
    Calculate Fama-French style factor scores
    """
    # Value factors
    df['value_score'] = (
        df['book_to_market'].rank(pct=True) +
        df['earnings_yield'].rank(pct=True) +
        (1 - df['price_to_sales'].rank(pct=True))
    ) / 3

    # Momentum factors
    df['momentum_score'] = (
        df['return_12m'].rank(pct=True) +
        df['return_6m'].rank(pct=True)
    ) / 2

    # Quality factors
    df['quality_score'] = (
        df['roe'].rank(pct=True) +
        df['roa'].rank(pct=True) +
        (1 - df['debt_to_equity'].rank(pct=True))
    ) / 3

    # Size factor (inverse - prefer smaller in this factor)
    df['size_score'] = 1 - df['market_cap'].rank(pct=True)

    return df

def stage3_clustering_selection(df, n_clusters=10, top_pct_per_cluster=0.20):
    """
    Stage 3: Cluster stocks and select top performers from each cluster
    Ensures diversification across different stock regimes
    """
    # Calculate factor scores
    df = calculate_factor_scores(df)

    # Feature matrix for clustering
    cluster_features = ['value_score', 'momentum_score', 'quality_score',
                       'volatility', 'beta', 'market_cap']
    X = df[cluster_features].values

    # Standardize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Calculate composite score
    df['composite_score'] = (
        0.3 * df['value_score'] +
        0.3 * df['momentum_score'] +
        0.2 * df['quality_score'] +
        0.2 * (1 - df['volatility'].rank(pct=True))
    )

    # Select top N% from each cluster
    selected = []
    for cluster_id in range(n_clusters):
        cluster_stocks = df[df['cluster'] == cluster_id]
        n_select = max(1, int(len(cluster_stocks) * top_pct_per_cluster))
        top_stocks = cluster_stocks.nlargest(n_select, 'composite_score')
        selected.append(top_stocks)

    return pd.concat(selected)
```

### Stage 4: PCA & Advanced Ranking (200 → 50 stocks)
**Purpose**: Reduce dimensionality and create robust composite rankings
**Computational Complexity**: O(min(n·p², p³)) for PCA

**Methods:**
1. **PCA for dimension reduction** (50+ features → 10-15 components)
2. **Percentile ranking** across multiple factors
3. **Composite score weighting**
4. **Cross-sectional z-score normalization**

**Python Implementation:**
```python
from sklearn.decomposition import PCA

def stage4_pca_ranking(df, n_components=10, top_n=50):
    """
    Stage 4: PCA dimension reduction and advanced ranking
    """
    # Select features for PCA
    features = [col for col in df.columns if col not in
                ['ticker', 'cluster', 'composite_score']]

    X = df[features].values

    # Standardize before PCA
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Apply PCA
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(X_scaled)

    # Explained variance
    explained_var = pca.explained_variance_ratio_.cumsum()
    print(f"Variance explained by {n_components} components: {explained_var[-1]:.2%}")

    # Create percentile ranks for each factor
    df['value_pctile'] = df['value_score'].rank(pct=True) * 100
    df['momentum_pctile'] = df['momentum_score'].rank(pct=True) * 100
    df['quality_pctile'] = df['quality_score'].rank(pct=True) * 100

    # Composite rank with weights
    df['final_rank'] = (
        0.35 * df['value_pctile'] +
        0.35 * df['momentum_pctile'] +
        0.30 * df['quality_pctile']
    )

    # Cross-sectional z-score normalization
    df['final_rank_zscore'] = (df['final_rank'] - df['final_rank'].mean()) / df['final_rank'].std()

    # Select top N stocks
    return df.nlargest(top_n, 'final_rank')
```

### Stage 5: Portfolio Optimization (50 → 10-20 stocks)
**Purpose**: Final selection with portfolio constraints
**Computational Complexity**: O(p³) for mean-variance optimization

**Methods:**
1. **Ledoit-Wolf shrinkage** for covariance estimation
2. **Mean-variance optimization** (Markowitz)
3. **Risk parity** or **minimum variance** alternatives
4. **Kelly criterion** for position sizing

**Python Implementation:**
```python
from sklearn.covariance import LedoitWolf

def stage5_portfolio_optimization(df, returns_df, target_n=10, method='max_sharpe'):
    """
    Stage 5: Portfolio optimization with robust covariance estimation
    """
    # Get returns for selected stocks
    tickers = df['ticker'].values
    returns = returns_df[tickers]

    # Ledoit-Wolf shrinkage estimator for covariance
    lw = LedoitWolf()
    cov_matrix = lw.fit(returns).covariance_

    # Expected returns (simple mean)
    expected_returns = returns.mean() * 252  # Annualized

    if method == 'max_sharpe':
        # Maximum Sharpe ratio portfolio
        weights = maximize_sharpe_ratio(expected_returns, cov_matrix)
    elif method == 'min_variance':
        # Minimum variance portfolio
        weights = minimize_variance(cov_matrix)
    elif method == 'risk_parity':
        # Risk parity allocation
        weights = risk_parity_weights(cov_matrix)

    # Select stocks with non-zero weights
    selected_stocks = df[weights > 0.01]  # Threshold at 1%

    # Sort by weight
    selected_stocks['weight'] = weights[weights > 0.01]
    selected_stocks = selected_stocks.sort_values('weight', ascending=False)

    # Apply Kelly criterion for position sizing
    selected_stocks = apply_kelly_criterion(selected_stocks, returns)

    return selected_stocks.head(target_n)

def maximize_sharpe_ratio(returns, cov_matrix, risk_free_rate=0.02):
    """
    Quadratic programming for maximum Sharpe ratio
    """
    from scipy.optimize import minimize

    n = len(returns)

    def neg_sharpe(weights):
        port_return = np.sum(returns * weights)
        port_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(port_return - risk_free_rate) / port_vol

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 0.20) for _ in range(n))  # Max 20% per position
    initial_guess = np.array([1/n] * n)

    result = minimize(neg_sharpe, initial_guess, method='SLSQP',
                     bounds=bounds, constraints=constraints)

    return result.x

def apply_kelly_criterion(df, returns, fraction=0.25):
    """
    Apply fractional Kelly criterion for position sizing
    Recommended: 0.25x Kelly for practitioners
    """
    kelly_fractions = []

    for ticker in df['ticker']:
        stock_returns = returns[ticker]

        # Estimate win probability and odds
        win_prob = (stock_returns > 0).mean()

        if win_prob > 0:
            avg_win = stock_returns[stock_returns > 0].mean()
            avg_loss = abs(stock_returns[stock_returns < 0].mean())

            # Kelly formula: f* = (bp - q) / b
            # b = odds, p = win prob, q = loss prob
            if avg_loss > 0:
                b = avg_win / avg_loss
                kelly = (b * win_prob - (1 - win_prob)) / b
                kelly_fractions.append(max(0, kelly * fraction))
            else:
                kelly_fractions.append(0)
        else:
            kelly_fractions.append(0)

    df['kelly_fraction'] = kelly_fractions
    df['adjusted_weight'] = df['weight'] * df['kelly_fraction']

    # Renormalize
    df['adjusted_weight'] = df['adjusted_weight'] / df['adjusted_weight'].sum()

    return df
```

---

## Multi-Stage Filtering Approaches

### Academic Foundation

**Key Research:**
- **Multiple Criteria Decision Making (MCDM)**: Enables stock selection using aggregated information about firm financial performance and parameters characterizing maximal possible returns
- **Two-Stage Filter**: Uses supervised and unsupervised machine learning algorithms (4 clustering + 4 classification algorithms)
- **Scoring and Screening Models**: Integrates data from trading history, factors, financials, and media

### Mathematical Framework

**TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution):**

```
Score_i = S_i / (S_i + S_i*)

where:
S_i = distance to ideal solution
S_i* = distance to negative-ideal solution
```

**Computational Complexity**: O(n·m) where n = stocks, m = criteria

### Implementation Strategy

```python
def multi_criteria_decision_making(df, criteria, weights):
    """
    TOPSIS implementation for stock selection

    Parameters:
    -----------
    df : DataFrame with stocks and criteria
    criteria : list of column names
    weights : dict of criterion: weight
    """
    # Normalize decision matrix
    normalized = df[criteria].copy()
    for col in criteria:
        norm = np.sqrt((df[col]**2).sum())
        normalized[col] = df[col] / norm

    # Apply weights
    weighted = normalized.copy()
    for col, weight in weights.items():
        weighted[col] = normalized[col] * weight

    # Determine ideal and negative-ideal solutions
    ideal = weighted.max()
    negative_ideal = weighted.min()

    # Calculate distances
    dist_ideal = np.sqrt(((weighted - ideal)**2).sum(axis=1))
    dist_neg_ideal = np.sqrt(((weighted - negative_ideal)**2).sum(axis=1))

    # Calculate TOPSIS score
    df['topsis_score'] = dist_neg_ideal / (dist_ideal + dist_neg_ideal)

    return df
```

---

## Scoring and Ranking Algorithms

### Learning-to-Rank Methods

**1. RankNet (Microsoft Research, 2005)**
- Transforms ranking into pairwise binary classification
- **Complexity**: O(n²) for n items (pairwise comparisons)
- **Loss Function**: Cross-entropy on pairs

```python
def ranknet_loss(y_pred_i, y_pred_j, y_true_i, y_true_j):
    """
    RankNet pairwise loss
    """
    S_ij = np.sign(y_true_i - y_true_j)
    P_ij = 1 / (1 + np.exp(-(y_pred_i - y_pred_j)))
    return -S_ij * np.log(P_ij) - (1 - S_ij) * np.log(1 - P_ij)
```

**2. LambdaMART**
- Gradient boosted decision trees for ranking
- **Best performer** across profitability, ranking accuracy, risk metrics
- **Complexity**: O(n·log(n)·d·t) where d = tree depth, t = trees

**3. Composite Score Approach**

**Portfolio123 Methodology:**
- Convert each factor to percentile score (0-100)
- Combine with user-supplied weights
- Normalize to percentile ranks

```python
def composite_percentile_ranking(df, factors, weights):
    """
    Portfolio123-style composite ranking

    Returns percentile rank from 0-100
    """
    # Convert each factor to percentile
    percentiles = pd.DataFrame()
    for factor in factors:
        percentiles[f'{factor}_pct'] = df[factor].rank(pct=True) * 100

    # Weighted combination
    df['composite_score'] = sum(
        percentiles[f'{factor}_pct'] * weights.get(factor, 1.0)
        for factor in factors
    ) / sum(weights.values())

    # Final percentile rank
    df['final_rank'] = df['composite_score'].rank(pct=True) * 100

    return df
```

### Ensemble Methods

**Kavout K-Score Approach:**
- 200+ factors
- Ensemble machine learning
- Output: 1-9 score

**Implementation Pattern:**
```python
from sklearn.ensemble import VotingRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

def ensemble_stock_scoring(X_train, y_train, X_test):
    """
    Ensemble approach combining multiple models
    """
    # Base models
    models = [
        ('xgb', XGBRegressor(n_estimators=100, learning_rate=0.1)),
        ('lgbm', LGBMRegressor(n_estimators=100, learning_rate=0.1)),
        ('ridge', Ridge(alpha=1.0))
    ]

    # Stacking with meta-learner
    ensemble = StackingRegressor(
        estimators=models,
        final_estimator=Ridge(),
        cv=5
    )

    ensemble.fit(X_train, y_train)
    scores = ensemble.predict(X_test)

    return scores
```

---

## Statistical Significance Testing

### The Multiple Testing Problem

**Harvey, Liu & Zhu (2016) - "...and the Cross-Section of Expected Returns"**

**Key Findings:**
- 316 published factors examined
- 59 new factors discovered between 2010-2012 alone
- **Recommended t-ratio threshold: 3.0** (vs. traditional 2.0)
- **Result**: Only 2 factors survive (value and momentum)

### Bonferroni Correction

**Formula:**
```
α_adjusted = α / n

where:
α = desired significance level (e.g., 0.05)
n = number of tests
```

**Example:**
- Testing 20 factors with α = 0.05
- Bonferroni-corrected α = 0.05/20 = 0.0025
- Without correction: 64% chance of at least one false positive

**Implementation:**
```python
from scipy import stats

def bonferroni_correction(p_values, alpha=0.05):
    """
    Apply Bonferroni correction for multiple testing

    Returns:
    --------
    significant : boolean array indicating significant tests
    adjusted_alpha : corrected significance threshold
    """
    n_tests = len(p_values)
    adjusted_alpha = alpha / n_tests

    significant = p_values < adjusted_alpha

    return significant, adjusted_alpha

def test_factor_significance(returns, factor_scores, alpha=0.05):
    """
    Test if factor scores predict returns with Bonferroni correction
    """
    # Cross-sectional regression for each time period
    p_values = []

    for t in returns.index:
        # Regression: return_t = α + β * factor_t + ε
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            factor_scores.loc[t], returns.loc[t]
        )
        p_values.append(p_value)

    # Apply Bonferroni correction
    significant, adj_alpha = bonferroni_correction(p_values, alpha)

    # Average t-statistic
    avg_t_stat = np.mean([
        slope / std_err for slope, _, _, _, std_err in
        [stats.linregress(factor_scores.loc[t], returns.loc[t])
         for t in returns.index]
    ])

    # Harvey-Liu-Zhu threshold
    meets_hlz_threshold = avg_t_stat > 3.0

    return {
        'avg_t_stat': avg_t_stat,
        'bonferroni_significant': significant.mean(),
        'meets_hlz_threshold': meets_hlz_threshold,
        'adjusted_alpha': adj_alpha
    }
```

### False Discovery Rate (FDR) Control

**Benjamini-Hochberg Procedure** (less conservative than Bonferroni):

```python
def benjamini_hochberg(p_values, fdr=0.05):
    """
    Benjamini-Hochberg FDR control

    More powerful than Bonferroni for large-scale testing
    """
    n = len(p_values)
    sorted_indices = np.argsort(p_values)
    sorted_pvals = p_values[sorted_indices]

    # Find largest k where p(k) <= (k/n) * FDR
    thresholds = (np.arange(1, n+1) / n) * fdr
    significant = sorted_pvals <= thresholds

    if significant.any():
        k = np.max(np.where(significant)[0])
        threshold = sorted_pvals[k]
    else:
        threshold = 0

    return p_values <= threshold
```

---

## Outlier Detection Methods

### Robust Mahalanobis Distance

**Mathematical Foundation:**

Standard Mahalanobis distance:
```
D²_M(x) = (x - μ)ᵀ Σ⁻¹ (x - μ)

where:
μ = sample mean (sensitive to outliers!)
Σ = sample covariance (sensitive to outliers!)
```

**Problem**: Classical estimators are contaminated by the outliers we're trying to detect.

**Solution**: Robust estimators

### Minimum Covariance Determinant (MCD)

**Ledoit & Wolf**: "The MCD calculates the mean and covariance based on the most central subset of the data"

**Algorithm:**
1. Find h-subset (h ≈ 0.75n) minimizing |Σ_h|
2. Use this subset to estimate μ_robust and Σ_robust
3. Calculate robust Mahalanobis distance

**Complexity**: O(p²·n·log(n)) with FastMCD algorithm

**Implementation:**
```python
from sklearn.covariance import MinCovDet
from scipy.stats import chi2
import matplotlib.pyplot as plt

def robust_outlier_detection(df, features, contamination=0.25, plot=True):
    """
    Robust multivariate outlier detection using MCD

    Parameters:
    -----------
    contamination : float, expected proportion of outliers (default 0.25)
    """
    X = df[features].values
    n_samples, n_features = X.shape

    # Fit MCD
    mcd = MinCovDet(
        support_fraction=1-contamination,
        random_state=42
    )
    mcd.fit(X)

    # Robust Mahalanobis distances
    robust_mahal = mcd.mahalanobis(X)

    # Chi-square threshold (97.5th percentile)
    threshold = chi2.ppf(0.975, df=n_features)

    # Classify outliers
    is_outlier = robust_mahal > threshold

    if plot:
        plt.figure(figsize=(10, 6))
        plt.hist(robust_mahal, bins=50, alpha=0.7, label='Robust Mahalanobis Distance')
        plt.axvline(threshold, color='r', linestyle='--',
                   label=f'Threshold (χ² 97.5%): {threshold:.2f}')
        plt.xlabel('Robust Mahalanobis Distance')
        plt.ylabel('Frequency')
        plt.legend()
        plt.title('Outlier Detection via Robust Mahalanobis Distance')
        plt.show()

    return {
        'is_outlier': is_outlier,
        'robust_distance': robust_mahal,
        'threshold': threshold,
        'n_outliers': is_outlier.sum(),
        'pct_outliers': is_outlier.mean() * 100
    }
```

### Winsorization vs Trimming

**Winsorization**: Replace extremes with percentile values
**Trimming**: Remove extremes entirely

**Important Finding**: "Neither winsorizing nor trimming mitigates multivariate outliers - they actually exacerbate the problem"

**Best Practice**: Use robust Mahalanobis distance for multivariate outlier detection

```python
from scipy.stats.mstats import winsorize

def winsorize_returns(returns, limits=(0.05, 0.05)):
    """
    Winsorize at 5th and 95th percentiles

    Note: Use cautiously - may not help with multivariate outliers
    """
    return pd.DataFrame({
        col: winsorize(returns[col], limits=limits)
        for col in returns.columns
    }, index=returns.index)

def compare_outlier_methods(df, features):
    """
    Compare different outlier detection approaches
    """
    X = df[features].values

    # Method 1: Z-score (univariate)
    z_scores = np.abs(stats.zscore(X))
    z_outliers = (z_scores > 3).any(axis=1)

    # Method 2: Classical Mahalanobis
    mean = X.mean(axis=0)
    cov = np.cov(X.T)
    inv_cov = np.linalg.pinv(cov)
    diff = X - mean
    classical_mahal = np.sqrt(np.sum(diff @ inv_cov * diff, axis=1))
    classical_outliers = classical_mahal > chi2.ppf(0.975, df=X.shape[1])

    # Method 3: Robust Mahalanobis (MCD)
    mcd = MinCovDet().fit(X)
    robust_mahal = mcd.mahalanobis(X)
    robust_outliers = robust_mahal > chi2.ppf(0.975, df=X.shape[1])

    comparison = pd.DataFrame({
        'Z-Score Method': z_outliers,
        'Classical Mahalanobis': classical_outliers,
        'Robust Mahalanobis': robust_outliers
    })

    print("Outlier Detection Comparison:")
    print(comparison.sum())
    print("\nOverlap Analysis:")
    print(f"All methods agree: {(comparison.all(axis=1)).sum()}")
    print(f"No methods agree: {(~comparison.any(axis=1)).sum()}")

    return comparison
```

---

## Clustering Algorithms

### K-Means Clustering

**Mathematical Foundation:**
```
Objective: minimize Σ_i Σ_{x∈C_i} ||x - μ_i||²

where:
C_i = cluster i
μ_i = centroid of cluster i
```

**Complexity**: O(n·k·i·d)
- n = samples, k = clusters, i = iterations, d = dimensions

**Advantages**:
- Fast and scalable to large datasets
- Works well for spherical clusters
- Straightforward implementation

**Limitations**:
- Requires pre-specifying k
- Sensitive to initialization
- Assumes spherical clusters

**Implementation:**
```python
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def optimal_kmeans_clustering(df, features, k_range=range(5, 20)):
    """
    Find optimal number of clusters using elbow method and silhouette score
    """
    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    inertias = []
    silhouette_scores = []

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        inertias.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, labels))

    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.plot(k_range, inertias, 'bo-')
    ax1.set_xlabel('Number of Clusters (k)')
    ax1.set_ylabel('Inertia')
    ax1.set_title('Elbow Method')

    ax2.plot(k_range, silhouette_scores, 'ro-')
    ax2.set_xlabel('Number of Clusters (k)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis')

    plt.tight_layout()
    plt.show()

    # Optimal k (highest silhouette score)
    optimal_k = k_range[np.argmax(silhouette_scores)]

    return optimal_k, silhouette_scores
```

### Hierarchical Clustering

**Methods**:
- **Single linkage**: min distance between clusters
- **Complete linkage**: max distance between clusters
- **Average linkage**: average distance between clusters
- **Ward linkage**: minimizes within-cluster variance

**Complexity**: O(n³) for naive algorithm, O(n²log(n)) with optimizations

**Advantage**: Creates dendrogram showing hierarchical structure

**Implementation:**
```python
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

def hierarchical_stock_clustering(df, features, method='ward'):
    """
    Hierarchical clustering with dendrogram visualization
    """
    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Compute linkage matrix
    Z = linkage(X_scaled, method=method)

    # Plot dendrogram
    plt.figure(figsize=(15, 8))
    dendrogram(Z, labels=df['ticker'].values, leaf_rotation=90)
    plt.title(f'Hierarchical Clustering Dendrogram ({method} linkage)')
    plt.xlabel('Stock Ticker')
    plt.ylabel('Distance')
    plt.tight_layout()
    plt.show()

    return Z
```

### DBSCAN (Density-Based Spatial Clustering)

**Parameters**:
- **ε (eps)**: Neighborhood radius
- **MinPts**: Minimum points to form dense region

**Advantages**:
- Discovers clusters of arbitrary shape
- Identifies noise/outliers automatically
- No need to specify number of clusters

**Complexity**: O(n·log(n)) with spatial indexing

**Implementation:**
```python
from sklearn.cluster import DBSCAN

def dbscan_stock_clustering(df, features, eps=0.5, min_samples=5):
    """
    DBSCAN clustering - good for identifying outliers
    """
    X = df[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    labels = dbscan.fit_predict(X_scaled)

    # -1 label indicates noise/outliers
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    df['cluster'] = labels
    df['is_noise'] = labels == -1

    print(f"Number of clusters: {n_clusters}")
    print(f"Number of noise points: {n_noise} ({n_noise/len(df)*100:.1f}%)")

    return df
```

### Application to Stock Selection

**Strategy**: Cluster stocks by characteristics, select top from each cluster

```python
def cluster_based_selection(df, features, n_clusters=10, top_per_cluster=2):
    """
    Select diverse stocks using clustering
    Ensures representation across different market regimes
    """
    # Cluster stocks
    X = df[features].values
    X_scaled = StandardScaler().fit_transform(X)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)

    # Select top stocks from each cluster based on composite score
    selected_stocks = []

    for cluster_id in range(n_clusters):
        cluster_stocks = df[df['cluster'] == cluster_id]
        top_stocks = cluster_stocks.nlargest(top_per_cluster, 'composite_score')
        selected_stocks.append(top_stocks)

    return pd.concat(selected_stocks)
```

---

## Principal Component Analysis

### Mathematical Foundation

**PCA Goal**: Find orthogonal directions of maximum variance

**Eigenvalue decomposition**:
```
Σ = V Λ Vᵀ

where:
Σ = covariance matrix
V = eigenvectors (principal components)
Λ = diagonal matrix of eigenvalues (variance explained)
```

**Dimensionality Reduction**:
```
Z = X W_k

where:
X = original data (n × p)
W_k = first k principal components (p × k)
Z = transformed data (n × k)
```

**Complexity**: O(min(n²p, np²))

### Applications in Finance

**1. Yield Curve Analysis**
- PC1: Level (~90% variance)
- PC2: Slope (~8% variance)
- PC3: Curvature (~1% variance)

**2. Risk Factor Identification**
- Reduce 200+ factors to 10-15 components
- Retain 85%+ of information

**3. Portfolio Risk Decomposition**

**Implementation:**
```python
from sklearn.decomposition import PCA

def pca_stock_analysis(df, features, n_components=10, plot=True):
    """
    PCA for dimensionality reduction and factor identification
    """
    X = df[features].values

    # Standardize (critical for PCA)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit PCA
    pca = PCA(n_components=n_components)
    components = pca.fit_transform(X_scaled)

    # Variance explained
    var_explained = pca.explained_variance_ratio_
    cumulative_var = np.cumsum(var_explained)

    if plot:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # Scree plot
        ax1.bar(range(1, n_components+1), var_explained)
        ax1.set_xlabel('Principal Component')
        ax1.set_ylabel('Variance Explained')
        ax1.set_title('Scree Plot')

        # Cumulative variance
        ax2.plot(range(1, n_components+1), cumulative_var, 'bo-')
        ax2.axhline(y=0.85, color='r', linestyle='--', label='85% threshold')
        ax2.set_xlabel('Number of Components')
        ax2.set_ylabel('Cumulative Variance Explained')
        ax2.set_title('Cumulative Variance Explained')
        ax2.legend()

        plt.tight_layout()
        plt.show()

    # Feature importance in each component
    feature_importance = pd.DataFrame(
        pca.components_.T,
        columns=[f'PC{i+1}' for i in range(n_components)],
        index=features
    )

    # Add components to dataframe
    for i in range(n_components):
        df[f'PC{i+1}'] = components[:, i]

    return {
        'pca': pca,
        'components': components,
        'var_explained': var_explained,
        'cumulative_var': cumulative_var,
        'feature_importance': feature_importance,
        'df_with_components': df
    }

def interpret_principal_components(feature_importance, n_top=5):
    """
    Interpret principal components by top feature loadings
    """
    for col in feature_importance.columns:
        print(f"\n{col}:")
        top_features = feature_importance[col].abs().nlargest(n_top)
        for feature, loading in top_features.items():
            print(f"  {feature}: {loading:.3f}")
```

### Time-Varying PCA for Stock Prediction

**Research Finding**: "Exponential weights to price data so recent data points are weighted more heavily"

```python
def exponentially_weighted_pca(returns, halflife=60, n_components=5):
    """
    Time-varying PCA with exponential weighting
    Recent observations weighted more heavily
    """
    # Calculate exponential weights
    n_periods = len(returns)
    decay_factor = np.log(2) / halflife
    weights = np.exp(-decay_factor * np.arange(n_periods)[::-1])
    weights = weights / weights.sum()

    # Weighted covariance matrix
    centered = returns - returns.mean()
    weighted_cov = (centered.T @ np.diag(weights) @ centered) / weights.sum()

    # Eigenvalue decomposition
    eigenvalues, eigenvectors = np.linalg.eigh(weighted_cov)

    # Sort by eigenvalue (descending)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]

    # Select top components
    principal_components = eigenvectors[:, :n_components]

    # Project data
    factor_returns = returns @ principal_components

    return {
        'components': principal_components,
        'eigenvalues': eigenvalues,
        'factor_returns': factor_returns,
        'var_explained': eigenvalues / eigenvalues.sum()
    }
```

---

## Factor Analysis and Models

### Fama-French Factor Models

**Three-Factor Model (1993)**:
```
R_i - R_f = α_i + β_i(R_m - R_f) + s_i·SMB + h_i·HML + ε_i

where:
R_i - R_f = excess return on asset i
R_m - R_f = market excess return (MKT)
SMB = Small Minus Big (size factor)
HML = High Minus Low (value factor)
```

**Five-Factor Model (2015)**: Adds two factors
```
+ r_i·RMW + c_i·CMA

RMW = Robust Minus Weak (profitability factor)
CMA = Conservative Minus Aggressive (investment factor)
```

**Performance**: "Explains over 90% of diversified portfolio returns vs. 70% for CAPM"

### Factor Construction

**Implementation:**
```python
def construct_fama_french_factors(df, returns):
    """
    Construct Fama-French factors from stock universe
    """
    # Market factor (equal-weighted or value-weighted)
    market_return = returns.mean(axis=1)  # Equal-weighted
    risk_free_rate = 0.02 / 252  # Assume 2% annual
    MKT = market_return - risk_free_rate

    # Size factor (SMB - Small Minus Big)
    median_mcap = df.groupby(df.index)['market_cap'].transform('median')
    small_stocks = returns.loc[:, df['market_cap'] < median_mcap]
    big_stocks = returns.loc[:, df['market_cap'] >= median_mcap]
    SMB = small_stocks.mean(axis=1) - big_stocks.mean(axis=1)

    # Value factor (HML - High Minus Low)
    median_bm = df.groupby(df.index)['book_to_market'].transform('median')
    value_stocks = returns.loc[:, df['book_to_market'] >= median_bm]
    growth_stocks = returns.loc[:, df['book_to_market'] < median_bm]
    HML = value_stocks.mean(axis=1) - growth_stocks.mean(axis=1)

    # Profitability factor (RMW - Robust Minus Weak)
    median_profit = df.groupby(df.index)['operating_profitability'].transform('median')
    robust_stocks = returns.loc[:, df['operating_profitability'] >= median_profit]
    weak_stocks = returns.loc[:, df['operating_profitability'] < median_profit]
    RMW = robust_stocks.mean(axis=1) - weak_stocks.mean(axis=1)

    # Investment factor (CMA - Conservative Minus Aggressive)
    median_invest = df.groupby(df.index)['asset_growth'].transform('median')
    conservative_stocks = returns.loc[:, df['asset_growth'] < median_invest]
    aggressive_stocks = returns.loc[:, df['asset_growth'] >= median_invest]
    CMA = conservative_stocks.mean(axis=1) - aggressive_stocks.mean(axis=1)

    factors = pd.DataFrame({
        'MKT': MKT,
        'SMB': SMB,
        'HML': HML,
        'RMW': RMW,
        'CMA': CMA
    })

    return factors

def factor_regression_analysis(returns, factors):
    """
    Regress stock returns on factor returns
    Estimate factor loadings (betas)
    """
    from sklearn.linear_model import LinearRegression

    results = {}

    for stock in returns.columns:
        # Align data
        y = returns[stock].values.reshape(-1, 1)
        X = factors.values

        # Regression
        model = LinearRegression()
        model.fit(X, y)

        # Factor loadings
        betas = dict(zip(factors.columns, model.coef_[0]))
        alpha = model.intercept_[0]
        r_squared = model.score(X, y)

        results[stock] = {
            'alpha': alpha,
            'betas': betas,
            'r_squared': r_squared
        }

    return pd.DataFrame(results).T
```

### Using Factors for Stock Selection

**Strategy**: Select stocks with desired factor exposures

```python
def factor_based_selection(df, returns, factors, target_exposures, top_n=20):
    """
    Select stocks based on target factor exposures

    Parameters:
    -----------
    target_exposures : dict, e.g., {'HML': 1.0, 'SMB': 0.5, 'RMW': 1.0}
    """
    # Estimate factor loadings
    factor_loadings = factor_regression_analysis(returns, factors)

    # Calculate distance from target exposures
    distances = []
    for stock in factor_loadings.index:
        betas = factor_loadings.loc[stock, 'betas']
        distance = sum(
            (betas.get(factor, 0) - target_exp)**2
            for factor, target_exp in target_exposures.items()
        )
        distances.append(distance)

    factor_loadings['distance'] = distances
    factor_loadings['alpha'] = factor_loadings['alpha']

    # Select stocks with smallest distance and positive alpha
    candidates = factor_loadings[factor_loadings['alpha'] > 0]
    selected = candidates.nsmallest(top_n, 'distance')

    return selected
```

---

## Risk-Adjusted Performance Metrics

### Sharpe Ratio

**Formula**:
```
Sharpe = (R_p - R_f) / σ_p

where:
R_p = portfolio return
R_f = risk-free rate
σ_p = portfolio standard deviation
```

**Interpretation**:
- > 1.0: Very good
- > 2.0: Excellent
- > 3.0: Exceptional

**Implementation**:
```python
def sharpe_ratio(returns, risk_free_rate=0.02):
    """
    Calculate annualized Sharpe ratio
    """
    excess_returns = returns - risk_free_rate/252
    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
    return sharpe
```

### Sortino Ratio

**Formula**:
```
Sortino = (R_p - R_f) / σ_downside

where:
σ_downside = standard deviation of negative returns only
```

**Advantage**: Only penalizes downside volatility

**Benchmarks**: > 2.0 is considered good

**Implementation**:
```python
def sortino_ratio(returns, risk_free_rate=0.02, target_return=0):
    """
    Calculate annualized Sortino ratio
    """
    excess_returns = returns - risk_free_rate/252
    downside_returns = excess_returns[excess_returns < target_return]

    downside_std = np.sqrt((downside_returns**2).mean())
    sortino = np.sqrt(252) * excess_returns.mean() / downside_std

    return sortino
```

### Calmar Ratio

**Formula**:
```
Calmar = Annual Return / Maximum Drawdown
```

**Benchmarks**:
- > 0.5: Good
- > 3.0: Excellent

**Implementation**:
```python
def calmar_ratio(returns, periods_per_year=252):
    """
    Calculate Calmar ratio
    """
    # Annualized return
    cumulative_return = (1 + returns).prod()
    n_years = len(returns) / periods_per_year
    annual_return = cumulative_return ** (1/n_years) - 1

    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = abs(drawdown.min())

    calmar = annual_return / max_drawdown if max_drawdown > 0 else np.inf

    return calmar

def maximum_drawdown(returns):
    """
    Calculate maximum drawdown
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()
```

### Information Ratio

**Formula**:
```
IR = (R_p - R_b) / TE

where:
R_p = portfolio return
R_b = benchmark return
TE = tracking error (std dev of active returns)
```

**Application**: Measures risk-adjusted excess return vs. benchmark

**Implementation**:
```python
def information_ratio(portfolio_returns, benchmark_returns):
    """
    Calculate Information Ratio
    """
    active_returns = portfolio_returns - benchmark_returns
    ir = np.sqrt(252) * active_returns.mean() / active_returns.std()
    return ir
```

### Comprehensive Performance Analysis

```python
def comprehensive_performance_metrics(returns, benchmark_returns=None,
                                     risk_free_rate=0.02):
    """
    Calculate all risk-adjusted performance metrics
    """
    metrics = {}

    # Annualized return
    cumulative_return = (1 + returns).prod()
    n_years = len(returns) / 252
    metrics['Annual Return'] = cumulative_return ** (1/n_years) - 1

    # Volatility
    metrics['Annual Volatility'] = returns.std() * np.sqrt(252)

    # Sharpe Ratio
    metrics['Sharpe Ratio'] = sharpe_ratio(returns, risk_free_rate)

    # Sortino Ratio
    metrics['Sortino Ratio'] = sortino_ratio(returns, risk_free_rate)

    # Calmar Ratio
    metrics['Calmar Ratio'] = calmar_ratio(returns)

    # Maximum Drawdown
    metrics['Max Drawdown'] = maximum_drawdown(returns)

    # Information Ratio (if benchmark provided)
    if benchmark_returns is not None:
        metrics['Information Ratio'] = information_ratio(returns, benchmark_returns)

        # Tracking error
        active_returns = returns - benchmark_returns
        metrics['Tracking Error'] = active_returns.std() * np.sqrt(252)

    # Win rate
    metrics['Win Rate'] = (returns > 0).mean()

    # Skewness and Kurtosis
    metrics['Skewness'] = returns.skew()
    metrics['Kurtosis'] = returns.kurtosis()

    return pd.Series(metrics)
```

---

## Position Sizing Methods

### Kelly Criterion

**Mathematical Foundation**:

For a single bet:
```
f* = (bp - q) / b

where:
f* = optimal fraction of capital to bet
b = odds received (win amount / bet amount)
p = probability of winning
q = probability of losing (1 - p)
```

**For continuous distributions**:
```
f* = μ / σ²

where:
μ = expected excess return
σ² = variance of returns
```

**Critical Insight**: "0.10x-0.15x Kelly is recommended for professional money managers; 0.3x-0.5x for individual traders"

**Why Fractional Kelly?**
- Full Kelly maximizes geometric growth but has high volatility
- 0.5x Kelly reduces drawdown risk from 1-in-5 to 1-in-213
- Retains 51% of full Kelly growth

**Implementation**:
```python
def kelly_criterion(returns):
    """
    Calculate Kelly fraction for position sizing

    Assumes returns follow normal distribution
    """
    mean_return = returns.mean()
    variance = returns.var()

    if variance > 0:
        kelly_fraction = mean_return / variance
    else:
        kelly_fraction = 0

    return kelly_fraction

def kelly_position_sizing(stocks_df, returns_df, fraction=0.25, max_position=0.20):
    """
    Calculate position sizes using fractional Kelly criterion

    Parameters:
    -----------
    fraction : float, fractional Kelly (0.25 = quarter Kelly)
    max_position : float, maximum position size per stock
    """
    position_sizes = {}

    for ticker in stocks_df['ticker']:
        if ticker in returns_df.columns:
            stock_returns = returns_df[ticker]

            # Calculate Kelly fraction
            kelly = kelly_criterion(stock_returns)

            # Apply fractional Kelly and max position constraint
            position = min(max(0, kelly * fraction), max_position)
            position_sizes[ticker] = position

    # Normalize to sum to 1.0
    total = sum(position_sizes.values())
    if total > 0:
        position_sizes = {k: v/total for k, v in position_sizes.items()}

    stocks_df['kelly_position'] = stocks_df['ticker'].map(position_sizes)

    return stocks_df

def simulate_kelly_strategies(returns, kelly_fractions=[0.10, 0.25, 0.50, 1.0]):
    """
    Backtest different Kelly fractions
    """
    results = {}

    for frac in kelly_fractions:
        # Calculate position size
        kelly = kelly_criterion(returns)
        position = kelly * frac

        # Simulate returns
        portfolio_returns = returns * position

        # Performance metrics
        cumulative = (1 + portfolio_returns).prod()
        volatility = portfolio_returns.std() * np.sqrt(252)
        sharpe = sharpe_ratio(portfolio_returns)
        max_dd = maximum_drawdown(portfolio_returns)

        results[f'{frac}x Kelly'] = {
            'Cumulative Return': cumulative - 1,
            'Volatility': volatility,
            'Sharpe Ratio': sharpe,
            'Max Drawdown': max_dd
        }

    return pd.DataFrame(results).T
```

### Alternative Position Sizing Methods

**1. Equal Weight**:
```python
def equal_weight_sizing(n_stocks):
    return 1.0 / n_stocks
```

**2. Inverse Volatility**:
```python
def inverse_volatility_sizing(returns_df):
    """
    Weight inversely proportional to volatility
    Lower volatility → higher allocation
    """
    volatilities = returns_df.std()
    inv_vol = 1 / volatilities
    weights = inv_vol / inv_vol.sum()
    return weights
```

**3. Risk Parity**:
```python
def risk_parity_weights(cov_matrix, target_vol=0.15):
    """
    Equal risk contribution from each asset
    """
    from scipy.optimize import minimize

    n = cov_matrix.shape[0]

    def risk_contribution(weights):
        portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
        marginal_contrib = cov_matrix @ weights
        risk_contrib = weights * marginal_contrib / portfolio_vol

        # Minimize difference from equal risk contribution
        target_contrib = portfolio_vol / n
        return np.sum((risk_contrib - target_contrib)**2)

    constraints = {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    bounds = tuple((0, 1) for _ in range(n))
    initial = np.array([1/n] * n)

    result = minimize(risk_contribution, initial, method='SLSQP',
                     bounds=bounds, constraints=constraints)

    return result.x
```

---

## Portfolio Optimization

### Mean-Variance Optimization (Markowitz)

**Mathematical Formulation**:

Minimize portfolio variance:
```
minimize: w'Σw
subject to: w'μ >= R_target
            Σw_i = 1
            w_i >= 0 (long-only)
```

Maximize Sharpe ratio:
```
maximize: (w'μ - r_f) / sqrt(w'Σw)
subject to: Σw_i = 1
            0 <= w_i <= w_max
```

**Complexity**: O(n³) for quadratic programming

**Critical Issue**: "Sample covariance matrix is estimated with lots of error when n (stocks) is large relative to T (observations)"

### Ledoit-Wolf Shrinkage

**Problem**: Classical covariance estimator is poorly conditioned for large p, small n

**Solution**: Shrink toward structured estimator

```
Σ_shrunk = δF + (1-δ)S

where:
S = sample covariance matrix
F = structured target (e.g., constant correlation, identity)
δ = optimal shrinkage intensity
```

**Performance**: "Significantly lower out-of-sample variance than existing estimators, including multifactor models"

**Implementation**:
```python
from sklearn.covariance import LedoitWolf, OAS

def robust_covariance_estimation(returns):
    """
    Ledoit-Wolf shrinkage estimator for robust covariance
    """
    lw = LedoitWolf()
    cov_matrix = lw.fit(returns).covariance_
    shrinkage = lw.shrinkage_

    print(f"Optimal shrinkage intensity: {shrinkage:.4f}")

    return cov_matrix

def compare_covariance_estimators(returns):
    """
    Compare sample, Ledoit-Wolf, and OAS covariance estimators
    """
    # Sample covariance
    sample_cov = returns.cov().values

    # Ledoit-Wolf
    lw = LedoitWolf()
    lw_cov = lw.fit(returns).covariance_

    # Oracle Approximating Shrinkage (OAS)
    oas = OAS()
    oas_cov = oas.fit(returns).covariance_

    # Condition numbers (lower is better)
    print("Condition Numbers:")
    print(f"  Sample: {np.linalg.cond(sample_cov):.2e}")
    print(f"  Ledoit-Wolf: {np.linalg.cond(lw_cov):.2e}")
    print(f"  OAS: {np.linalg.cond(oas_cov):.2e}")

    return {
        'sample': sample_cov,
        'ledoit_wolf': lw_cov,
        'oas': oas_cov
    }
```

### Portfolio Optimization Methods

**1. Maximum Sharpe Ratio**:
```python
from scipy.optimize import minimize

def maximize_sharpe_portfolio(expected_returns, cov_matrix,
                              risk_free_rate=0.02, max_weight=0.20):
    """
    Find portfolio with maximum Sharpe ratio
    """
    n_assets = len(expected_returns)

    def neg_sharpe(weights):
        port_return = np.sum(expected_returns * weights)
        port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
        sharpe = (port_return - risk_free_rate) / port_vol
        return -sharpe

    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    ]

    bounds = tuple((0, max_weight) for _ in range(n_assets))

    initial_guess = np.array([1/n_assets] * n_assets)

    result = minimize(
        neg_sharpe,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'ftol': 1e-9, 'maxiter': 1000}
    )

    return result.x
```

**2. Minimum Variance**:
```python
def minimum_variance_portfolio(cov_matrix, max_weight=0.20):
    """
    Find minimum variance portfolio
    """
    n_assets = cov_matrix.shape[0]

    def portfolio_variance(weights):
        return np.dot(weights, np.dot(cov_matrix, weights))

    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
    ]

    bounds = tuple((0, max_weight) for _ in range(n_assets))

    initial_guess = np.array([1/n_assets] * n_assets)

    result = minimize(
        portfolio_variance,
        initial_guess,
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    return result.x
```

**3. Efficient Frontier**:
```python
def compute_efficient_frontier(expected_returns, cov_matrix, n_points=50):
    """
    Compute the efficient frontier
    """
    n_assets = len(expected_returns)

    # Range of target returns
    min_ret = expected_returns.min()
    max_ret = expected_returns.max()
    target_returns = np.linspace(min_ret, max_ret, n_points)

    frontier_vols = []
    frontier_weights = []

    for target_return in target_returns:
        # Minimize variance for target return
        def portfolio_variance(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
            {'type': 'eq', 'fun': lambda w: np.sum(w * expected_returns) - target_return}
        ]

        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_guess = np.array([1/n_assets] * n_assets)

        result = minimize(
            portfolio_variance,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        if result.success:
            frontier_vols.append(np.sqrt(result.fun))
            frontier_weights.append(result.x)

    return target_returns, np.array(frontier_vols), frontier_weights
```

### Black-Litterman Model

**Combines**: Market equilibrium + investor views

**Advantage**: More stable than pure mean-variance optimization

```python
def black_litterman(market_caps, cov_matrix, risk_aversion=2.5,
                    views=None, view_uncertainty=None):
    """
    Black-Litterman model for expected returns

    Parameters:
    -----------
    market_caps : market capitalization weights
    views : dict of stock: expected return view
    view_uncertainty : confidence in views
    """
    # Market equilibrium returns (reverse optimization)
    market_weights = market_caps / market_caps.sum()
    pi = risk_aversion * cov_matrix @ market_weights

    if views is None:
        return pi  # Pure equilibrium

    # Incorporate views (simplified version)
    tau = 0.025  # Uncertainty in equilibrium

    # ... full Black-Litterman calculation
    # (simplified here for brevity)

    return pi
```

---

## Data Preprocessing and Normalization

### Cross-Sectional Z-Score Normalization

**Purpose**: Standardize features at each time point for fair comparison

**Formula**:
```
z_i,t = (x_i,t - μ_t) / σ_t

where:
i = stock index
t = time index
μ_t = mean across all stocks at time t
σ_t = std dev across all stocks at time t
```

**Implementation**:
```python
def cross_sectional_zscore(df, features, by_date=True):
    """
    Cross-sectional z-score normalization

    Normalizes each feature across stocks at each time point
    """
    df_normalized = df.copy()

    if by_date and 'date' in df.columns:
        # Group by date and normalize
        for feature in features:
            df_normalized[f'{feature}_zscore'] = df.groupby('date')[feature].transform(
                lambda x: (x - x.mean()) / x.std()
            )
    else:
        # Single cross-section
        for feature in features:
            mean = df[feature].mean()
            std = df[feature].std()
            df_normalized[f'{feature}_zscore'] = (df[feature] - mean) / std

    return df_normalized
```

### Percentile Ranking

**Advantage**: Robust to outliers and non-normal distributions

**Implementation**:
```python
def percentile_ranking(df, features):
    """
    Convert features to percentile ranks (0-100)
    """
    df_ranked = df.copy()

    for feature in features:
        df_ranked[f'{feature}_pctile'] = df[feature].rank(pct=True) * 100

    return df_ranked

def create_composite_percentile_score(df, factor_weights):
    """
    Create weighted composite score from percentile ranks

    Parameters:
    -----------
    factor_weights : dict of {feature: weight}
    """
    composite = 0
    total_weight = sum(factor_weights.values())

    for feature, weight in factor_weights.items():
        pctile_col = f'{feature}_pctile'
        if pctile_col in df.columns:
            composite += df[pctile_col] * (weight / total_weight)

    df['composite_percentile'] = composite

    return df
```

### Handling Missing Data

**Strategies**:
1. **Forward fill**: Use last known value
2. **Industry/Sector median**: Fill with peer group median
3. **Model-based imputation**: Use ML to predict missing values

**Implementation**:
```python
def handle_missing_data(df, method='median', by_sector=True):
    """
    Handle missing data in stock features
    """
    df_clean = df.copy()

    if method == 'forward_fill':
        df_clean = df_clean.fillna(method='ffill')

    elif method == 'median':
        if by_sector and 'sector' in df.columns:
            # Fill with sector median
            for col in df.select_dtypes(include=[np.number]).columns:
                df_clean[col] = df.groupby('sector')[col].transform(
                    lambda x: x.fillna(x.median())
                )
        else:
            # Fill with overall median
            df_clean = df_clean.fillna(df_clean.median())

    elif method == 'drop':
        df_clean = df_clean.dropna()

    return df_clean
```

---

## Backtesting and Validation

### Walk-Forward Analysis

**Gold Standard** for trading strategy validation

**Process**:
1. Divide data into rolling windows
2. Optimize on in-sample window
3. Test on out-of-sample window
4. Roll forward and repeat

**Advantages**:
- Reduces overfitting
- Simulates real-world adaptive trading
- Tests strategy robustness over time

**Implementation**:
```python
def walk_forward_analysis(df, returns, strategy_func,
                         train_period=252, test_period=63,
                         step_size=21):
    """
    Walk-forward optimization and testing

    Parameters:
    -----------
    train_period : days for training (e.g., 252 = 1 year)
    test_period : days for testing (e.g., 63 = 1 quarter)
    step_size : days to roll forward (e.g., 21 = 1 month)
    """
    results = []

    start_idx = 0
    while start_idx + train_period + test_period < len(df):
        # Split data
        train_end = start_idx + train_period
        test_end = train_end + test_period

        train_data = df.iloc[start_idx:train_end]
        test_data = df.iloc[train_end:test_end]

        train_returns = returns.iloc[start_idx:train_end]
        test_returns = returns.iloc[train_end:test_end]

        # Optimize strategy on training data
        selected_stocks = strategy_func(train_data, train_returns)

        # Test on out-of-sample data
        if len(selected_stocks) > 0:
            test_stock_returns = test_returns[selected_stocks['ticker']]
            portfolio_return = test_stock_returns.mean(axis=1).mean()

            results.append({
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'n_stocks': len(selected_stocks),
                'oos_return': portfolio_return,
                'selected_stocks': selected_stocks['ticker'].tolist()
            })

        # Roll forward
        start_idx += step_size

    return pd.DataFrame(results)

def walk_forward_performance(wf_results):
    """
    Analyze walk-forward results
    """
    metrics = {
        'Total OOS Return': wf_results['oos_return'].sum(),
        'Avg OOS Return': wf_results['oos_return'].mean(),
        'OOS Std Dev': wf_results['oos_return'].std(),
        'OOS Sharpe': wf_results['oos_return'].mean() / wf_results['oos_return'].std() * np.sqrt(252/63),
        'Win Rate': (wf_results['oos_return'] > 0).mean(),
        'Avg Stocks Selected': wf_results['n_stocks'].mean()
    }

    return pd.Series(metrics)
```

### Combinatorially Purged Cross-Validation (CPCV)

**Research Finding (2024)**: "CPCV demonstrates stability and efficiency vs. Walk-Forward's temporal variability and weaker stationarity"

**Purpose**: Better address overfitting than traditional methods

### Overfitting Detection

**Signs of Overfitting**:
1. Large gap between in-sample and out-of-sample performance
2. Many parameters optimized
3. Perfect or near-perfect training performance
4. Unstable performance across different time periods

**Implementation**:
```python
def detect_overfitting(strategy_results):
    """
    Detect potential overfitting in strategy results
    """
    is_results = strategy_results['in_sample']
    oos_results = strategy_results['out_of_sample']

    # Performance gap
    is_sharpe = is_results['sharpe_ratio']
    oos_sharpe = oos_results['sharpe_ratio']
    sharpe_degradation = (is_sharpe - oos_sharpe) / is_sharpe

    # Correlation of returns
    return_correlation = np.corrcoef(
        is_results['returns'],
        oos_results['returns']
    )[0, 1]

    warnings = []

    if sharpe_degradation > 0.50:
        warnings.append(f"Large Sharpe degradation: {sharpe_degradation:.1%}")

    if return_correlation < 0.3:
        warnings.append(f"Low IS/OOS correlation: {return_correlation:.2f}")

    if is_sharpe > 3.0 and oos_sharpe < 1.0:
        warnings.append("Suspiciously high IS Sharpe with poor OOS performance")

    overfitting_score = sharpe_degradation * 0.5 + (1 - return_correlation) * 0.5

    return {
        'overfitting_score': overfitting_score,
        'sharpe_degradation': sharpe_degradation,
        'return_correlation': return_correlation,
        'warnings': warnings,
        'likely_overfit': overfitting_score > 0.5
    }
```

---

## Machine Learning Integration

### Gradient Boosting (XGBoost, LightGBM)

**Research Finding**: "LambdaMART (gradient boosted trees) best performer across profitability, ranking accuracy, and risk metrics"

**Advantages**:
- Handles non-linear relationships
- Automatic feature interaction detection
- Robust to outliers
- Fast training with large datasets

**Implementation**:
```python
import xgboost as xgb
from lightgbm import LGBMRegressor

def train_gradient_boosting_ranker(X_train, y_train, X_test):
    """
    Train gradient boosting model for stock ranking
    """
    # XGBoost Ranker
    xgb_model = xgb.XGBRanker(
        objective='rank:pairwise',
        learning_rate=0.1,
        n_estimators=100,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8
    )

    # Create group structure (stocks per time period)
    # Assumes data is sorted by date
    group_sizes = [len(X_train)]  # Simplified - should be groups by date

    xgb_model.fit(X_train, y_train, group=group_sizes)

    # Predict scores
    scores = xgb_model.predict(X_test)

    return scores, xgb_model

def lightgbm_stock_selection(df, features, target='forward_return', top_n=20):
    """
    Use LightGBM for stock selection
    """
    # Prepare data
    X = df[features]
    y = df[target]

    # Train/test split (time-series aware)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Train LightGBM
    model = LGBMRegressor(
        n_estimators=100,
        learning_rate=0.05,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X_train, y_train)

    # Predict on test set
    predictions = model.predict(X_test)

    # Select top stocks
    test_df = df.iloc[split_idx:].copy()
    test_df['prediction'] = predictions
    selected = test_df.nlargest(top_n, 'prediction')

    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return selected, feature_importance
```

### Random Forest

**Research Finding**: "Random forests outperform gradient-boosted trees and deep neural networks in some stock selection applications"

**Implementation**:
```python
from sklearn.ensemble import RandomForestRegressor

def random_forest_stock_ranking(df, features, target='forward_return'):
    """
    Random forest for stock ranking
    """
    X = df[features]
    y = df[target]

    # Time-series split
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Train Random Forest
    rf = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        min_samples_split=20,
        min_samples_leaf=10,
        max_features='sqrt',
        n_jobs=-1,
        random_state=42
    )

    rf.fit(X_train, y_train)

    # Predict
    predictions = rf.predict(X_test)

    # OOB score (out-of-bag estimate)
    rf_oob = RandomForestRegressor(
        n_estimators=100,
        oob_score=True,
        random_state=42
    )
    rf_oob.fit(X_train, y_train)

    print(f"OOB Score: {rf_oob.oob_score_:.4f}")

    return predictions, rf
```

### Ensemble Methods

**Research Finding**: "Ensemble methods combining all models achieved 0.45% daily return vs. 0.43% for RF, 0.37% for GBT, 0.33% for DNN"

**Implementation**:
```python
from sklearn.ensemble import VotingRegressor, StackingRegressor

def ensemble_stock_selection(X_train, y_train, X_test):
    """
    Ensemble combining multiple ML models
    """
    # Base models
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    xgb_model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    lgbm = LGBMRegressor(n_estimators=100, random_state=42)

    # Stacking ensemble
    stacking = StackingRegressor(
        estimators=[
            ('rf', rf),
            ('xgb', xgb_model),
            ('lgbm', lgbm)
        ],
        final_estimator=Ridge(alpha=1.0),
        cv=5
    )

    stacking.fit(X_train, y_train)
    predictions = stacking.predict(X_test)

    return predictions, stacking
```

---

## Computational Considerations

### Vectorization and Parallel Processing

**SIMD Vectorization**: Process 8 data elements simultaneously with AVX-512

**GPU Acceleration**: RTX 4090 with 16,384 CUDA cores for parallel computation

**Implementation Strategies**:

**1. Pandas Vectorization**:
```python
# Slow (loop)
for i in range(len(df)):
    df.loc[i, 'score'] = calculate_score(df.loc[i])

# Fast (vectorized)
df['score'] = (df['value'] * 0.3 + df['momentum'] * 0.3 + df['quality'] * 0.4)
```

**2. NumPy Broadcasting**:
```python
# Calculate returns for all stocks simultaneously
returns_matrix = (prices[1:] / prices[:-1]) - 1
```

**3. Parallel Processing with Joblib**:
```python
from joblib import Parallel, delayed

def process_stock(ticker, data):
    # Process individual stock
    return result

# Parallel execution
results = Parallel(n_jobs=-1)(
    delayed(process_stock)(ticker, data[ticker])
    for ticker in tickers
)
```

**4. Dask for Large Datasets**:
```python
import dask.dataframe as dd

# Load large dataset
ddf = dd.read_csv('large_stock_data.csv')

# Parallel computation
result = ddf.groupby('ticker')['return'].mean().compute()
```

### Computational Complexity Summary

| Operation | Complexity | Scalability (1000 stocks) |
|-----------|-----------|--------------------------|
| Basic filters | O(n) | Excellent |
| K-means | O(n·k·i·p) | Good |
| Hierarchical clustering | O(n²log n) | Moderate |
| PCA | O(min(n²p, np²)) | Good |
| Mahalanobis (MCD) | O(p²·n·log n) | Good |
| Mean-variance opt | O(n³) | Moderate |
| Gradient boosting | O(n·log n·d·t) | Excellent |
| Walk-forward backtest | O(w·s) | Good |

**Key**: n = stocks, p = features, k = clusters, i = iterations, d = depth, t = trees, w = windows, s = strategy complexity

### Memory Optimization

**1. Data Types**:
```python
def optimize_dtypes(df):
    """
    Reduce memory usage by optimizing data types
    """
    for col in df.select_dtypes(include=['float']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')

    for col in df.select_dtypes(include=['int']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')

    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:
            df[col] = df[col].astype('category')

    return df
```

**2. Chunking**:
```python
def process_in_chunks(data, chunk_size=1000):
    """
    Process large dataset in chunks
    """
    results = []

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        result = process_chunk(chunk)
        results.append(result)

    return pd.concat(results)
```

---

## Implementation Guide

### Complete Pipeline

```python
class StockFilteringPipeline:
    """
    End-to-end stock filtering pipeline
    From 3000+ stocks to top 10
    """

    def __init__(self, config=None):
        self.config = config or self.default_config()
        self.results = {}

    @staticmethod
    def default_config():
        return {
            'stage1': {
                'min_market_cap': 500e6,
                'min_avg_volume': 1e6,
                'min_price': 5,
                'min_history_days': 252
            },
            'stage2': {
                'contamination': 0.33,
                'winsorize_limits': (0.05, 0.05)
            },
            'stage3': {
                'n_clusters': 10,
                'top_pct_per_cluster': 0.20,
                'factor_weights': {
                    'value': 0.3,
                    'momentum': 0.3,
                    'quality': 0.2,
                    'low_vol': 0.2
                }
            },
            'stage4': {
                'n_pca_components': 10,
                'top_n': 50
            },
            'stage5': {
                'optimization_method': 'max_sharpe',
                'target_n': 10,
                'max_weight': 0.20,
                'kelly_fraction': 0.25
            }
        }

    def run_pipeline(self, df, returns_df):
        """
        Execute complete filtering pipeline
        """
        print(f"Starting pipeline with {len(df)} stocks")

        # Stage 1: Exclusion filters
        df_s1 = self.stage1_exclusion(df)
        print(f"After Stage 1 (Exclusion): {len(df_s1)} stocks")

        # Stage 2: Outlier detection
        df_s2 = self.stage2_outliers(df_s1)
        print(f"After Stage 2 (Outlier Removal): {len(df_s2)} stocks")

        # Stage 3: Clustering and factor scoring
        df_s3 = self.stage3_clustering(df_s2)
        print(f"After Stage 3 (Clustering): {len(df_s3)} stocks")

        # Stage 4: PCA and ranking
        df_s4 = self.stage4_pca_ranking(df_s3)
        print(f"After Stage 4 (PCA/Ranking): {len(df_s4)} stocks")

        # Stage 5: Portfolio optimization
        df_s5 = self.stage5_optimization(df_s4, returns_df)
        print(f"Final Selection (Stage 5): {len(df_s5)} stocks")

        return df_s5

    def stage1_exclusion(self, df):
        cfg = self.config['stage1']
        return stage1_exclusion_filter(
            df,
            min_market_cap=cfg['min_market_cap'],
            min_avg_volume=cfg['min_avg_volume'],
            min_price=cfg['min_price'],
            min_history_days=cfg['min_history_days']
        )

    def stage2_outliers(self, df):
        cfg = self.config['stage2']

        features = ['return_12m', 'volatility', 'beta', 'market_cap',
                   'book_to_market', 'roe', 'debt_to_equity']

        # Winsorize
        df = winsorize_features(df, features, limits=cfg['winsorize_limits'])

        # Robust outlier detection
        df = stage2_outlier_detection(df, features, cfg['contamination'])

        return df

    def stage3_clustering(self, df):
        cfg = self.config['stage3']
        return stage3_clustering_selection(
            df,
            n_clusters=cfg['n_clusters'],
            top_pct_per_cluster=cfg['top_pct_per_cluster']
        )

    def stage4_pca_ranking(self, df):
        cfg = self.config['stage4']
        return stage4_pca_ranking(
            df,
            n_components=cfg['n_pca_components'],
            top_n=cfg['top_n']
        )

    def stage5_optimization(self, df, returns_df):
        cfg = self.config['stage5']
        return stage5_portfolio_optimization(
            df,
            returns_df,
            target_n=cfg['target_n'],
            method=cfg['optimization_method']
        )

# Usage example
if __name__ == '__main__':
    # Load data
    df = pd.read_csv('stock_universe.csv')
    returns = pd.read_csv('stock_returns.csv', index_col=0)

    # Run pipeline
    pipeline = StockFilteringPipeline()
    final_selection = pipeline.run_pipeline(df, returns)

    # Display results
    print("\nFinal Stock Selection:")
    print(final_selection[['ticker', 'composite_score', 'weight',
                          'kelly_fraction', 'expected_return']])
```

---

## References and Further Reading

### Academic Papers

1. **Harvey, C.R., Liu, Y., & Zhu, H. (2016)**. "...and the Cross-Section of Expected Returns." Review of Financial Studies.
   - Multiple testing correction framework
   - t-ratio threshold of 3.0

2. **Ledoit, O., & Wolf, M. (2003)**. "Improved Estimation of the Covariance Matrix of Stock Returns with an Application to Portfolio Selection." Journal of Empirical Finance.
   - Shrinkage estimator for robust covariance

3. **Fama, E.F., & French, K.R. (2015)**. "A Five-Factor Asset Pricing Model." Journal of Financial Economics.
   - Extended factor model

4. **Kelly, J.L. (1956)**. "A New Interpretation of Information Rate." Bell System Technical Journal.
   - Kelly criterion for optimal betting

5. **Markowitz, H. (1952)**. "Portfolio Selection." Journal of Finance.
   - Modern Portfolio Theory foundation

### Books

1. **Advances in Financial Machine Learning** - Marcos López de Prado
2. **Quantitative Portfolio Management** - Michael Isichenko
3. **Active Portfolio Management** - Grinold & Kahn
4. **Machine Learning for Asset Managers** - Marcos López de Prado

### Online Resources

1. **Ken French Data Library**: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
2. **SSRN Quantitative Finance**: https://www.ssrn.com/index.cfm/en/janda/quantitative-finance/
3. **Quantopian Lectures** (archived): https://github.com/quantopian/research_public

---

## Conclusion

This research document provides a comprehensive framework for filtering large stock universes (1000+) down to optimal selections (10-20 stocks) using rigorous statistical methods:

**Key Takeaways**:

1. **Progressive Filtering**: 5-stage funnel systematically reduces universe
2. **Statistical Rigor**: Harvey-Liu-Zhu threshold (t > 3.0) for factor validation
3. **Robust Methods**: MCD for outliers, Ledoit-Wolf for covariance
4. **Diversification**: Clustering ensures representation across regimes
5. **Risk Management**: Kelly criterion, Sharpe/Sortino/Calmar ratios
6. **Validation**: Walk-forward analysis to prevent overfitting
7. **Computational Efficiency**: Vectorization, parallelization for scalability

**Recommended Pipeline**:
- Stage 1 (O(n)): Basic exclusion filters
- Stage 2 (O(n·p²)): Robust outlier detection
- Stage 3 (O(n·k·i·p)): Clustering and factor scoring
- Stage 4 (O(n·p²)): PCA and composite ranking
- Stage 5 (O(p³)): Portfolio optimization with Kelly sizing

This framework balances statistical sophistication with computational practicality, suitable for both academic research and professional quantitative trading.

---

**End of Research Document**
