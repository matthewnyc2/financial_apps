# Event-Driven Trading Strategies

## Overview

Event-driven trading strategies profit from significant price movements caused by corporate events and market catalysts. Rather than relying on technical patterns or market momentum, event-driven traders analyze the impact of announcements and developments on security prices.

This document outlines five key event-driven strategies implemented in the system:

1. **Earnings Momentum Strategy** - Exploits price movements on earnings announcements
2. **Post-Earnings Announcement Drift (PEAD)** - Captures delayed market reactions to earnings
3. **Dividend Capture Strategy** - Profits from dividend-driven price gaps
4. **M&A Arbitrage Calculator** - Risk arbitrage on acquisition announcements
5. **Event Study Analysis** - Statistical analysis of price behavior around events

---

## 1. Earnings Momentum Strategy

### Strategy Overview

The earnings momentum strategy exploits the significant price movements that occur when companies announce earnings that surprise the market. Research shows that earnings surprises drive some of the largest single-day moves in equities.

### How It Works

**Key Insight**: Markets react strongly to earnings surprises, especially when actual results deviate significantly from consensus expectations.

Trading Rules:
- **BUY Signal**: Positive EPS surprise (Actual > Expected) + Volume surge (>1.5x average) + Price gaps up
- **SELL Signal**: Negative EPS surprise (Actual < Expected) + Volume surge + Price gaps down
- **HOLD**: Insufficient surprise magnitude or volume confirmation

### Trading Mechanics

```
Surprise Magnitude = (Actual EPS - Expected EPS) / |Expected EPS|
Normalized Surprise = tanh(Surprise Magnitude)  // Range: [-1, 1]

Signal Strength = Normalized Surprise × Volume Surge Factor

Where:
- Volume Surge Factor = Current Volume / Average Pre-Event Volume
- Buy/Sell threshold: |Normalized Surprise| > 0.1 AND Volume Surge > 1.5
```

### Entry and Exit Rules

**Entry Conditions** (typically earnings announcement day or day after):
1. Positive (negative) surprise magnitude > 10%
2. Trading volume > 1.5x 20-day average
3. Price gap in direction of surprise
4. Strength score > 0.6 indicates high confidence

**Exit Conditions**:
1. Take profit: +1% to +3% gain (depending on surprise size)
2. Stop loss: -1% to -2% loss (risk management)
3. Time-based: Close position within 2-5 trading days

### Statistical Tests

**T-Test for Surprise Significance**:
```
Null Hypothesis: Surprise = 0 (no actual surprise)
t-statistic = (Actual EPS - Expected EPS) / Standard Error
p-value = 2-tailed probability

Interpretation:
- p < 0.05: Statistically significant surprise
- p < 0.01: Highly significant surprise
```

### Advantages

- Clear, objective entry triggers (announcement-based)
- Large move magnitude (average 2-5% on significant surprises)
- Reduced information asymmetry after public announcement
- High volume supports easy execution
- Works across market cycles (bull and bear markets)

### Disadvantages

- Binary event risk (unknown market reaction magnitude)
- Gap risk (price jumps over stop losses)
- Requires accurate earnings forecasts
- Competition from institutional players
- Difficult to scale to portfolios

### Recommended Parameters

- **Expected Return**: 1-3% per event
- **Win Rate**: 50-60% typical
- **Risk-Reward Ratio**: 1:2 to 1:3 (acceptable)
- **Position Sizing**: 1-2% risk per trade
- **Best for**: Intraday to 5-day holding periods

---

## 2. Post-Earnings Announcement Drift (PEAD)

### Strategy Overview

Post-Earnings Announcement Drift (PEAD) is one of the most well-documented market anomalies. Research shows that stock prices continue to drift in the direction of earnings surprises for weeks (even months) after the announcement, suggesting the market underreacts to earnings news.

### The PEAD Phenomenon

**Key Finding**: The market's reaction to earnings surprises is incomplete at the announcement. Price continues moving in the surprise direction for 20-60 days post-announcement.

