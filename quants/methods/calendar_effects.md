# Calendar Effects Analysis

## Overview

Calendar effects are documented anomalies in asset returns that occur at specific times of the year, month, week, or around holidays. These effects suggest that market returns exhibit systematic patterns related to calendar dates, contradicting the Efficient Market Hypothesis. This document details the implementation of five key calendar effects used for quantitative trading.

---

## 1. Day-of-Week Effect (Monday Effect)

### Strategy Overview

The day-of-week effect examines whether average returns differ systematically across weekdays. The most prominent manifestation is the **Monday Effect**, where returns on Mondays tend to be significantly lower than other weekdays.

### Theoretical Basis

- **Tax-Loss Harvesting**: Investors realize losses on Friday and reinvest on Monday
- **Information Processing**: Negative news over the weekend gets factored in Monday morning
- **Behavioral Factors**: Weekend sentiment carries into Monday trading

### How It Works

1. Calculate daily returns for each trading day
2. Segment returns by day of week (Monday-Friday)
3. Compute mean, standard deviation, and median for each day
4. Conduct ANOVA test to detect overall weekday differences
5. Perform t-test comparing Monday returns to other days

### Statistical Tests

**ANOVA (Analysis of Variance):**
```
H₀: μ_Monday = μ_Tuesday = ... = μ_Friday
H₁: At least one mean differs

F-statistic = (Between-group variance) / (Within-group variance)
p-value indicates significance of differences
```

**Two-Sample t-test:**
```
H₀: μ_Monday = μ_Other_Days
t-statistic = (M_Monday - M_Other) / SE(difference)
```

### Trading Signal Logic

- **BUY Signal**: When Monday effect is significant and Monday returns < other days (avoid Monday trading)
- **SELL Signal**: When Monday returns significantly negative
- **Confidence**: 1 - p_value (higher statistical significance = higher confidence)

### Empirical Findings

- Monday returns typically 0.1-0.5% lower than other days
- Effect stronger in some markets (US, UK, Japan)
- Diminishing but still observable in modern markets
- More pronounced in smaller-cap stocks

### Recommended Parameters

- Minimum data: 5 days per week for 52+ weeks
- Significance level: α = 0.05
- Best for: Intraday to weekly strategies

---

## 2. January Effect

### Strategy Overview

The January Effect is the tendency for stock prices to increase more in January than any other month of the year. This calendar anomaly has been extensively documented and represents one of the most studied seasonal patterns.

### Theoretical Basis

- **Tax-Loss Harvesting Reversal**: Tax losses sold in December are repurchased in January
- **Window Dressing**: Fund managers buy stocks to improve year-end portfolio appearance in January
- **Year-End Bonuses**: Employee bonuses received in December are invested in January
- **New Year Optimism**: Positive sentiment at calendar year start

### How It Works

1. Group price data by calendar year and month
2. Calculate monthly returns: (End_Price - Start_Price) / Start_Price
3. Segment returns into January and non-January months
4. Compute descriptive statistics for each group
5. Apply t-test and Mann-Whitney U test for non-parametric validation

### Statistical Tests

**Parametric t-test:**
```
t = (M_Jan - M_Other) / √[(s²_Jan/n_Jan) + (s²_Other/n_Other)]
degrees of freedom = n_Jan + n_Other - 2
```

**Mann-Whitney U Test (Non-parametric):**
```
U-statistic = sum of ranks comparison
p-value = probability of observing data if groups identical
```

### Trading Signal Logic

- **BUY Signal**: When January effect is significant (p < 0.05) and effect_direction = 'positive'
- **Signal Timing**: Initiate positions late December through early January
- **Confidence**: min(0.85, 1.0 - p_value)
- **Return Mean**: Historical average January return

### Empirical Evidence

- Average January return: +2% to +5% (stock indices)
- Effect size larger for small-cap stocks
- Documented in multiple countries and asset classes
- Effect has weakened post-discovery but remains detectable

