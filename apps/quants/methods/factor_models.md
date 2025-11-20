# Factor Models in Quantitative Finance

## Overview

Factor models explain asset returns using systematic risk factors. This document outlines the implementation of Fama-French factor models, momentum factors, and related analytical methods.

## 1. Factor Model Foundation

### 1.1 Fama-French Three-Factor Model

The classic three-factor model explains returns as:

$$r_p - r_f = \alpha + \beta_{MKT}(r_m - r_f) + \beta_{SMB} \cdot SMB + \beta_{HML} \cdot HML + \epsilon$$

**Components:**
- **Market Factor (MKT):** Excess return of market portfolio
- **Size Factor (SMB):** Small Minus Big - return spread between small and large cap stocks
- **Value Factor (HML):** High Minus Low - return spread between high and low book-to-market stocks

### 1.2 Fama-French Five-Factor Model

Extended model includes additional factors:

$$r_p - r_f = \alpha + \beta_{MKT}(r_m - r_f) + \beta_{SMB} \cdot SMB + \beta_{HML} \cdot HML + \beta_{RMW} \cdot RMW + \beta_{CMA} \cdot CMA + \epsilon$$

**Additional Components:**
- **Profitability Factor (RMW):** Robust Minus Weak - return spread between high and low profitability firms
- **Investment Factor (CMA):** Conservative Minus Aggressive - return spread between low and high asset growth firms

### 1.3 Momentum Factor

Momentum captures the tendency of assets to continue outperforming or underperforming:

$$r_p - r_f = \alpha + \beta_{MKT}(r_m - r_f) + \beta_{MOM} \cdot MOM + \epsilon$$

## 2. Factor Construction Methods

### 2.1 SMB (Size Factor) Construction

**Process:**
1. Sort securities by market capitalization
2. Divide into percentile groups (typically 30th, 70th)
3. Calculate returns for small-cap and large-cap portfolios
4. SMB = Return(Small) - Return(Large)

**Interpretation:**
- Positive SMB: Small caps outperform large caps
- Captures size/liquidity risk premium
- High exposure indicates small-cap tilt

### 2.2 HML (Value Factor) Construction

**Process:**
1. Calculate book-to-market ratio for each security
2. Sort by book-to-market percentiles
3. Create high (top 30%) and low (bottom 30%) value portfolios
4. HML = Return(High BtM) - Return(Low BtM)

**Interpretation:**
- Positive HML: Value stocks outperform growth stocks
- Captures value risk premium
- High positive exposure indicates value tilt

### 2.3 RMW (Profitability Factor) Construction

**Process:**
1. Measure profitability (ROE, operating profitability, etc.)
2. Sort securities by profitability percentiles
3. Create robust and weak profitability portfolios
4. RMW = Return(Robust) - Return(Weak)

**Interpretation:**
- Positive RMW: High profitability stocks outperform
- Captures quality/profitability premium
- High exposure indicates quality bias

### 2.4 CMA (Investment Factor) Construction

**Process:**
1. Measure investment intensity (asset growth, capex/assets)
2. Sort by investment percentiles
3. Create conservative (low investment) and aggressive (high investment) portfolios
4. CMA = Return(Conservative) - Return(Aggressive)

**Interpretation:**
- Positive CMA: Conservative investment strategies outperform
- Captures over-investment risk premium
- High exposure indicates preference for low-growth firms

### 2.5 MOM (Momentum Factor) Construction

**Process:**
1. Calculate past returns over lookback period (typically 12 months)
2. Skip recent period to avoid reversal effects
3. Sort securities by momentum scores
4. Create long (top performers) and short (poor performers) portfolios
5. MOM = Return(Winners) - Return(Losers)

**Interpretation:**
- Positive MOM: Momentum strategies are profitable
- Captures continuation of returns
- High exposure indicates trend-following positions

## 3. Factor Model Analysis

### 3.1 Regression Analysis

**Objective:** Estimate factor exposures and alpha

**Linear Regression:**
$$y = \alpha + X\beta + \epsilon$$

Where:
- y: Excess portfolio returns
- X: Factor returns matrix
- β: Factor loadings (exposures)
- α: Intercept (alpha)
- ε: Regression residuals

**Output Metrics:**
- **Alpha:** Risk-adjusted return independent of factors
- **Beta:** Sensitivity to each factor
- **R-squared:** Proportion of return variation explained
- **Standard Error:** Uncertainty in beta estimates
- **t-statistics:** Statistical significance of factors

### 3.2 Factor Exposures