Research Evidence:
- Ball and Brown (1968): First documented PEAD
- Foster, Olsen, Shevlin (1984): PEAD persists for months
- Bartov, Radhakrishnan, Krinsky (2000): Stronger for larger surprises
- Bernard and Thomas (1989): Stronger for small-cap stocks

### Trading Mechanics

```
Daily Drift = Cumulative Price Return / Days Since Event
Drift Strength = Daily Drift × Surprise Magnitude × Size Factor

Drift Prediction Model:
Expected Return = Surprise × Beta × (1 - decay_factor^days)

Where:
- Beta ≈ 0.05 (sensitivity to surprise)
- decay_factor ≈ 0.98 (daily decay rate)
- Days = Number of days since announcement
```

### Position Strategy

**Entry**:
1. Identify significant earnings surprise
2. Wait 1-3 days for initial market reaction to settle
3. Enter long (positive surprise) or short (negative surprise) position
4. Target holding period: 20-60 days

**Exit**:
1. Time-based: 60 days after announcement
2. Price-based: Stop loss at 2% against position
3. Take profit: When drift model predicts reversal

### Drift Decay

```
Price Impact Timeline:
Day 0:   Announcement (25-35% of total drift)
Day 1-5: Rapid drift (35-45% of total drift)
Day 5-20: Moderate drift (15-25% of total drift)
Day 20+: Diminishing drift (<5% remaining)

Cumulative Abnormal Return (CAR):
CAR(20) = ~3-5% for large surprises
CAR(60) = ~4-6% for large surprises
```

### Statistical Significance Testing

**Regression Model**:
```
Abnormal Return(t) = Alpha + Beta × Surprise × (1 - decay^t) + Error(t)

R² (goodness of fit):
- R² > 0.30: Model explains significant drift behavior
- R² > 0.50: Strong drift pattern
- Significant at p < 0.05: Drift is statistically significant
```

### Advantages

- Well-documented market anomaly with strong research support
- Longer holding period (20-60 days) reduces execution costs
- Strength based on surprise magnitude (larger surprises = stronger drift)
- Works with simple implementation
- Profitable across different time periods
- Lower execution risk than earnings-day trading

### Disadvantages

- Slower to capitalize (20-60 day drift period)
- Competition from market makers has eroded some profits
- Requires holding through market volatility
- Sensitive to large market shocks
- Assumes continued drift (reversal risk)

### Recommended Parameters

- **Expected Return**: 1-2% total over 60 days
- **Annualized Return**: 6-12% if successfully repeated
- **Win Rate**: 55-65% typical
- **Position Size**: 2-3% risk per trade
- **Best for**: Portfolio-based strategies (multiple events)

---

## 3. Dividend Capture Strategy

### Strategy Overview

The dividend capture strategy exploits the mechanical price drop that occurs on the ex-dividend date. Since dividend is no longer owed to new owners, the stock price drops by approximately the dividend amount on the ex-date.

### Key Dates and Mechanics

**Important Dates**:
1. **Announcement Date**: Company announces dividend (stock price usually rises)
2. **Ex-Dividend Date**: Last day to own stock to receive dividend
   - Price drops by ~dividend amount (mechanical adjustment)
   - This is the CRITICAL date for the strategy
3. **Record Date**: Date used to determine dividend recipients
4. **Payment Date**: When dividend is actually paid to shareholders

### Price Mechanics

```
Pre-Ex Dividend:  Stock = Company Value + Present Value of Dividend
Ex-Dividend:      Stock = Company Value (dividend removed)

Expected Price Drop = Dividend Amount (before taxes)

Actual calculation:
Expected Drop = Dividend / (1 + required_return/365)
               ≈ Dividend (for typical returns)

Tax-Adjusted Drop = Dividend × (1 - capital_gains_rate) / (1 - dividend_tax_rate)
                  = Dividend × adjustment_factor
```

### Strategy Implementation