### Risk Considerations

- Effect not present in every year
- Return reversals possible
- Market microstructure changes may reduce effect
- Crowded trade risk if widely known

---

## 3. Turn-of-Month Strategy

### Strategy Overview

The Turn-of-Month (TOM) effect represents the tendency for stock returns to be abnormally high around month boundaries. Specifically, the last few trading days of a month and the first few days of the next month show elevated average returns.

### Theoretical Basis

- **Cash Flow Timing**: Monthly salaries, dividends reinvested at month-end
- **Portfolio Rebalancing**: Month-end rebalancing drives increased demand
- **Option Expiration**: Monthly options expiration effects
- **Institutional Flows**: Large fund flows at period boundaries

### How It Works

1. Define TOM period: Last N days of month + First N days of next month (default: 3 days each)
2. Calculate daily returns for entire period
3. Segment returns into TOM and mid-month periods
4. Compare return statistics between segments
5. Calculate Sharpe ratios for each period

### Trading Signal Logic

**TOM Period Definition:**
```
is_TOM = (day > days_in_month - 3) OR (day ≤ 3)
```

**Return Comparison:**
```
Excess_Return = Mean_Return_TOM - Mean_Return_Mid-Month
t-test: H₀: μ_TOM = μ_Mid
```

### Performance Metrics

- **Excess Return**: TOM average return - mid-month average return
- **Sharpe Ratio**: (Mean Return) / (Std Dev) for each period
- **Count**: Number of observations in each category
- **Statistical Significance**: t-test p-value

### Trading Signals

- **BUY Signal**: When TOM effect significant and excess_return > 0
- **Signal Generation**: One signal per TOM day in observation period
- **Confidence**: min(0.8, 1.0 - p_value)
- **Strategy**: Buy on last 3 days of month, hold through first 3 days of next month

### Empirical Performance

- Average excess return: +0.3% to +0.7% per day during TOM period
- Effect consistent across developed markets
- Stronger effect in emerging markets
- Works across different asset classes (equities, commodities)

### Recommended Parameters

- Days before month end: 3-5 days
- Days after month start: 3-5 days
- Holding period: 6+ trading days for TOM effect realization
- Minimum data: 24+ months for reliability

---

## 4. Holiday Effect Analysis

### Strategy Overview

The Holiday Effect describes systematic return patterns around market holidays and vacation periods. These include the pre-holiday drift (positive returns) and holiday-specific seasonality.

### Theoretical Basis

- **Pre-Holiday Drift**: Positive returns before holiday closures (risk-free overnight position)
- **Reduced Risk**: Lower trading volume during holidays reduces volatility
- **Information Asymmetry**: News over holiday period affects Monday open
- **Technical Factors**: Short-term traders exit before holidays

### How It Works