**Definition:** Beta coefficients measure portfolio sensitivity to factors

**Interpretation:**
- β = 1.0: Factor sensitivity equal to benchmark
- β > 1.0: High factor sensitivity
- β < 0: Inverse relationship with factor

**Uses:**
- Style analysis
- Risk attribution
- Portfolio construction
- Performance attribution

### 3.3 Alpha and Beta Estimation

**Alpha Calculation:**
$$\alpha = r_p - r_f - \sum_i \beta_i \cdot (f_i - r_f)$$

- Represents return not explained by factor exposures
- Annualized for comparison with annual benchmarks

**Beta Estimation Methods:**
1. **OLS Regression:** Ordinary least squares
2. **Regularized Regression:** Ridge/Lasso for high-dimensional data
3. **Rolling Betas:** Time-varying factor exposures
4. **Robust Estimation:** For non-normal distributions

## 4. Statistical Analysis

### 4.1 Performance Metrics

**Return Metrics:**
- Total Return: Cumulative return over period
- Annual Return: Annualized total return
- Excess Return: Return above risk-free rate

**Risk Metrics:**
- Volatility: Standard deviation of returns
- Maximum Drawdown: Peak-to-trough decline
- Value at Risk (VaR): Tail risk measure

**Risk-Adjusted Metrics:**
- **Sharpe Ratio:** Return per unit of risk
  $$SR = \frac{r_p - r_f}{\sigma_p}$$

- **Sortino Ratio:** Return per unit of downside risk
- **Calmar Ratio:** Return relative to maximum drawdown
- **Information Ratio:** Excess return per unit of tracking error

### 4.2 Residual Analysis

**Components:**
- **Mean:** Should be close to zero (no systematic bias)
- **Standard Deviation:** Unexplained return volatility
- **Skewness:** Asymmetry of return distribution
- **Kurtosis:** Tail behavior
- **Jarque-Bera Test:** Normality test
- **Autocorrelation:** Serial dependence in residuals

**Diagnostics:**
- Non-zero mean: Suggests missing factors
- High skewness/kurtosis: Non-normal returns
- Autocorrelation: Return predictability

### 4.3 Factor Correlation Analysis

**Purpose:** Understand factor diversification

**Key Points:**
- High correlation: Factors move together, limited diversification
- Low correlation: Factors provide independent information
- Negative correlation: Natural hedge properties

**Matrix Interpretation:**
- Diagonal: Factor variance
- Off-diagonal: Factor covariance/correlation
- Condition number: Multicollinearity assessment

## 5. Factor Portfolio Construction

### 5.1 Long-Short Portfolios

**Strategy:**
1. Rank securities by factor exposure
2. Long: High-exposure securities (top 30%)
3. Short: Low-exposure securities (bottom 30%)
4. Gain from factor premium (long - short spread)

**Characteristics:**
- Market-neutral (balanced long/short)
- Isolates factor premium
- Self-financing structure
- Limited capital requirement

### 5.2 Weighted Portfolios

**Construction:**
1. Calculate factor exposures for each security
2. Weight portfolio by factor scores
3. Concentrate capital in high-exposure securities

**Variants:**
- Equal weight
- Market-cap weight
- Inverse volatility weight
- Factor-score weight

### 5.3 Factor Mimicking Portfolios

**Purpose:** Create tradable implementations of factors

**Methods:**
1. Linear optimization approach
2. Minimize tracking error to factor
3. Subject to constraints (leverage, turnover)

**Applications:**
- Enhanced indexing
- Systematic factor allocation
- Factor investing strategies

## 6. Implementation Details

### 6.1 Class Structure

#### FactorModel
**Main class for factor regression and analysis**
- `factor_regression()`: OLS regression analysis
- `calculate_exposure()`: Beta estimation
- `calculate_alpha()`: Alpha calculation
- `residual_analysis()`: Statistical diagnostics

#### FactorConstruction
**Factor construction methods**
- `construct_smb()`: Size factor
- `construct_hml()`: Value factor
- `construct_rmw()`: Profitability factor
- `construct_cma()`: Investment factor
- `construct_momentum()`: Momentum factor

#### FactorPortfolioConstruction
**Portfolio construction utilities**
- `construct_long_short_portfolio()`: Long-short positions
- `construct_weighted_portfolio()`: Weighted allocation

#### FactorAnalysis
**Statistical analysis tools**
- `calculate_performance_metrics()`: Risk-return metrics
- `factor_correlation_matrix()`: Correlation analysis
- `factor_contribution_analysis()`: Attribution analysis
- `style_factor_analysis()`: Style decomposition