**Trading Rules**:
1. **Entry**: Buy stock 1-2 days before ex-dividend date
2. **Hold**: Through ex-dividend date until ex-date + 5 days (holding period)
3. **Exit**: Sell stock after ex-date when price recovers
4. **Profit**: Dividend received - Transaction costs - Price gap loss

**Profitability Condition**:
```
Net Profit = Dividend × (1 - dividend_tax_rate) - Transaction Costs
            - Holding Costs - Slippage

Profitable if:
Dividend × (1 - tax_rate) > 2 × Transaction Cost + Holding Cost + Slippage

Typical assumptions:
- Transaction Cost: 10 basis points (buy + sell)
- Dividend Tax Rate: 15% (long-term capital gains, varies by jurisdiction)
- Holding Period: 5 days
- Slippage: 5-10 basis points
```

### Statistical Analysis

**Chi-Square Test on Price Drop**:
```
Null Hypothesis: Actual Price Drop = Expected Price Drop (dividend amount)

Chi² = (Actual Drop - Expected Drop)² / Expected Drop

Result interpretation:
- p > 0.05: Price drop consistent with dividend amount (no arbitrage)
- p < 0.05: Significant deviation from expected drop (potential profit)
- Positive deviation: Stock didn't drop enough (buy signal)
- Negative deviation: Stock dropped too much (sell opportunity)
```

### Risk Factors

1. **Dividend Reinvestment Risk**: When yield is high, dividend reinvesting at lower prices
2. **Ex-Date Price Risk**: Stock may not recover gap within holding period
3. **Market Volatility**: Large market moves can overcome small dividend profit
4. **Tax Considerations**: Qualified vs. non-qualified dividends affect after-tax return
5. **Stock Splits/Special Dividends**: Complicate analysis

### Advantages

- Objective, mechanical event (ex-dividend date is known in advance)
- Limited downside (stock rarely falls >5% on ex-date)
- Can be held for short period (5-20 days)
- Works best with high-dividend stocks (2-5%+ yields)
- Tax-efficient in some jurisdictions (qualified dividends)

### Disadvantages

- Very small profit margin per trade (<1%)
- Requires scale/portfolio approach to be profitable
- Transaction costs eat into profits (especially small positions)
- Stock may gap down more than dividend amount
- Tax treatment varies by jurisdiction (less effective in high-tax environments)

### Recommended Parameters

- **Minimum Dividend Yield**: 1.5% annual
- **Minimum Holding Period**: 60+ days (for long-term capital gains)
- **Expected Net Return**: 0.3-0.8% per event
- **Best for**: High-dividend sectors (utilities, REITs, preferred stocks)
- **Frequency**: Multiple events per month across diverse holdings

---

## 4. M&A Arbitrage Calculator

### Strategy Overview

Merger and acquisition (M&A) arbitrage, also called risk arbitrage, involves buying the target company's stock at a discount after a takeover is announced. The discount reflects the probability that the deal will not close.

### Deal Mechanics

**Typical M&A Timeline**:
1. **Announcement**: Acquirer announces offer price for target stock
2. **Market Reaction**: Target stock trades at discount (deal risk premium)
3. **Regulatory Review**: Government reviews deal for antitrust concerns (~30-60 days)
4. **Shareholder Vote**: Target shareholders must approve deal
5. **Closing**: Deal closes when all conditions met (typically 60-180 days from announcement)

### The Arbitrage Opportunity

```
Pre-Announcement:  Stock trades at intrinsic value P0
Post-Announcement: Deal offered at price P_deal > P0

Market Price:      P_market = P0 < P_deal (reflects deal risk)

Spread:            P_deal - P_market (arbitrageur's profit if deal closes)

Market's Implied Probability:
Probability = P_market / P_deal

Arbitrageur's Profit (if deal closes) = (P_deal - P_market) / P_market
```

### Risk Factors and Deal Failure Scenarios

**1. Regulatory Risk** (most common):
- Antitrust concerns
- Foreign investment restrictions
- Industry-specific regulations
- Historical failure rate: 5-15% depending on concentration

