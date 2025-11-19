# Order Flow and Market Making Analysis

Comprehensive guide to order flow microstructure, market maker behavior, and informed trading detection.

## Table of Contents

1. [VPIN (Volume-Synchronized Probability of Informed Trading)](#vpin)
2. [Order Book Imbalance](#order-book-imbalance)
3. [Buy/Sell Pressure Metrics](#buysell-pressure-metrics)
4. [Market Maker Spread Optimization](#market-maker-spread-optimization)
5. [Inventory Risk Management](#inventory-risk-management)
6. [Implementation Guide](#implementation-guide)

---

## VPIN

### Concept

VPIN (Volume-Synchronized Probability of Informed Trading) measures the likelihood that trading volume contains informed traders. It's based on the observation that informed traders accumulate positions systematically, creating directional volume imbalances.

**Key Insight**: When buy volume significantly deviates from sell volume, informed traders may be active.

### Formula

**Basic VPIN Calculation:**

```
VPIN = E[|ΔV_B - ΔV_S|] / (ΔV_B + ΔV_S)
```

Where:
- `ΔV_B` = Buy volume in a bucket
- `ΔV_S` = Sell volume in a bucket
- `E[·]` = Expected value over N buckets

**Bucket-based Approach:**

```
VPIN_t = (1/N) × Σ(|V_B,i - V_S,i|) / (V_B,i + V_S,i)
```

Where:
- N = number of buckets in the window
- i = bucket index
- Buckets are created on volume thresholds (e.g., every $1M of traded volume)

### Trade Classification (Tick Rule)

```
If price_t > price_{t-1}  →  BUY (tick up)
If price_t < price_{t-1}  →  SELL (tick down)
If price_t = price_{t-1}  →  Classify using previous trade direction
```

### Interpretation

- **VPIN ≈ 0.5**: Random/uninformed trading (volume equally split buy/sell)
- **VPIN > 0.6**: High probability of informed trading
- **VPIN > 0.7**: Very high informed trading probability
- **VPIN < 0.4**: Uninformed/noise trading

### Empirical Evidence

- High VPIN precedes market stress events and flash crashes
- VPIN > 0.65 shows increased adverse price movement risk
- Useful for estimating latent liquidity levels

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `window_size` | 50 | Number of buckets in calculation window |
| `bucket_volume` | $1M | Volume threshold for bucket creation |

---

## Order Book Imbalance

### Concept

Order book imbalance measures the relative strength of buy vs sell orders at different price levels. It reflects immediate supply-demand dynamics.

### Formula

**Depth Imbalance (Top N Levels):**

```
Imbalance_depth = (Σ Bid_Volume - Σ Ask_Volume) / (Σ Bid_Volume + Σ Ask_Volume)
```

**Range**: [-1, 1]
- +1 = All buy orders (extreme buying pressure)
- 0 = Balanced book
- -1 = All sell orders (extreme selling pressure)

### Weighted Imbalance

Gives more weight to closer price levels (better execution impact):

```
Weighted_Imbalance = Σ(w_i × (B_i - A_i)) / Σ(w_i × (B_i + A_i))

where w_i = 1/i (decreasing weight with depth)
```

**Intuition**: Level 1 (best bid/ask) has 1x weight, Level 2 has 0.5x weight, etc.

### Midprice Imbalance

Simplest form - just best bid and ask volumes:

```
Imbalance_best = (Bid_Volume - Ask_Volume) / (Bid_Volume + Ask_Volume)
```

### Predictive Power

- Positive imbalance → Higher probability of price increases
- Imbalance persistence → Short-term momentum
- Imbalance reversals → Mean reversion signals

### Use Cases

1. **Short-term price prediction**: Imbalance correlates with next tick direction
2. **Liquidity assessment**: Measures market depth
3. **Market microstructure**: Identifies informed vs uninformed orders
4. **Trade execution**: Guide for best execution algorithms

---

## Buy/Sell Pressure Metrics

### Concept

These metrics quantify the relative strength of buying vs selling activity, indicating market direction bias.

### 1. Basic Pressure

```
Buy_Pressure = Buy_Volume / (Buy_Volume + Sell_Volume)
Sell_Pressure = Sell_Volume / (Buy_Volume + Sell_Volume)

Buy_Pressure + Sell_Pressure = 1
```

**Range**: [0, 1]

### 2. Net Buy Pressure

Signed metric showing directional pressure:

```
Net_Pressure = (Buy_Volume - Sell_Volume) / (Buy_Volume + Sell_Volume)
```

**Range**: [-1, 1]
- +1 = Pure buying (all trades are buys)
- 0 = Balanced volume
- -1 = Pure selling (all trades are sells)

### 3. Aggressive Buy/Sell Ratio

Measures aggressiveness of one side:

```
Aggressive_Buy_Ratio = Aggressive_Buy_Volume / Total_Buy_Volume
```

**Definition**: Aggressive orders = market orders (cross the spread)

**Interpretation**:
- High ratio → Buyers willing to pay: Bullish
- Low ratio → Buyers using limit orders: Bearish (price-conscious)

### 4. Cumulative Net Buying Pressure

Over a time window:

```
CNBP_t = Σ(BuyVolume_i - SellVolume_i) / Σ(TotalVolume_i)
```

**Use**: Detects cumulative directional flow building up.

### Application Examples

| Metric | Interpretation | Trading Signal |
|--------|----------------|----|
| Buy_Pressure > 0.65 | Strong buying | Bullish |
| Net_Pressure < -0.6 | Strong selling | Bearish |
| Aggressive_Buy_Ratio > 0.7 | Aggressive buying | Demand strength |
| CNBP trending up | Cumulative buying pressure | Momentum building |

---

## Market Maker Spread Optimization

### Concept

Market makers balance profitability (wider spreads) with competitiveness (tighter spreads). Optimal spreads depend on:
- Inventory levels
- Volatility
- Order arrival rates
- Risk aversion

### Avellaneda-Stoikov Model

**Most widely used market maker model** (Avellaneda & Stoikov, 2008)

#### Formula

```
s* = (2/γ) × ln(1 + γ/k) + (γ × q × σ² × T) / k
```

Where:
- `s*` = Optimal spread
- `γ` = Risk aversion coefficient (>0)
- `q` = Current inventory position
- `σ` = Volatility
- `T` = Time to exit/liquidity horizon
- `k` = Order arrival intensity (orders/time)

#### Simplified Form

**Baseline Reserve Spread:**
```
s_reserve = (2/γ) × ln(1 + γ/k)
```
This is the spread needed to cover risk in an infinite horizon.

**Inventory Adjustment:**
```
Δs = (γ × q × σ² × T) / k
```

### Bid-Ask Skew

Adjust spreads asymmetrically based on inventory:

```
bid_spread = s/2 + Δs/2   (wider if long, narrower if short)
ask_spread = s/2 - Δs/2   (narrower if long, wider if short)
```

**Intuition**: If holding excess inventory, make it easier to sell (narrow ask spread) and harder to buy (wide bid spread).

### Inventory-Cost Spread Model

Simple model scaling spread with inventory usage:

```
Spread_Adjustment = α × (q / Q_max) × σ

where:
- α = sensitivity parameter (0.5)
- q = current inventory
- Q_max = maximum inventory limit
- σ = volatility
```

**Implementation:**
```
base_spread = 0.1 × σ
bid_spread = base_spread + adjustment
ask_spread = base_spread - adjustment
```

### Volatility-Scaled Spread

Account for both volatility and order imbalance:

```
Spread = Base_Spread × (1 + α×σ) × (1 + β×|Imbalance|)

where:
- α = volatility sensitivity (≈ 2.0)
- β = imbalance sensitivity (≈ 0.5)
```

**Use**: Widen spreads when:
1. Volatility increases (higher risk)
2. Order book is imbalanced (harder to hedge)

### Parameters

| Parameter | Typical Range | Description |
|-----------|---------------|-------------|
| Risk Aversion (γ) | 0.001 - 0.1 | Higher = narrower spreads |
| Volatility (σ) | 0.005 - 0.05 | Daily/intraday annualized |
| Time Horizon (T) | 0.1 - 1.0 | Fraction of trading day |
| Order Intensity (k) | 10 - 100 | Orders per hour |

---

## Inventory Risk Management

### Concept

Inventory is a liability for market makers. Holding positions creates:
1. **Variance risk**: Prices can move against position
2. **Liquidation costs**: Cost to exit large positions
3. **Opportunity costs**: Capital locked in position

Goal: Manage inventory to balance profitability and risk.

### Inventory Cost Model

**Expected holding cost:**

```
C = (1/2) × λ × σ² × q² × T + L × |q|

where:
- λ = Risk aversion (0.5)
- σ = Volatility
- q = Inventory
- T = Time horizon
- L = Liquidation cost rate
```

**Components:**
1. **Variance term** `(1/2) × λ × σ² × q² × T`
   - Quadratic in inventory (concentrated risk costs)
   - Example: Doubling inventory quadruples variance cost

2. **Liquidation term** `L × |q|`
   - Linear in inventory
   - Market impact cost to close position

### Example

```
q = 100 units
σ = 0.02 (2% daily volatility)
T = 1 hour = 1/8 trading day
λ = 0.5
L = 0.001 (0.1% of price)

Variance cost = 0.5 × 0.5 × 0.02² × 100² × 0.125 = $0.25
Liquidation cost = 0.001 × 100 = $0.10
Total cost = $0.35
```

### Target Inventory

Adjust target position based on price:

```
q_target = -α × (P - P_ref) / P_ref × Q_max

where:
- α = Sensitivity (0.5)
- P = Current price
- P_ref = Reference price
- Q_max = Max inventory limit
```

**Interpretation**:
- If price rises → Reduce target inventory (take profits)
- If price falls → Increase target inventory (average down)

### Inventory Limit Breach Probability

Risk of hitting max position limit:

```
P(breach) = 2 × [1 - N((Q_max - |q|) / (σ × √T))]

where N = Standard normal CDF
```

**Use**: Determine how aggressive to quote based on:
1. Current inventory
2. Remaining capacity
3. Expected volatility moves

### Rebalancing Signals

Generate adjustment intensities:

```
buy_intensity = max(0, -q) / Q_max
sell_intensity = max(0, q) / Q_max
```

**Use**: When sell_intensity high, offer tighter ask spread to sell position.

---

## Implementation Guide

### Basic Usage

#### 1. Calculate VPIN

```python
from order_flow import VPIN

vpin = VPIN(window_size=50, bucket_volume=1e6)

# Add trades (stream data)
for price, volume, prev_price in market_data:
    vpin.add_trade(price, volume, prev_price)

# Get informed trading probability
prob_informed = vpin.calculate()
```

#### 2. Measure Order Book Imbalance

```python
from order_flow import OrderBookImbalance

# Bid-ask book: [[price, volume], ...]
bids = [[100.0, 1000], [99.9, 1500], ...]
asks = [[100.1, 800], [100.2, 1200], ...]

imbalance = OrderBookImbalance.calculate_imbalance(
    np.array(bids), np.array(asks), depth=5
)
```

#### 3. Determine Buy/Sell Pressure

```python
from order_flow import BuySellPressure

buy_vol = 50000
sell_vol = 30000

buy_p, sell_p = BuySellPressure.calculate_pressure(buy_vol, sell_vol)
net_p = BuySellPressure.net_buy_pressure(buy_vol, sell_vol)

print(f"Buy: {buy_p:.2%}, Sell: {sell_p:.2%}, Net: {net_p:.4f}")
```

#### 4. Optimize Market Maker Spreads

```python
from order_flow import MarketMakerSpread

inventory = 100        # units
max_inventory = 500    # units
volatility = 0.02      # 2% daily vol
time_to_exit = 1.0     # 1 day

bid_spread, ask_spread = MarketMakerSpread.avellaneda_stoikov_spread(
    inventory, max_inventory, volatility, time_to_exit
)
```

#### 5. Manage Inventory Risk

```python
from order_flow import InventoryRiskManagement

# Calculate inventory cost
cost = InventoryRiskManagement.inventory_cost(
    inventory, volatility, time_to_exit
)

# Get target position
target = InventoryRiskManagement.target_inventory(
    current_price=100.5, reference_price=100.0,
    max_inventory=500
)

# Assess breach risk
breach_prob = InventoryRiskManagement.position_limit_breach_probability(
    inventory, max_inventory, volatility, time_to_exit
)
```

### Real-world Workflow

```python
from order_flow import OrderFlowAnalyzer

analyzer = OrderFlowAnalyzer(window_size=100)

# Process incoming market data
for event in market_stream:
    metrics = analyzer.update(
        price=event.price,
        volume=event.volume,
        bid_size=event.bid_volume,
        ask_size=event.ask_volume
    )

    # Make decisions based on metrics
    if metrics.vpin > 0.65:
        print("High informed trading activity detected")

    if metrics.order_imbalance > 0.5:
        print("Strong buying pressure - bullish signal")

    if abs(metrics.net_flow) > 0.6:
        print(f"Directional flow detected: {metrics.net_flow:.3f}")
```

---

## Key Relationships

### 1. VPIN → Market Stress

- High VPIN correlates with increased volatility
- VPIN > 0.65 predicts flash crash events
- Useful early warning system for market stress

### 2. Order Imbalance → Price Movement

- Positive imbalance → Upward price momentum
- Imbalance strength correlates with price impact
- Reverts quickly (mean reversion property)

### 3. Buy/Sell Pressure → Volume Prediction

- Sustained pressure indicates trend continuation
- Pressure reversals signal trend exhaustion
- Useful for volume-weighted execution

### 4. Inventory ↔ Spreads ↔ Risk

```
Higher Inventory → Wider Spreads → Lower Profitability
Lower Inventory → Tighter Spreads → Higher Profitability
```

---

## Practical Tips

### VPIN Best Practices

1. Use larger bucket sizes for less frequent recalculation
2. Monitor VPIN trend, not just level
3. Combine with other risk metrics
4. Calibrate thresholds to your market

### Spread Optimization

1. Start with Avellaneda-Stoikov, adjust parameters for your venue
2. Monitor realized spread vs theory
3. Rebalance spreads every 10-100ms for low latency
4. Test sensitivity to volatility forecast errors

### Inventory Management

1. Set max inventory based on liquidation costs
2. Use target inventory for automatic rebalancing
3. Monitor breach probability as position risk metric
4. Reduce spreads when approaching limits

### Combined Signals

| Signal | Implication | Action |
|--------|------------|--------|
| High VPIN + Long Inventory | Informed trading + Too long | Widen asks, narrow bids |
| High Buy Pressure + Positive Imbalance | Sustained buying | Tighten ask spread |
| VPIN rising + Imbalance reversing | End of informed move | Normalize spreads |

---

## References

1. **Easley, D., López de Prado, M. M., & O'Hara, M.** (2012). "The Volume Clock: Insights into the High Frequency Paradigm". Journal of Portfolio Management, 39(1).

2. **Avellaneda, M., & Stoikov, S.** (2008). "High-frequency trading in a limit order book". Quantitative Finance, 8(3).

3. **O'Hara, M.** (2015). "Machine Learning Algorithmic Trading based on Limit Order Book Dynamics". Journal of Financial Econometrics, 13(3).

4. **Menkveld, A. J.** (2013). "High Frequency Trading and the New Market Makers". Journal of Financial Economics, 113(2).

---

## Appendix: Data Requirements

### Market Data Needed

1. **Tick data**:
   - Timestamp (microsecond precision)
   - Trade price
   - Trade volume
   - Trade direction (buy/sell side aggressor)

2. **Order book snapshots**:
   - Bid prices and volumes (depth: top 5-10 levels)
   - Ask prices and volumes (depth: top 5-10 levels)
   - Order book timestamp

3. **OHLCV bars** (optional):
   - Open, High, Low, Close prices
   - Volume
   - Time period (1-minute or 5-minute)

### Sampling Frequency

- VPIN: Every $500K-$1M of volume
- Order imbalance: Every 100ms - 1 second
- Spreads: Every 100-500ms
- Inventory: Real-time

---

**Version**: 1.0
**Last Updated**: 2025-11-19
