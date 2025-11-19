# Technical Pattern Recognition System

## Overview

This module implements comprehensive technical analysis pattern recognition, identifying candlestick patterns, support/resistance levels, Fibonacci retracements, and larger chart formations. These patterns help traders identify potential reversals, continuations, and support/resistance zones.

---

## 1. Candlestick Pattern Recognition

### What Are Candlestick Patterns?

Candlestick patterns are visual representations of price action within a specific time period. Each candle shows:
- **Open**: Opening price
- **High**: Highest price in the period
- **Low**: Lowest price in the period
- **Close**: Closing price

The "body" is the range between open and close, while "shadows" extend to high and low.

### Implemented Patterns

#### Hammer Pattern (Bullish Reversal)

**Characteristics:**
- Small body at the top
- Long lower shadow (2x+ body length)
- Minimal upper shadow
- Often appears after a downtrend

**Formula:**
```
Condition: Lower Shadow > 2 × Body Length AND Upper Shadow < Body Length/2
Body Color: Bullish (Close > Open)
```

**Trading Signal:**
```
Signal Type: BUY
Entry Level: Close of hammer candle
Stop Loss: Low of hammer - (ATR × 0.3)
Take Profit: Close + (Close - Low)
Confidence: 0.70
```

**Interpretation:**
The long lower shadow shows rejection of lower prices (buying pressure), suggesting a potential uptrend reversal.

---

#### Inverse Hammer Pattern (Bullish Reversal)

**Characteristics:**
- Small body at the bottom
- Long upper shadow (2x+ body length)
- Minimal lower shadow
- Also called "Shooting Star" (depending on position)

**Formula:**
```
Condition: Upper Shadow > 2 × Body Length AND Lower Shadow < Body Length/2
Body Color: Bearish (Close < Open)
```

**Trading Signal:**
```
Signal Type: BUY
Entry Level: Close of inverse hammer candle
Stop Loss: Low of candle - (ATR × 0.3)
Take Profit: High + (High - Low)
Confidence: 0.65
```

---

#### Doji Pattern (Indecision)

**Characteristics:**
- Opening price approximately equals closing price (minimal body)
- Long shadows on both sides
- Represents indecision between bulls and bears
- Can signal potential reversal or continuation

**Formula:**
```
Condition: |Open - Close| ≤ Total Range × 5%
Total Range = High - Low
```

**Trading Signal:**
```
Signal Type: HOLD (needs confirmation)
Entry Level: Close of Doji
Stop Loss: Low - (ATR × 0.3)
Take Profit: High + (ATR × 0.3)
Confidence: 0.60
Pattern Direction: NEUTRAL
```

**Interpretation:**
Doji is not a standalone signal—needs confirmation from subsequent candles showing strong directional movement.

---

#### Bullish Engulfing (Reversal)

**Characteristics:**
- Current candle completely engulfs the previous candle
- White (bullish) candle engulfs black (bearish) candle
- Shows strong buying pressure overcoming previous selling

**Formula:**
```
Conditions:
1. Close(t) > Open(t)  [Current bullish candle]
2. Close(t-1) ≤ Open(t-1)  [Previous bearish candle]
3. Open(t) < Close(t-1)  [Current opens below previous close]
4. Close(t) > Open(t-1)  [Current closes above previous open]
```

**Trading Signal:**
```
Signal Type: BUY
Entry Level: Close of engulfing candle
Stop Loss: Low - (ATR × 0.3)
Take Profit: Close + (Close - Open)
Confidence: 0.75
```

---

#### Bearish Engulfing (Reversal)

**Characteristics:**
- Black (bearish) candle engulfs white (bullish) candle
- Shows strong selling pressure overcoming previous buying

**Formula:**
```
Conditions:
1. Close(t) < Open(t)  [Current bearish candle]
2. Close(t-1) ≥ Open(t-1)  [Previous bullish candle]
3. Open(t) > Close(t-1)  [Current opens above previous close]
4. Close(t) < Open(t-1)  [Current closes below previous open]
```

**Trading Signal:**
```
Signal Type: SELL
Entry Level: Close of engulfing candle
Stop Loss: High + (ATR × 0.3)
Take Profit: Close - (Open - Close)
Confidence: 0.75
```