1. Define market holidays (US market: New Year's, Independence Day, Thanksgiving, Christmas)
2. Identify periods near holidays (±N days window, default N=1)
3. Calculate returns for holiday-adjacent and normal trading days
4. Compare return distributions using statistical tests
5. Identify specific holiday effects

### Holidays Tracked

| Holiday | Impact | Typical Date |
|---------|--------|--------------|
| New Year's Day | Strong | Jan 1 |
| Independence Day | Moderate | Jul 4 |
| Thanksgiving | Moderate | 4th Thu in Nov |
| Christmas | Strong | Dec 25 |

### Statistical Testing

**Two-Sample t-test:**
```
H₀: μ_Holiday = μ_Normal
Groups: Returns within days_window of holidays vs. normal days
```

**Effect Size Calculation:**
```
Effect = Mean_Return_Holiday - Mean_Return_Normal
Larger positive effect = pre-holiday drift
```

### Trading Signal Logic

- **BUY Signal**: When holiday effect significant and effect_size > 0
- **Signal Timing**: Start of holiday-adjacent period
- **Confidence**: min(0.75, 1.0 - p_value)
- **Strategy**: Long positions before holidays, close at market close

### Empirical Characteristics

- Pre-holiday returns: +0.2% to +0.5% positive excess
- Effect timing: 1-3 days before holiday
- Post-holiday: Mixed results (depends on holiday)
- Volume: Significantly reduced during holidays

### Practical Considerations

- Different market holidays across exchanges
- Effect varies by country (US, UK, Japan, etc.)
- Weekday positioning affects holiday proximity effects
- Mandatory market closures vs. half-day sessions differ

---

## 5. Seasonality Decomposition

### Strategy Overview

Seasonality decomposition partitions a price/return series into three components: trend, seasonal pattern, and residual noise. This allows quantification of seasonal strength and identification of seasonal patterns that may be tradeable.

### Theoretical Basis

- **Economic Seasonality**: Fiscal year-end effects, quarterly earnings cycles
- **Weather Seasonality**: Energy prices, agricultural commodities, retail sales
- **Behavioral Seasonality**: Vacation periods, annual bonuses, tax planning
- **Technical Seasonality**: Option expiration, rebalancing calendars

### Mathematical Approach

**Additive Model:**
```
Y(t) = Trend(t) + Seasonal(t) + Residual(t)
```

Where:
- **Y(t)**: Original log-return series
- **Trend(t)**: Long-term movement (centered moving average)
- **Seasonal(t)**: Repeating pattern (daily/monthly/yearly)
- **Residual(t)**: Unexplained variance

### How It Works

1. Convert prices to log-returns for stationarity
2. Estimate trend using centered moving average (window = 252 days)
3. Detrend series: Detrended = Returns - Trend
4. Extract seasonality: Average by day-of-year/month
5. Calculate residuals: Residual = Detrended - Seasonal
6. Test seasonality significance using Kruskal-Wallis test

### Kruskal-Wallis Test

Non-parametric test for seasonal differences across months:
```
H₀: Distribution of returns same for all months
H₁: At least one month differs

H-statistic = Σ(rank_group_i²/n_i) - 3(n+1)
p-value = P(H > observed_H | H₀)
```

### Monthly Seasonality Analysis

For each calendar month:
- **Mean Return**: Average daily or monthly return
- **Standard Deviation**: Return volatility
- **Count**: Number of observations
- **Seasonal Index**: Seasonal component / average seasonal magnitude

### Output Metrics

| Metric | Definition |
|--------|-----------|
| Trend Direction | 'up' or 'down' based on trend endpoints |
| Seasonal Amplitude | Standard deviation of seasonal component |
| Kruskal-Wallis H | Test statistic for seasonality |
| p-value | Significance of seasonal pattern |
| Monthly Indices | Seasonal pattern by month |

### Trading Applications

1. **Mean Reversion**: Trade against extreme seasonal values
2. **Momentum**: Trade with strong seasonal trends
3. **Timing**: Position sizing based on seasonal volatility
4. **Hedging**: Reduce positions before high-seasonality periods

### Empirical Patterns by Asset Class

**Equities:**
- January/April/September seasonality
- Q4 strength ("Santa Claus rally")
- Summer weakness ("Sell in May and go away")

**Commodities:**
- Energy: Winter heating demand spike
- Agricultural: Harvest seasonality
- Metals: Jewelry demand seasonality

**Bonds:**
- Q4 refinancing demand
- Month-end volatility patterns
- Coupon payment date effects

### Recommended Parameters

- **Seasonal Period**: 252 trading days (1 year) for daily data
- **Trend Window**: 252 days centered moving average
- **Minimum Data**: 3-5 years for reliable seasonal patterns
- **Significance Level**: α = 0.05

---

## Statistical Testing Framework

### Parametric vs Non-parametric Tests

| Test | Type | Use Case | Assumptions |
|------|------|----------|-------------|
| t-test | Parametric | Compare 2 group means | Normality, equal variance |
| ANOVA | Parametric | Compare 3+ group means | Normality, homogeneity |
| Mann-Whitney U | Non-parametric | Compare 2 groups | None, rank-based |
| Kruskal-Wallis | Non-parametric | Compare 3+ groups | None, rank-based |

### Significance Thresholds

- **α = 0.05**: Standard threshold (5% Type I error)
- **α = 0.01**: Stricter for high-confidence signals
- **p-value < α**: Reject null hypothesis, effect significant
- **Bonferroni Correction**: When testing multiple effects simultaneously

### Effect Size Interpretation

- **Cohen's d**: Standardized mean difference
  - Small: d = 0.2
  - Medium: d = 0.5
  - Large: d = 0.8

- **Excess Return**: Absolute return difference
  - Small: 0.1% - 0.3% per period
  - Medium: 0.3% - 1.0% per period
  - Large: > 1.0% per period

---

## Integration Example

```python
from calendar_effects import CalendarEffectsAnalyzer
import pandas as pd
import numpy as np

# Load price data
prices = pd.Series(...)  # Daily closing prices
dates = pd.DatetimeIndex(...)  # Corresponding dates

# Create analyzer and run comprehensive analysis
analyzer = CalendarEffectsAnalyzer()
results = analyzer.analyze_all(prices, dates)

# Extract specific effects
dow_results = results['day_of_week']
january_results = results['january_effect']
tom_results = results['turn_of_month']
holiday_results = results['holiday_effect']
seasonal_results = results['seasonality']

# Get trading signals
signals = results['signals']
summary = analyzer.get_summary()

# Generate report
print(f"Detected {summary['total_signals']} calendar-based signals")
print(f"Buy signals: {summary['buy_signals']}, Sell signals: {summary['sell_signals']}")
print(f"Effects: {summary['effects_detected']}")
```

---

## Risk Warnings

### Model Limitations

1. **Historical Bias**: Past patterns may not persist
2. **Market Evolution**: Effects diminish as traders exploit them
3. **Data Snooping**: Multiple testing increases false positive risk
4. **Overfitting**: Optimizing parameters on historical data reduces out-of-sample performance
5. **Survivor Bias**: Historical data may not represent all conditions

### Implementation Risks

1. **Execution Risk**: Signals may not execute at expected prices
2. **Slippage**: Market impact on signal execution
3. **Transaction Costs**: Fees may exceed expected returns
4. **Correlated Effects**: Calendar effects may coincide with other market events
5. **Crowded Trades**: If widely known, effect may reverse

### Mitigation Strategies

- Combine multiple calendar effects for robustness
- Use position sizing based on signal confidence
- Implement stop-loss orders
- Monitor out-of-sample performance
- Adjust parameters quarterly based on recent data
- Consider regime-dependent parameters (bull/bear markets)

---

## References

### Key Academic Papers

1. Gibbons, M. R., & Hess, P. (1981). Day of the Week Effects and Asset Returns
2. Rozeff, M. S., & Kinney, W. R. (1976). Capital Market Seasonality
3. Ariel, R. A. (1987). A Monthly Effect in Stock Returns
4. Henkel, S. H., Martin, J. S., & Nardari, F. (2011). Time-Varying Short-Horizon Predictability
5. Schwert, G. W. (2003). Anomalies and Market Efficiency

### Implementation Notes

- All calculations use daily/monthly data
- Default parameters based on 50+ years of research
- Statistical tests validated on multiple markets
- Code handles missing data and holidays gracefully
- Modular design allows independent component use

---

## Updates and Maintenance

- **Review Frequency**: Quarterly parameter review
- **Rebalancing**: Update sensitivity thresholds semi-annually
- **Data Quality**: Validate data for splits, dividends, gaps
- **Model Validation**: Backtest on rolling windows (2+ years)
- **Forward Testing**: Paper trade for 3-6 months before deployment

