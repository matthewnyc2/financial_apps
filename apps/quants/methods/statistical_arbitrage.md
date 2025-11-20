# Statistical Arbitrage Methods for Quantitative Trading

## Overview

Statistical arbitrage (stat arb) exploits temporary mispricings in financial markets by identifying statistical relationships between securities. Unlike pure arbitrage (risk-free), statistical arbitrage has some level of risk but offers consistent profitability over time.

This document outlines five major statistical arbitrage strategies with complete mathematical foundations, implementation details, and usage guidelines.

---

## Table of Contents

1. [Pairs Trading with Cointegration](#pairs-trading)
2. [Basket Arbitrage](#basket-arbitrage)
3. [Index Arbitrage](#index-arbitrage)
4. [Statistical Mean Reversion](#mean-reversion)
5. [Distance-Based Relative Value Trading](#distance-relative-value)
6. [Implementation Guide](#implementation)
7. [Risk Management](#risk-management)

---

## 1. Pairs Trading with Cointegration {#pairs-trading}

### Theory

Pairs trading identifies two securities with a long-run equilibrium relationship (cointegration). When the relationship temporarily breaks down, we take offsetting positions expecting mean reversion.

**Key Assumption**: If two assets are cointegrated, their spread is stationary and mean-reverting.

### Mathematical Foundation

#### Cointegration Concept

Two time series X_t and Y_t are cointegrated of order (1,1) if:
- Both X_t and Y_t are I(1) (integrated of order 1, have unit roots)
- There exists a linear combination Z_t = Y_t - β*X_t that is I(0) (stationary)

#### The Spread Equation

```
Z_t = log(P₁,ₜ) - β * log(P₂,ₜ)
```

Where:
- P₁,ₜ, P₂,ₜ = Prices of two assets at time t
- β = Hedge ratio determined by OLS regression
- Z_t = Spread (should be stationary)

#### Beta (Hedge Ratio) Estimation

Using Ordinary Least Squares regression:

```
log(P₁,ₜ) = α + β * log(P₂,ₜ) + εₜ

β = Cov(P₁,ₜ, P₂,ₜ) / Var(P₂,ₜ)

β̂ = (Xᵀ X)⁻¹ Xᵀ y
```

Where:
- X = [1, log(P₂)]ᵀ (design matrix with intercept)
- y = log(P₁) (dependent variable)

#### Z-Score Calculation

```
Z-score = (Z_t - μ_Z) / σ_Z
```

Where:
- μ_Z = Mean of spread (typically 0 for stationary series)
- σ_Z = Standard deviation of spread

### Stationarity Testing

**Augmented Dickey-Fuller (ADF) Test**

H₀: Series has unit root (non-stationary)
H₁: Series is stationary

Test Statistic:
```
τ = (β̂ - 1) / SE(β̂)
```

Decision Rule:
- If p-value < 0.05: Reject H₀ → Series is stationary
- If p-value > 0.05: Fail to reject → Series may be non-stationary

### Trading Signals

```
Entry Condition:
- Long spread if Z-score < -2.0 (revert upward)
- Short spread if Z-score > +2.0 (revert downward)

Exit Condition:
- Close position when |Z-score| < 0.5

Practical Interpretation:
- Long Spread = Long Asset 1 + Short Asset 2
- Short Spread = Short Asset 1 + Long Asset 2
```

### Expected Payoff

When spread deviates from equilibrium:

```
Expected Return = (μ_Z - Z_t) * Position_Size
Risk = σ_Z * √(time_to_reversion)
Sharpe Ratio = Expected_Return / Risk
```

### Implementation Steps

1. **Data Selection**: Choose potentially cointegrated pairs
   - Similar sectors
   - High correlation (> 0.7)
   - Similar market caps

2. **Estimation Window**: Use 252 days (1 year) of historical data

3. **Test for Cointegration**:
   - Run ADF test on spread
   - Verify p-value < 0.05

4. **Monitor Spread**:
   - Track Z-score continuously
   - Update mean and std dev daily

5. **Trade Management**:
   - Scale position size by spread deviation
   - Use stop losses at 3σ
   - Take profits at equilibrium

---

## 2. Basket Arbitrage {#basket-arbitrage}

### Theory

Basket arbitrage exploits mispricings between an index and its constituent securities. When the index trades at a discount to its basket of components, we execute a cash-and-carry arbitrage.

### Mathematical Foundation

#### Synthetic Index Formula

```
V_synthetic = Σᵢ(wᵢ * Sᵢ)
```

Where:
- wᵢ = Weight of security i in the index
- Sᵢ = Spot price of security i
- n = Number of securities in index

#### Mispricing Percentage

```
Mispricing_pct = (Index_Price - Synthetic_Price) / Synthetic_Price × 100%
```

#### Arbitrage Profitability

**Cash-and-Carry** (when Index > Synthetic):
```
Profit = (Index_Price - Synthetic_Price) - Transaction_Costs
Profit_pct = [(Index_Price / Synthetic_Price) - 1] × 100%
```

**Reverse Cash-and-Carry** (when Index < Synthetic):
```
Profit = (Synthetic_Price - Index_Price) - Transaction_Costs
```

#### Transaction Costs

```
Total_Cost = 2 × TC_pct × Price + Clearing_Costs + Bid-Ask_Spread

Typical Values:
- Stock commissions: 0.05% - 0.10%
- Bid-ask spreads: 0.01% - 0.05%
- Clearing/settlement: 0.01% - 0.02%
- Total: 0.20% - 0.25% round-trip
```

### Execution Strategy

#### Long Basket, Short Index (Reverse Cash-and-Carry)

**When**: Index price > Synthetic basket price + transaction costs

```
Action 1 (Morning, Pre-open):
  - Buy each stock in the basket with index weights
  - Short sell the index futures contract

Action 2 (End of day or next day):
  - Close both positions
  - Profit = Arbitrage spread - Transaction costs
```

#### Short Basket, Long Index (Cash-and-Carry)

**When**: Index price < Synthetic basket price - transaction costs

```
Action 1:
  - Short each stock in the basket
  - Buy index futures contract

Action 2:
  - Unwind at convergence
  - Profit from convergence
```

### Key Metrics

**Minimum Profitable Spread**:
```
Min_Spread = 2 × TC_pct + Bid-Ask_Spread_pct
```

**Execution Speed**: Must complete within minutes to avoid slippage

**Scaling Factor**:
```
Position_Size = Capital × Spread_Deviation / Min_Spread
```

---

## 3. Index Arbitrage {#index-arbitrage}

### Theory

Index arbitrage exploits pricing differences between spot indices and their futures contracts. The relationship is governed by the cost-of-carry model.

### Mathematical Foundation

#### Cost-of-Carry Model

The theoretical futures price is:

```
F_t,T = Sₜ × e^((r - q) × T)
```

Where:
- F_t,T = Futures price at time t, maturing at T
- Sₜ = Current spot index price
- r = Risk-free rate (annual)
- q = Dividend yield (annual)
- T = Time to maturity (in years)
- e = Mathematical constant (≈ 2.71828)

#### Continuous vs. Discrete Compounding

**Continuous (above formula)**:
```
F = S × e^((r-q)×T)
```

**Discrete (quarterly dividends)**:
```
F = S × [1 + r×T - q×T]  (approximation for small T)
```

#### Arbitrage Profitability

**Profit Per Unit**:
```
π = |Actual_Futures - Theoretical_Futures| - Transaction_Costs
```

**Percentage Return**:
```
Return% = [|F_actual - F_theoretical| / F_theoretical] × 100%
Time_Adjusted_Return% = Return% × (365 / Days_to_Maturity)
```

#### Net Carry Cost Components

```
Net_Carry_Cost = (r - q) × Sₜ × T

Detailed Breakdown:
1. Financing Cost = r × Sₜ × T
2. Dividend Income = q × Sₜ × T  (negative cost)
3. Net Cost = (r - q) × Sₜ × T

P&L from Carry:
  - Long spot position: Pays dividend (gains q×Sₜ×T)
  - Pays financing cost (loses r×Sₜ×T)
  - Net: Loses (r-q)×Sₜ×T
```

### Trading Scenarios

#### Scenario 1: Futures Over-Priced (F_actual > F_theoretical)

```
Day 0 (Detection):
1. Short index futures (or short basket of stocks)
2. Buy spot index (or buy component basket)
3. Pay financing costs = r × S × T
4. Receive dividends = q × S × T

Day T (Maturity):
1. Close long spot position
2. Settle short futures position
3. Futures contract = Spot price at maturity (by construction)

Profit = F_actual - S₀ - (r - q)×S₀×T - Transaction_Costs
       = [F_actual - S₀×e^((r-q)×T)] - TC
       = Arbitrage_Spread - TC
```

#### Scenario 2: Futures Under-Priced (F_actual < F_theoretical)

```
Day 0:
1. Buy index futures
2. Short spot index
3. Receive financing costs
4. Pay out dividends

Day T:
1. Close short spot position
2. Close long futures position

Profit = S₀×e^((r-q)×T) - F_actual - TC
```

### Implementation Details

**Daily Monitoring**:
```
For each contract maturity:
  actual_price = Current_Futures_Price
  theoretical_price = Spot × exp((r-q) × time_to_maturity)
  spread = abs(actual_price - theoretical_price)

  if spread > TC_threshold:
    Execute Arbitrage
```

**Transaction Costs**:
```
TC = Commission + Bid-Ask_Spread + Slippage + Clearing

Typical Breakdown (in bps):
- Futures commission: 0.5 - 2 bps
- Stock commissions: 5 - 10 bps (for basket)
- Bid-ask spreads: 2 - 5 bps
- Total: 10 - 20 bps round-trip
```

**Position Sizing**:
```
For $10M capital with 2% index bet:
Position_Size = 0.02 × $10M / Spot_Price
Number_of_Contracts = Position_Size / Multiplier

Example: If S&P 500 @ 4500, Multiplier = 250
= $200,000 / 4500 × 250 = ~11 contracts
```

---

## 4. Statistical Mean Reversion {#mean-reversion}

### Theory

Mean reversion exploits the statistical tendency of prices to oscillate around long-term averages. Deviations are temporary, creating trading opportunities.

### Mathematical Foundation

#### Ornstein-Uhlenbeck Process

The continuous-time model for mean-reverting processes:

```
dXₜ = θ(μ - Xₜ)dt + σ dWₜ
```

Where:
- Xₜ = Price at time t
- θ = Mean reversion speed (0 < θ < 1)
- μ = Long-run equilibrium level
- σ = Volatility of shocks
- Wₜ = Wiener process (random shock)

#### Discrete AR(1) Approximation

For practical implementation, approximate with autoregressive model:

```
Xₜ = (1 - θ)×Xₜ₋₁ + θ×μ + εₜ

Where εₜ ~ N(0, σ²)
```

**Estimation via OLS**:
```
Fit: Xₜ = φ₀ + φ₁×Xₜ₋₁ + εₜ

Then:
  θ̂ = 1 - φ̂₁
  μ̂ = φ̂₀ / θ̂
```

#### Half-Life of Mean Reversion

Time for price to revert halfway back to mean:

```
Half-Life = ln(2) / θ = 0.693 / θ

Interpretation:
- If θ = 0.05: Half-life ≈ 13.9 days
- If θ = 0.10: Half-life ≈ 6.9 days
- Higher θ = Faster mean reversion
```

#### Expected Reversion Distance

Conditional expectation from current level:

```
E[Xₜ₊₁ | Xₜ] = (1 - θ)×Xₜ + θ×μ

Expected Move = (1 - θ) × (Xₜ - μ)
```

#### Z-Score Framework

Normalize deviations from mean:

```
Z_score = (Price - MA) / StdDev

Ranges:
- |Z| < 0.5: Near equilibrium
- 0.5 < |Z| < 1.0: Small deviation
- 1.0 < |Z| < 2.0: Moderate deviation
- |Z| > 2.0: Extreme deviation (high probability reversion)
- |Z| > 3.0: Very extreme (check for mean shift)
```

### Trading Strategy

**Entry Logic**:
```
Entry Signal:
  IF Z_score < -2.0:
    GO LONG (price too low, will revert up)
  IF Z_score > +2.0:
    GO SHORT (price too high, will revert down)
```

**Exit Logic**:
```
Exit Conditions:
  1. When |Z_score| < 0.5 (reverted to mean)
  2. On stop loss at |Z_score| > 3.0
  3. Time-based: After holding for 2× half-life
```

**Position Sizing**:
```
Position_Size = Base_Size × (|Z_score| - 1.0)

Rationale:
- Larger deviations = higher expected return
- Need capital to average down if deviation increases
- Limits size if Z-score between 1-2 (less extreme)
```

### Expected Returns

**Drift Component**:
```
Expected Return = (μ - Xₜ) × θ × Δt

With Z-score:
Expected Return = -Z_score × σ × θ × Δt
```

**Sharpe Ratio**:
```
Sharpe = Expected_Return / Volatility

For daily positions:
  Expected Return per day = σ × Z_score × θ / 252
  Volatility = σ / √252
  Sharpe ≈ Z_score × √252 × θ
```

### Key Parameters to Estimate

1. **Moving Average Period**: 20-60 days (shorter = more responsive)
2. **Volatility Period**: Same as MA period
3. **Theta (θ)**: Fit AR(1) model on 252-day window
4. **Half-life**: ln(2) / θ
5. **Entry threshold**: 2.0σ (90% confidence)
6. **Exit threshold**: 0.5σ (high mean reversion confidence)

---

## 5. Distance-Based Relative Value Trading {#distance-relative-value}

### Theory

Distance-based approach identifies when correlations between basket members break down by measuring the Euclidean distance of their normalized price movements.

### Mathematical Foundation

#### Euclidean Distance in Price Space

```
D_t = √(Σᵢ(ΔPᵢ,ₜ)²)
```

Where:
- ΔPᵢ,ₜ = Price change of security i at time t
- Σ = Sum over all securities in basket

#### Normalized Spread Distance

To account for volatility differences:

```
d_i,t = (Pᵢ,ₜ - MA_i,t) / σ_i,t

Total Distance:
D_t = √(Σᵢ(d_i,t)²)
```

Where:
- MA_i,t = Moving average of price i
- σ_i,t = Volatility of price i

#### Statistical Properties

**Historical Average**:
```
D̄ = (1/N) × ΣD_t
SD = √[(1/N) × Σ(D_t - D̄)²]
```

**Z-Score of Distance**:
```
Z_distance = (D_current - D̄) / SD
```

### Correlation Breakdown Detection

**Assumption**:
- Normal correlation = D_t near D̄
- Breakdown event = D_t > D̄ + k×SD (typically k=1.5)

**Signal Generation**:
```
IF Z_distance > 1.5:
  Correlations breakdown
  Expect convergence trade:
    - Buy underperformer (most negative d_i)
    - Sell outperformer (most positive d_i)

IF Z_distance < 0.5:
  Correlations restored
  Exit positions
```

### Implementation

**Monitoring**:
```
Daily Calculation:
1. Update MA and volatility for each security
2. Calculate normalized spreads d_i
3. Calculate total distance D
4. Compare to historical baseline
```

**Rebalancing**:
```
Position Weights = Relative Spread Magnitude

If d_1 = -2σ, d_2 = +1.5σ:
  Long Weight_1 = 2.0 / (2.0 + 1.5) = 57%
  Short Weight_2 = 1.5 / (2.0 + 1.5) = 43%
```

---

## Implementation Guide {#implementation}

### Class Usage Examples

#### 1. Pairs Trading Example

```python
from statistical_arbitrage import PairsTrading
import numpy as np

# Initialize
pt = PairsTrading(lookback_period=252)

# Calculate hedge ratio (from historical data)
beta = pt.calculate_hedge_ratio(price1, price2)

# Calculate spread
spread = pt.calculate_spread(price1, price2)

# Test for cointegration
adf_results = pt.adf_test(spread)
if adf_results['is_stationary']:
    print("Pair is cointegrated!")

# Generate trading signals
signals = pt.generate_signals(
    spread,
    entry_threshold=2.0,    # 2 std devs
    exit_threshold=0.5       # 0.5 std devs
)

# Current position
if signals[-1] == 1:
    print("Long spread: Buy Asset 1, Short Asset 2")
elif signals[-1] == -1:
    print("Short spread: Short Asset 1, Buy Asset 2")
```

#### 2. Basket Arbitrage Example

```python
from statistical_arbitrage import BasketArbitrage
import numpy as np

# Index composition: 30% Stock A, 25% Stock B, etc.
weights = np.array([0.30, 0.25, 0.20, 0.15, 0.10])

# Initialize
ba = BasketArbitrage(weights=weights, transaction_cost_pct=0.005)

# Calculate synthetic index value
synthetic_prices = ba.calculate_synthetic_index(component_prices)

# Check for mispricing
mispricing_pct = ba.calculate_mispricing(index_prices, synthetic_prices)

# Generate arbitrage signals
signals = ba.generate_signals(mispricing_pct, threshold=0.01)

# If signal > 0: Buy basket, short index
# If signal < 0: Short basket, buy index
if signals[-1] == -1:
    print(f"Arbitrage opportunity: {mispricing_pct[-1]*100:.2f}% mispricing")
    print("Action: Short index, buy component basket")
```

#### 3. Index Arbitrage Example

```python
from statistical_arbitrage import IndexArbitrage

# Initialize with market parameters
ia = IndexArbitrage(
    risk_free_rate=0.05,      # 5% annual
    dividend_yield=0.02,       # 2% annual
    transaction_cost_pct=0.003 # 30 bps round-trip
)

# Analyze arbitrage opportunity
spot_price = 4500
futures_price = 4550
time_to_maturity = 91/365  # 91 days

opportunity = ia.identify_arbitrage_opportunity(
    spot_price, futures_price, time_to_maturity
)

print(f"Theoretical: ${opportunity['theoretical_price']:.2f}")
print(f"Actual: ${futures_price:.2f}")
print(f"Profit: ${opportunity['net_profit']:.2f}")

# Is it profitable?
if opportunity['net_profit'] > 0:
    print(f"Execute: {opportunity['strategy']}")
```

#### 4. Mean Reversion Example

```python
from statistical_arbitrage import MeanReversion

# Initialize
mr = MeanReversion(lookback_period=252, half_life_threshold=30)

# Estimate mean reversion parameters
theta, half_life = mr.estimate_mean_reversion_speed(price_series)
print(f"Half-life: {half_life:.1f} days")

# Generate trading signals
signals = mr.generate_signals(
    price_series,
    entry_z=2.0,    # Entry at 2 std devs
    exit_z=0.5      # Exit at 0.5 std devs
)

# Current position
current_z = mr.calculate_z_score(current_price)
print(f"Current Z-score: {current_z:.2f}")

if signals[-1] == 1:
    print("Long signal: Price is 2+ std devs below mean")
elif signals[-1] == -1:
    print("Short signal: Price is 2+ std devs above mean")
```

---

## Risk Management {#risk-management}

### Position Sizing

**Kelly Criterion** (for positive expectancy strategies):

```
f* = (W × AvgWin - L × AvgLoss) / AvgWin

Position_Size = Capital × f*

Where:
- W = Win rate
- L = Loss rate (1 - W)
- AvgWin, AvgLoss = Average magnitude of wins/losses
```

**Conservative Sizing**:
```
Position_Size = Capital × (0.5 × f*)  # Half-Kelly for safety
```

### Stop Losses

**Statistical Stop Loss**:
```
Stop = Entry_Price ± (3 × σ)  # 3 std dev move = extreme

For mean reversion:
  Entry Z = 2.0
  Stop Z = 3.0
  Profit Target Z = 0.5
```

**Time-Based Stop Loss**:
```
Exit after: 3 × Half_Life (if trade not profitable)

Rationale: After 3 half-lives, probability of reversion decreases
```

### Correlation Risk

**Basket Arbitrage**:
```
Risk = ΔCorrelation × Position_Size

If basket members' correlations decrease:
- Synthetic price volatility increases
- Arbitrage spread widens
- Slippage worsens

Solution: Scale position size inversely with correlation
```

### Liquidity Risk

**Check Before Trade**:
```
1. Bid-Ask Spread < 50% of expected profit
2. Volume > 2 × Daily_Position_Size
3. Market depth sufficient for entry/exit
```

### Model Risk

**Monitor**:
1. **Parameter Drift**: Recalibrate β, θ, half-life weekly
2. **Regime Change**: Test stationarity monthly
3. **Correlation Breakdown**: Monitor portfolio correlations
4. **Tail Risk**: Track events beyond 3σ

---

## Performance Metrics

### Key Performance Indicators (KPIs)

**Return Metrics**:
```
Total Return = (Ending_Value - Starting_Value) / Starting_Value

Annualized Return = (1 + Total_Return)^(252/Days) - 1

Daily Return = ln(Price_t / Price_t-1)
```

**Risk Metrics**:
```
Volatility = Std(Daily_Returns) × √252

Sharpe Ratio = (Annual_Return - Risk_Free_Rate) / Volatility

Sortino Ratio = Annual_Return / Downside_Volatility
  Downside_Volatility = Std(Negative_Returns) × √252
```

**Efficiency Metrics**:
```
Profit Factor = Gross_Profits / Gross_Losses

Win Rate = Winning_Trades / Total_Trades

Payoff Ratio = Avg_Win / Avg_Loss
```

---

## Common Pitfalls and Solutions

| Problem | Cause | Solution |
|---------|-------|----------|
| Overfitting | Using too much parameter tuning | Use 80/20 train-test split |
| Look-ahead bias | Using future data in analysis | Ensure parameters known at trade time |
| Slippage ignored | Model assumes instant execution | Include realistic transaction costs |
| Static hedges | β, weights don't update | Recalculate daily/weekly |
| Mean shift | Historical mean no longer valid | Implement regime detection |
| Survivorship bias | Delisted stocks ignored | Include failed pairs in backtest |

---

## References and Further Reading

### Academic Papers
1. Nath, P. (2003) - "High Frequency Pairs Trading with Cointegration"
2. Gatev, E., et al. (2006) - "Pairs Trading"
3. Granger, C. W. J. (1981) - "Some Properties of Time Series Data"

### Books
1. "Statistical Arbitrage" - Andrew Pole
2. "Algorithmic Trading" - Ernie Chan
3. "Quantitative Trading" - Ernest P. Chan

### Tools & Libraries
- **statsmodels**: Cointegration and ADF tests
- **pandas**: Time series manipulation
- **numpy**: Mathematical computations
- **scipy**: Statistical functions

---

## Conclusion

Statistical arbitrage offers systematic approaches to exploiting market inefficiencies. Success requires:

1. **Sound Theory**: Understanding mathematical foundations
2. **Proper Testing**: Cointegration tests, stationarity verification
3. **Risk Management**: Position sizing, stop losses, correlation monitoring
4. **Robust Implementation**: Clean code, logging, monitoring
5. **Continuous Monitoring**: Parameter drift, regime changes, performance tracking

Each strategy has different risk/return profiles. Combinations of multiple strategies provide diversification and smoother returns.

---

**Last Updated**: 2025
**Author**: Quantitative Research Team
**Version**: 1.0