---

#### Bullish Harami (Reversal, weaker than engulfing)

**Characteristics:**
- Current candle completely inside previous candle range
- White candle inside black candle (opposite of engulfing)
- Suggests weakening momentum and potential reversal

**Formula:**
```
Conditions:
1. Close(t) > Open(t)  [Current bullish]
2. Close(t-1) ≤ Open(t-1)  [Previous bearish]
3. Open(t) > Low(t-1) AND Close(t) < High(t-1)  [Inside range]
4. Open(t) ≥ Close(t-1) AND Close(t) ≤ Open(t-1)  [Properly contained]
```

**Trading Signal:**
```
Signal Type: BUY
Entry Level: Close of harami candle
Stop Loss: Low - (ATR × 0.3)
Take Profit: High of previous candle
Confidence: 0.65
```

---

#### Bearish Harami (Reversal)

**Characteristics:**
- Black candle inside white candle
- Suggests weakening uptrend momentum

**Formula:**
```
Conditions:
1. Close(t) < Open(t)  [Current bearish]
2. Close(t-1) ≥ Open(t-1)  [Previous bullish]
3. Open(t) < High(t-1) AND Close(t) > Low(t-1)  [Inside range]
```

**Trading Signal:**
```
Signal Type: SELL
Entry Level: Close of harami candle
Stop Loss: High + (ATR × 0.3)
Take Profit: Low of previous candle
Confidence: 0.65
```

---

## 2. Support and Resistance Level Identification

### What Are Support and Resistance Levels?

- **Support**: Price level where buying interest emerges, preventing further decline
- **Resistance**: Price level where selling interest emerges, preventing further rise
- **Pivot Point**: Central level calculated from previous day's OHLC

### Methods for Identification

#### 1. Local Extrema Method

**Algorithm:**
```
For each bar i:
    IF High[i] >= High[i-5:i] AND High[i] >= High[i+1:i+5]:
        Mark as Resistance

    IF Low[i] <= Low[i-5:i] AND Low[i] <= Low[i+1:i+5]:
        Mark as Support
```

**Confirmation:**
- Multiple touches within 1% of level (at least 2 touches)
- Stronger level with more touches

---

#### 2. Pivot Point Method

**Formulas:**

```
Pivot (P) = (High + Low + Close) / 3

Resistance 1 (R1) = (2 × Pivot) - Low
Resistance 2 (R2) = Pivot + (High - Low)

Support 1 (S1) = (2 × Pivot) - High
Support 2 (S2) = Pivot - (High - Low)
```

**Interpretation:**

| Level | Probability | Usage |
|-------|---|---|
| R2 | Low | Major breakout resistance |
| R1 | Medium | First resistance |
| Pivot | Medium | Neutral zone |
| S1 | Medium | First support |
| S2 | Low | Major breakout support |

---

#### 3. Price Clustering Method

**Algorithm:**
```
Recent_Prices = Last 20 days of closing prices
Create 5-bin histogram
Identify bins with highest frequency
Cluster Price = Center of highest-frequency bin
```

**Interpretation:**
High price clustering indicates strong support/resistance (price aggregation)

---

## 3. Fibonacci Retracement Levels

### What Are Fibonacci Retracements?

Fibonacci levels are based on the Fibonacci sequence (1, 1, 2, 3, 5, 8, 13, 21...). In trading, the key ratios are:
- **23.6%**: Minor retracement
- **38.2%**: Common retracement
- **50.0%**: Popular psychological level
- **61.8%**: Golden ratio, strongest retracement
- **78.6%**: Deep retracement

### Calculation Method

**Step 1: Identify Swing High and Swing Low**
```
Swing High = Max(High) over lookback period
Swing Low = Min(Low) over lookback period
Difference = Swing High - Swing Low
```

**Step 2: Calculate Retracement Levels**
```
Level 23.6% = Swing High - (Difference × 0.236)
Level 38.2% = Swing High - (Difference × 0.382)
Level 50.0% = Swing High - (Difference × 0.500)
Level 61.8% = Swing High - (Difference × 0.618)
Level 78.6% = Swing High - (Difference × 0.786)
```