**2. Financing Risk** (esp. all-cash deals):
- Buyer's bank financing falls through
- Market conditions deteriorate (rising rates)
- Buyer's financial position weakens
- Typical for LBO deals

**3. Shareholder Vote Risk**:
- Activist opposition
- Competing bid emerges
- Minority shareholder groups block deal
- Less common (80%+ approval typical)

**4. Market Risk**:
- General market declines
- Sector rotation
- Buyer stock underperforms (stock deals)

### Return Calculations

**Expected Return Formula**:
```
Expected Return = (P_deal × P(complete) +
                  P_alternative × P(fail) - P_market) / P_market

Where:
- P(complete) = Probability deal closes
- P(fail) = 1 - P(complete)
- P_alternative = Stock price if deal fails (usually ≈ pre-announcement price)

Annualized Return = Expected Return × 365 / Days to Closing

Risk-Adjusted Return:
Excess Return = Annualized Return - Risk-Free Rate

Risk-Reward Ratio = Excess Return / Maximum Downside Risk
```

### Statistical Analysis

**Chi-Square Test on Market Probability**:
```
Null Hypothesis: Market price correctly reflects deal probability

Expected Price = P_deal × (P_market / P_deal) = P_market (tautological, so we test deviation)

Chi² = (P_market - Expected)² / Expected

Interpretation:
- Large Chi² (p < 0.05): Market misprice deal probability
- Arbitrageur's edge if implied probability significantly differs from actual probability
```

### Deal Evaluation Criteria

**Attractive Deals Typically Show**:
1. **Excess Return > 10% annualized**: Compensation for deal risk
2. **Risk-Reward Ratio > 1.5**: Profit potential exceeds downside
3. **Days to Closing > 30**: Sufficient time to earn return
4. **Regulatory approval likelihood > 75%**: Low regulatory risk
5. **Financing secured**: For all-cash deals