### 6.2 Key Parameters

**Factor Construction:**
- Percentile cutoffs: 30th/70th (adjustable)
- Rebalancing frequency: Monthly/Quarterly
- Momentum lookback: 12 months typical
- Skip period: 1 month (avoid microstructure bias)

**Regression Analysis:**
- Frequency: Daily, weekly, monthly
- Rolling window: 1-5 years
- OLS vs. robust methods
- Intercept estimation

### 6.3 Data Requirements

**Minimum Data Needed:**
- Security returns (daily/weekly/monthly)
- Market values or capitalizations
- Fundamental data (book value, profitability, growth)
- Risk-free rate series

**Quality Considerations:**
- Missing data handling
- Survivorship bias
- Look-ahead bias
- Delisting adjustments

## 7. Practical Applications

### 7.1 Portfolio Analysis
- Decompose returns into factor contributions
- Identify concentrated factor exposures
- Assess style drift
- Benchmark against factor indices

### 7.2 Risk Management
- Quantify systematic risk (betas)
- Monitor factor exposures
- Stress test factor scenarios
- Set factor-based risk limits

### 7.3 Performance Attribution
- Isolate alpha from factor returns
- Identify manager skill
- Compare portfolios on factor basis
- Adjust for market conditions

### 7.4 Factor Investing Strategy
- Build factor-based portfolios
- Rotate between factors
- Combine factors efficiently
- Manage factor crowding

## 8. Mathematical Formulations

### 8.1 OLS Regression
$$\beta = (X'X)^{-1}X'y$$

### 8.2 Beta Standard Error
$$SE(\beta) = \sqrt{MSE \cdot (X'X)^{-1}}$$

### 8.3 Adjusted R-squared
$$R^2_{adj} = 1 - \frac{(1-R^2)(n-1)}{n-k}$$

### 8.4 Sharpe Ratio
$$SR = \frac{E[r_p - r_f]}{\sigma[r_p - r_f]}$$

### 8.5 Information Ratio
$$IR = \frac{E[r_p - r_b]}{\sigma[r_p - r_b]}$$

## 9. References and Further Reading

### Key Academic Papers
- Fama & French (1993): "Common Risk Factors in Stock Returns"
- Fama & French (2015): "Five-Factor Model"
- Carhart (1997): "Mutual Fund Performance"
- Jegadeesh & Titman (1993): "Momentum in Stock Returns"

### Data Sources
- Kenneth French Data Library
- CRSP/Compustat
- Bloomberg Terminal
- FactSet
- Refinitiv

## 10. Usage Examples

### Basic Factor Model Analysis
```python
from factor_models import FactorModel
import pandas as pd

# Load data
returns = pd.read_csv('returns.csv', index_col=0, parse_dates=True)
factors = pd.read_csv('factors.csv', index_col=0, parse_dates=True)

# Create model
fm = FactorModel(returns, factors)

# Analyze
result = fm.factor_regression(asset_index=0)
exposures = fm.calculate_exposure()
alphas = fm.calculate_alpha()
```

### Factor Construction
```python
from factor_models import FactorConstruction

# Construct factors from data
smb = FactorConstruction.construct_smb(market_cap, returns)
hml = FactorConstruction.construct_hml(book_to_market, returns)
rmw = FactorConstruction.construct_rmw(profitability, returns)
```

### Performance Analysis
```python
from factor_models import FactorAnalysis

# Calculate metrics
metrics = FactorAnalysis.calculate_performance_metrics(portfolio_returns)
corr = FactorAnalysis.factor_correlation_matrix(factors)
```

## 11. Best Practices

1. **Data Quality:** Ensure clean, survivorship-bias-adjusted data
2. **Standardization:** Use consistent measurement periods
3. **Diversification:** Avoid concentrated factor exposures
4. **Rebalancing:** Regular portfolio rebalancing
5. **Constraints:** Include realistic constraints (leverage, capacity)
6. **Monitoring:** Track factor exposures over time
7. **Robustness:** Test across time periods and markets
8. **Documentation:** Record all assumptions and methodology

## 12. Common Pitfalls

1. **Look-ahead bias:** Using future data in construction
2. **Overfitting:** Too many factors relative to data
3. **Survivorship bias:** Ignoring delisted securities
4. **Multicollinearity:** Correlated factors causing instability
5. **Parameter drift:** Assuming constant factor structure
6. **Crowding:** Ignoring capacity constraints
7. **Cost omission:** Ignoring transaction costs
8. **Regime changes:** Missing structural market changes