**Step 3: Calculate Extension Levels (targets)**
```
Extension 161.8% = Swing High + (Difference × 0.618)
Extension 261.8% = Swing High + (Difference × 1.618)
Extension 361.8% = Swing High + (Difference × 2.618)
```

### Trading Strategy Using Fibonacci

**Bullish Scenario (Pullback in Uptrend):**
```
Entry Zone: 38.2% - 61.8% retracement
Stop Loss: Below 78.6% retracement
Take Profit: 161.8% extension
```

**Bearish Scenario (Pullback in Downtrend):**
```
Entry Zone: 38.2% - 61.8% retracement (below previous high)
Stop Loss: Above 78.6% retracement
Take Profit: Previous lows or extensions
```

**Signal Generation:**
```
IF Price touches 61.8% AND is near support:
    Signal: BUY at 61.8%
    Stop Loss: 78.6%
    Take Profit: 38.2%
    Confidence: 0.65
```

---

## 4. Chart Pattern Detection

### Head and Shoulders Pattern (Bearish Reversal)

**Structure:**
```
Left Shoulder: Peak with supporting low
Head: Higher peak with supporting low (lower than shoulders)
Right Shoulder: Similar to left shoulder
Neckline: Line connecting the three lows
```

**Entry Rules:**
```
Entry: Breakout below neckline
Stop Loss: Above the head
Take Profit: Neckline - (Head Height - Neckline)
Target Distance = Head Height - Neckline
```

**Identification Formula:**
```
1. Three local maxima (peaks)
2. Middle peak (head) highest
3. Shoulder heights similar: 0.95 < Left/Right Ratio < 1.05
4. Pattern requires at least 10 bars
```

**Probability:** Strong bearish reversal, ~70% success rate

---

### Triangles (Consolidation Patterns)

#### Ascending Triangle (Bullish)

**Characteristics:**
- Lower trend line rising
- Upper trend line flat (resistance)
- Converging price action
- Breakout expected upward

**Detection:**
```
Condition: Slope(Lows) > 0.0005 AND |Slope(Highs)| < 0.0005
Entry: Above resistance line
Stop Loss: Below recent low
Take Profit: Resistance + (Range)
Confidence: 0.65
```

---

#### Descending Triangle (Bearish)

**Characteristics:**
- Upper trend line falling
- Lower trend line flat (support)
- Converging price action
- Breakout expected downward

**Detection:**
```
Condition: Slope(Highs) < -0.0005 AND |Slope(Lows)| < 0.0005
Entry: Below support line
Stop Loss: Above recent high
Take Profit: Support - (Range)
Confidence: 0.65
```

---

#### Symmetric Triangle (Neutral/Continuation)

**Characteristics:**
- Both trend lines converging
- Suggests consolidation before breakout
- Direction confirmed by breakout direction

**Detection:**
```
Condition: Slope(Highs) < -0.0002 AND Slope(Lows) > 0.0002
Interpretation: Neutral, wait for breakout confirmation
Confidence: 0.60
```

---

### Double Top and Double Bottom

#### Double Top (Bearish Reversal)

**Structure:**
```
First Peak: At resistance level
Valley: Pullback between peaks
Second Peak: Similar height to first (within 2%)
Breakdown: Below valley support
```

**Trading Rules:**
```
Entry: Below valley low
Stop Loss: Above the peaks
Take Profit: Valley - (Peak Height - Valley)
Confidence: 0.65
```

---

#### Double Bottom (Bullish Reversal)

**Structure:**
```
First Trough: At support level
Peak: Rally between troughs
Second Trough: Similar depth to first (within 2%)
Breakout: Above peak resistance
```

**Trading Rules:**
```
Entry: Above peak high
Stop Loss: Below the troughs
Take Profit: Peak + (Peak - Trough)
Confidence: 0.65
```

---

### Cup and Handle (Bullish Continuation)

**Structure:**
```
Cup: U-shaped consolidation with rounded bottom
Handle: Small pullback after cup (lasting 1-4 weeks)
Breakout: Price breaks above handle resistance
```

**Characteristics:**
- Forms during strong uptrend
- Cup usually lasts 3-12 months
- Handle typically 25-50% of cup depth

**Trading Rules:**
```
Entry: Breakout above handle resistance
Stop Loss: Below cup low
Take Profit: Cup High + Cup Depth
Confidence: 0.68
```