**Risky Deals Avoid**:
1. Excess return < 5% (insufficient compensation)
2. Significant regulatory concerns
3. Hostile takeover with competitive bidding
4. Equity financing (dependent on buyer's stock performance)
5. <30 days to closing (insufficient time)

### Advantages

- Profitable on completed deals (spread = profit)
- Limited upside (capped at deal spread)
- Profitable in all market conditions (market-neutral)
- Research-driven (information advantage possible)
- Lower correlation with general market moves

### Disadvantages

- Requires deal completion (execution risk)
- Limited upside (capped return)
- Concentration risk (correlated failures in M&A environment)
- Regulatory/legal complexities
- Deal spread declines over time (declining return as closing date approaches)

### Recommended Parameters

- **Minimum Spread**: 1% (covers transaction costs)
- **Minimum Excess Return**: 10% annualized
- **Minimum Regulatory Probability**: 70%
- **Maximum Position Size**: 2-3% of portfolio (deal risk concentration)
- **Typical Holding Period**: 30-180 days

---

## 5. Event Study Analysis

### Methodology Overview

Event study analysis is a rigorous statistical framework for measuring the impact of events on security prices. It quantifies the "abnormal return" - the portion of return not explained by normal market movements.

### Core Concepts

**Normal Return (Expected Return)**:
The return a security would be expected to earn in the absence of the event, calculated using a market model:

```
Expected Return(t) = Alpha + Beta × Market Return(t)

Where:
- Alpha: Security-specific return (intercept)
- Beta: Market sensitivity (systematic risk)
- Market Return: Overall market return (benchmark)
```

**Abnormal Return**:
```
Abnormal Return(t) = Actual Return(t) - Expected Return(t)
```

**Cumulative Abnormal Return (CAR)**:
```
CAR(t) = Sum of Abnormal Returns from event to day t
CAR₀₊₂₀ = Sum of abnormal returns for 20 days post-event
```

### Market Model Estimation

**Two-Phase Approach**:

**Phase 1: Estimation Window** (120 days before event)
- Calculate market model parameters (Alpha, Beta)
- Establish baseline expected returns
- Measure volatility (estimation error standard deviation)

**Phase 2: Event Window** (5 days before through 20 days after event)
- Compare actual returns to expected returns
- Calculate abnormal returns
- Aggregate into cumulative abnormal returns

### Statistical Significance Testing

**T-Test on Average Abnormal Return**:
```
Null Hypothesis: Average Abnormal Return = 0 (event has no impact)

t-statistic = Mean(AR) / SE(AR)

Where:
SE(AR) = Std Dev(AR) / sqrt(N)
N = Number of days in event window

Interpretation:
- |t| > 1.96: Significant at 5% level (p < 0.05)
- |t| > 2.58: Significant at 1% level (p < 0.01)
- p-value: Exact probability of result under null hypothesis
```

**Cross-Sectional Test**:
For multiple events, test if average CAR differs from zero:
```
t-statistic = Mean(CAR) / SE(CAR)

SE(CAR) = sqrt(Sum(AR_std²) / N) where N = number of events

More robust than single-event test
```

### GARCH Volatility Model

**Standard GARCH(1,1) Specification**:
```
sigma²(t) = omega + alpha × epsilon²(t-1) + beta × sigma²(t-1)

Where:
- omega: Base volatility level
- alpha: Weight on recent squared errors (short-term shock)
- beta: Weight on previous volatility (persistence)
- epsilon(t): Residual return from market model

Interpretation:
- High alpha: Market reacts quickly to news
- High beta: Volatility persists (clustering)
- alpha + beta: Persistence measure (close to 1 = high persistence)

Volatility Forecast:
sigma²(t+1) = omega + alpha × epsilon²(t) + beta × sigma²(t)
```

### Event Window Selection

**Standard Windows**:
- **Short-term**: [-2, +2] (5 days total)
- **Medium-term**: [-5, +20] (26 days total)
- **Long-term**: [-60, +120] (181 days total, for PEAD analysis)

**Window Justification**:
- **Before event**: Capture pre-event anticipation
- **After event**: Capture full market reaction
- **Longer windows**: Measure persistence of effects
- **Shorter windows**: Isolate direct event impact

### Result Interpretation

**Common Event Study Findings**:

1. **Positive Abnormal Returns**:
   - CAR > 0 and p < 0.05: Good news, market reacts positively
   - Magnitude: -1% to +10% typical for major events

2. **Negative Abnormal Returns**:
   - CAR < 0 and p < 0.05: Bad news, market reacts negatively
   - Magnitude: -10% to +1% typical for major events

3. **No Significant Effect**:
   - p > 0.05: Event not significant (already known, priced in)
   - CAR ≈ 0: Market-neutral impact

### Advantages

- Rigorous statistical framework (peer-reviewed methodology)
- Quantifies event impact with confidence intervals
- Controls for market movements (market-adjusted)
- Can analyze single events or aggregate across many events
- Works across asset classes and geographies
- Establishes baseline for other event-driven strategies

### Disadvantages

- Requires clean historical data (non-event period)
- Sensitive to estimation window selection
- Assumes normal distribution (violated in fat-tailed markets)
- Backward-looking (uses historical beta, actual may differ)
- Other events may contaminate event window

---

## Implementation Guide

### Data Requirements

```python
# Minimum data for event analysis:
1. Daily prices (or returns) for stock and market index
2. Trading volumes (for earnings/dividend strategies)
3. Event metadata:
   - Event date (index position)
   - Event type (earnings, dividend, M&A, etc.)
   - Event details (EPS, dividend amount, deal price, etc.)

# Recommended data frequency: Daily
# Minimum history: 200 days (for robust market model)
# Ideal history: 3-5 years (captures different market regimes)
```

### Code Usage Example

```python
from event_driven import (
    EarningsMomentumStrategy,
    PostEarningsAnnouncementDrift,
    DividendCaptureStrategy,
    MandAArbitrageCalculator,
    EventStudyAnalysis
)

# 1. Analyze earnings announcement
earnings = EarningsMomentumStrategy()
signal = earnings.analyze_event(
    prices=stock_prices,
    volumes=trading_volumes,
    actual_eps=2.50,
    expected_eps=2.20,
    event_idx=100
)
print(f"Signal: {signal.signal_type}, Confidence: {signal.strength:.1%}")

# 2. Analyze PEAD
pead = PostEarningsAnnouncementDrift()
signal = pead.analyze_pead_signal(
    surprise=0.15,  # 15% surprise
    price=100.0,
    subsequent_prices=prices[101:161],
    event_idx=100
)

# 3. Analyze dividend capture
dividend = DividendCaptureStrategy()
metrics = dividend.calculate_profit_potential(
    price_before_ex=100.0,
    dividend_amount=2.50,
    price_after_ex=97.30
)
print(f"Net Profit: ${metrics['after_tax_profit']:.2f}, Profitable: {metrics['profitable']}")

# 4. M&A arbitrage
mna = MandAArbitrageCalculator()
metrics = mna.calculate_deal_metrics(
    current_price=95.00,
    deal_price=110.00,
    days_to_closing=90,
    probability_completion=0.80
)
print(f"Excess Return: {metrics['excess_return_pct']:.2f}%")

# 5. Event study
study = EventStudyAnalysis()
results = study.calculate_abnormal_returns(
    stock_returns=returns,
    market_returns=market_returns,
    event_idx=250
)
print(f"CAR: {results['average_car']:.4f}, p-value: {results['p_value']:.4f}")
```

---

## Risk Management

### Position Sizing

```
Position Size = Account Risk / Trade Risk

Typical risk limits:
- Single event: 1-2% account risk
- Portfolio of similar events: 3-5% total risk
- M&A arb concentration: 2-3% per deal
- Reduce on losing streaks (reduce volatility)
```

### Stop Loss Rules

- **Earnings/PEAD**: 1-2% below entry
- **Dividend capture**: 2-3% below entry
- **M&A arb**: 5-10% below entry (deal risk)
- **Time-based**: Close at end of specified holding period

### Hedging Strategies

- **Earnings trades**: Buy puts or use collars to limit downside
- **Dividend capture**: Short puts to generate income
- **M&A arb**: Delta-neutral hedging using acquirer short
- **PEAD**: Reduce position size over drift period

---

## Performance Metrics

### Key Metrics to Track

1. **Win Rate**: Percentage of profitable trades
2. **Profit Factor**: Total wins / Total losses
3. **Sharpe Ratio**: Return per unit of risk
4. **Maximum Drawdown**: Largest peak-to-trough decline
5. **Calmar Ratio**: Return / Maximum Drawdown
6. **Statistical Significance**: P-values, t-statistics

### Benchmarks

```
Target Performance by Strategy:
- Earnings Momentum: 10-15% annual, 50-60% win rate
- PEAD: 10-20% annual, 55-65% win rate
- Dividend Capture: 5-10% annual, 70-80% win rate
- M&A Arb: 8-12% annual, 60-70% win rate
- Event Study: Varies (measure-only)

Combined Portfolio: 12-18% annual with lower drawdown
```

---

## Conclusion

Event-driven strategies offer unique opportunities to profit from corporate events and market catalysts. By combining fundamental analysis with rigorous statistical testing, traders can identify high-probability opportunities and manage risk effectively. Success requires:

1. **Data Quality**: Accurate event data and price history
2. **Statistical Rigor**: Proper hypothesis testing and significance
3. **Risk Management**: Disciplined position sizing and stop losses
4. **Diversification**: Multiple event types and securities
5. **Adaptability**: Adjust strategies as markets evolve

The five strategies presented here form a comprehensive toolkit for event-driven trading. Each has distinct risk-reward characteristics and works best in different market conditions. Combining multiple approaches with disciplined execution can produce consistent, superior risk-adjusted returns.