**Measurement:**
```
Cup Size = High - Low
Entry Point = Handle High
Stop Loss = Cup Low
Target = Entry + Cup Size
```

---

## 5. Pattern-Based Signal Generation

### Signal Types

Each identified pattern generates a `PatternSignal` with:

```python
PatternSignal(
    timestamp: int,           # Bar index
    pattern_name: str,        # Pattern name
    signal_type: str,         # 'BUY', 'SELL', 'HOLD'
    price: float,             # Current price
    confidence: float,        # 0.0 to 1.0 confidence
    pattern_direction: str,   # 'BULLISH', 'BEARISH', 'NEUTRAL'
    entry_level: float,       # Recommended entry
    stop_loss: float,         # Stop loss level
    take_profit: Optional[float]  # Take profit target
)
```

### Signal Strength and Confidence

**Confidence Scoring:**

| Pattern | Confidence | Reason |
|---------|---|---|
| Bullish/Bearish Engulfing | 0.75 | Strong reversal signal |
| Hammer/Inverse Hammer | 0.70 | Clear reversal pattern |
| Head and Shoulders | 0.70 | Established pattern |
| Triangles | 0.65 | Consolidation signal |
| Harami | 0.65 | Weaker than engulfing |
| Double Top/Bottom | 0.65 | Proven reversal pattern |
| Cup and Handle | 0.68 | Strong continuation |
| Fibonacci 61.8% Support | 0.65 | Golden ratio |
| Doji | 0.60 | Needs confirmation |

### Consensus Signals

Combine multiple patterns for higher confidence:

```
Total Confidence = Average of all signals at same bar
High Confidence = Confidence > 0.70
Entry Decision:
- 1 signal: Confidence ≥ 0.70
- 2 signals: Confidence ≥ 0.65
- 3+ signals: Confidence ≥ 0.60
```

---

## 6. Implementation Guide

### Basic Usage

```python
from technical_patterns import TechnicalPatternAnalyzer
import numpy as np

# Initialize analyzer
analyzer = TechnicalPatternAnalyzer()

# Prepare OHLC data
open_prices = np.array([...])
high_prices = np.array([...])
low_prices = np.array([...])
close_prices = np.array([...])

# Get all patterns
results = analyzer.analyze(open_prices, high_prices, low_prices, close_prices)

# Get all signals
all_signals = analyzer.get_all_signals(open_prices, high_prices, low_prices, close_prices)

# Get high-confidence signals only
high_conf_signals = analyzer.get_high_confidence_signals(
    open_prices, high_prices, low_prices, close_prices,
    min_confidence=0.70
)

print(f"Found {len(high_conf_signals)} high-confidence signals")
for signal in high_conf_signals:
    print(f"{signal.pattern_name}: {signal.signal_type}")
    print(f"  Entry: {signal.entry_level}, Stop: {signal.stop_loss}")
```

### Individual Pattern Detection

```python
# Candlestick patterns only
candlestick = CandlestickPatterns(atr_multiplier=0.3)
candle_signals = candlestick.recognize_patterns(open_prices, high_prices, low_prices, close_prices)

# Support/Resistance only
sr = SupportResistance(lookback_period=20, min_touches=2)
levels = sr.identify_levels(high_prices, low_prices, close_prices)

# Fibonacci only
fib = FibonacciRetracement()
fib_levels = fib.calculate_retracement(high_prices, low_prices, close_prices[-1])

# Chart patterns only
charts = ChartPatterns(min_pattern_bars=10)
chart_signals = charts.detect_patterns(high_prices, low_prices, close_prices)
```

### Integration with Trading System

```python
# Generate signals before market open
signals = analyzer.get_high_confidence_signals(open, high, low, close, min_confidence=0.70)

for signal in signals:
    if signal.signal_type == "BUY":
        execute_buy_order(
            price=signal.entry_level,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            pattern=signal.pattern_name
        )
    elif signal.signal_type == "SELL":
        execute_sell_order(
            price=signal.entry_level,
            stop_loss=signal.stop_loss,
            take_profit=signal.take_profit,
            pattern=signal.pattern_name
        )
```

---

## 7. Best Practices

### Pattern Confirmation

1. **Multiple Patterns**: Best signals occur when multiple patterns align
   ```
   Score = Sum of all pattern confidences at same bar
   Score > 1.5 = Strong signal
   ```

2. **Timeframe Alignment**: Patterns more reliable on higher timeframes
   - Daily: Strongest signals
   - 4-hour: Good signals
   - 1-hour: More false signals

3. **Volume Confirmation**:
   - Patterns backed by volume more reliable
   - Breakouts need volume spike
   - Consolidations need low volume

### Risk Management

1. **Stop Loss Placement**
   - Always use pattern-defined stop loss
   - Never risk more than 2% per trade

2. **Take Profit Levels**
   - Use pattern measurement for targets
   - Scale out at multiple levels
   - First target: Pattern measured move
   - Second target: Extension level

3. **Position Sizing**
   ```
   Position Size = Account Risk / (Entry - Stop Loss)
   Account Risk = 2% of account per trade
   ```

### Market Conditions

| Market Type | Best Patterns | Avoid |
|---|---|---|
| Trending Up | Hammer, Bullish Engulfing, Cup & Handle | Bearish patterns |
| Trending Down | Inverse Hammer, Bearish Engulfing | Bullish patterns |
| Ranging | Triangles, Head & Shoulders, Support/Resistance | Breakout patterns |
| High Volatility | Fibonacci levels, Doji (indecision) | Tight patterns |
| Low Volatility | Ascending/Descending Triangles | - |

---

## 8. Parameter Tuning Guide

### Candlestick Patterns
```
ATR Multiplier: 0.2 - 0.5 (default 0.3)
Lower = More sensitive
Higher = More conservative
```

### Support/Resistance
```
Lookback Period: 10-30 (default 20)
Min Touches: 2-3 (default 2)
```

### Chart Patterns
```
Min Pattern Bars: 8-15 (default 10)
Lower = Shorter patterns detected
Higher = Longer patterns only
```

### Fibonacci
```
Lookback Period: 252 (one year)
Standard Levels: 23.6%, 38.2%, 50%, 61.8%, 78.6%
Extensions: 161.8%, 261.8%, 361.8%
```

---

## 9. Common Pitfalls

### False Signals

**Problem:** Too many false breakout signals
**Solution:** Require volume confirmation, use longer timeframes

**Problem:** Engulfing patterns in low volume
**Solution:** Filter by volume spike, require above-average volume

**Problem:** Fibonacci levels too wide in choppy markets
**Solution:** Add volatility filter, wait for clear trend

### Whipsaws

**Problem:** Entered buy, immediate reversal to sell
**Solution:**
- Wait for candle close confirmation
- Use tighter stops initially
- Require multiple pattern confirmation

### Timing Issues

**Problem:** Identified pattern too late
**Solution:**
- Scan larger timeframes first
- Identify pattern completion conditions
- Act on breakout confirmation, not formation

---

## 10. Code Reference

### Main Classes

1. **CandlestickPatterns**: Recognizes single/double candle patterns
2. **SupportResistance**: Identifies price levels and pivots
3. **FibonacciRetracement**: Calculates retracement and extension levels
4. **ChartPatterns**: Detects multi-bar chart formations
5. **TechnicalPatternAnalyzer**: Unified interface for all analysis

### Key Methods

```python
analyzer.analyze()                    # Full analysis
analyzer.get_all_signals()           # All patterns as signals
analyzer.get_high_confidence_signals()  # Filtered by confidence

candlestick.recognize_patterns()     # Candle patterns
sr.identify_levels()                 # Support/resistance
fibonacci.calculate_retracement()    # Fib levels
charts.detect_patterns()             # Chart patterns
```

---

## References

- Elder, A. (1993). Trading for a Living
- Bulkowski, T. (2005). Encyclopedia of Chart Patterns
- Murphy, J. (1999). Technical Analysis of the Financial Markets
- Pring, M. (2002). Technical Analysis Explained
- Pesavento, L. & Shapiro, S. (1997). Fibonacci Ratios with Pattern Recognition

---

## Disclaimer

This information is for educational purposes only. Past performance does not guarantee future results. Always backtest strategies on historical data before live trading. Consult with a financial advisor before implementing any trading strategy.
