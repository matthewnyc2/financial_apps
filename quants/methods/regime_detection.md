# Regime Detection and Market State Classification Guide

## Overview

Regime detection identifies different market states (regimes) in financial data - such as bull/bear markets, high/low volatility environments, or distinct behavioral patterns. This is crucial for adaptive trading strategies, risk management, and portfolio allocation.

**Key Concept**: Markets don't trade in a single regime. Understanding regime switches enables dynamic strategy adaptation and better risk management during regime transitions.

---

## 1. Hidden Markov Models (HMM)

### 1.1 Introduction to HMM

**Definition**: A probabilistic model where:
- **Hidden States**: Unobservable regimes (e.g., Bull, Bear, Neutral)
- **Observations**: Observable data (returns, volatility)
- **Markov Property**: Future states depend only on current state, not history

**HMM Components**:

1. **Transition Matrix** P(s_t | s_{t-1}):
   - Probability of transitioning between states
   - Captures regime persistence and switching

2. **Emission Distribution** P(x_t | s_t):
   - Probability of observing returns given state
   - Typically Gaussian for continuous data

3. **Initial Distribution** P(s_0):
   - Starting probabilities for each state

**Mathematics**:

$$P(x_1, ..., x_T, s_1, ..., s_T) = P(s_1) \prod_{t=1}^{T} P(x_t | s_t) P(s_{t+1} | s_t)$$

### 1.2 Fitting HMM to Financial Data

**Steps**:

1. Prepare returns data
2. Specify number of hidden states
3. Use Expectation-Maximization (EM) algorithm to estimate parameters
4. Predict hidden state sequence using Viterbi algorithm

**Code**:

```python
from regime_detection import HiddenMarkovRegimes

# Initialize with 2-state model (Bull/Bear)
hmm = HiddenMarkovRegimes(returns, n_states=2)

# Fit model
hmm.fit_gaussian_hmm(random_state=42, n_iter=1000)

# Predict states (Viterbi algorithm)
states = hmm.predict_states()

# Get soft probabilities
state_probs = hmm.predict_proba_states()
```

### 1.3 Viterbi Algorithm

**Purpose**: Find most likely sequence of hidden states

**Algorithm**:
```
1. Initialize: v_t(i) = P(s_1=i) * P(x_1|s_1=i)
2. Recursion: v_t(j) = max_i[v_{t-1}(i) * P(s_t=j|s_{t-1}=i) * P(x_t|s_t=j)]
3. Traceback: Find states maximizing v_T(i)
```

**Complexity**: O(n*k^2) where n=sequence length, k=number of states

**Advantages**:
- Hard assignment (crisp state labels)
- Accounts for transitions
- Computationally efficient

### 1.4 Interpreting HMM Results

**Parameter Extraction**:

```python
# Get model parameters
params = hmm.get_model_parameters()

# Transition matrix
trans = hmm.get_transition_matrix()
# Interpretation: P(next_state | current_state)

# State characteristics
stats = hmm.get_state_statistics()
# Mean return, volatility, duration for each state
```

**Example Interpretation** (2-state model):

| State | Mean Return | Volatility | Avg Duration | Interpretation |
|-------|------------|-----------|--------------|-----------------|
| 0 | 0.05% | 0.80% | 45 days | Bull: positive returns, lower vol |
| 1 | -0.03% | 1.50% | 25 days | Bear: negative returns, higher vol |

---

## 2. Change Point Detection

### 2.1 PELT Algorithm

**Purpose**: Identify structural breaks in time series

**Algorithm**: Pruned Exact Linear Time
- Dynamic programming with pruning
- Tests for changes in mean, variance
- O(n) complexity with pruning

**Method**:

$$\min_{\text{changepoints}} \left[ \sum_{i=1}^{m} \text{Cost}(y_{t_i} : y_{t_{i+1}}) + m \cdot \beta \right]$$

Where:
- **Cost()**: Negative log-likelihood for segment
- **β**: Penalty term (BIC or AIC)
- m: Number of segments

**Code**:

```python
from regime_detection import ChangePointDetection

cpd = ChangePointDetection(data)

# PELT with BIC penalty
result = cpd.pelt_algorithm(penalty='BIC', min_size=2)
changepoints = result['changepoints']
n_segments = result['n_segments']
```

**Parameters**:

- **BIC Penalty**: β = log(n)/2 → Favors fewer changepoints
- **AIC Penalty**: β = 1 → More changepoints detected
- **min_size**: Prevents over-fitting, ensures economical segments

### 2.2 CUSUM Algorithm

**Purpose**: Sequential detection of mean shifts

**Algorithm**: Cumulative Sum Control Chart

$$\text{CUSUM}^+ = \max(0, \text{CUSUM}^+_{t-1} + X_t - d)$$
$$\text{CUSUM}^- = \min(0, \text{CUSUM}^-_{t-1} + X_t + d)$$

Where:
- d: Drift parameter (mean shift size to detect)
- Threshold h: Trigger detection when |CUSUM| > h

**Advantages**:
- Sequential detection (can be used in real-time)
- High power for small shifts
- Separates positive/negative shifts

**Code**:

```python
cusum = cpd.cusum_algorithm(threshold=5.0, drift=1.0)
changepoints = cusum['changepoints']
cusum_pos = cusum['cusum_pos']  # Plot to visualize
cusum_neg = cusum['cusum_neg']
```

### 2.3 Kernel-Based Change Detection

**Approach**: Use rolling window statistics

```python
result = cpd.kernel_change_detection(window=50, threshold=2.0)
changepoints = result['changepoints']
z_scores = result['z_scores']
```

**Interpretation**: Changes flagged where rolling statistics deviate significantly

---

## 3. Volatility Regime Classification

### 3.1 Rolling Volatility Approach

**Definition**: Classify periods by realized volatility level

**Steps**:
1. Calculate rolling volatility: $\sigma_t = \sqrt{\text{Var}(r_{t-20:t})} \times \sqrt{252}$
2. Define thresholds (e.g., 33rd, 67th percentiles)
3. Assign regime labels (Low, Medium, High)

**Code**:

```python
from regime_detection import VolatilityRegimes

vol_reg = VolatilityRegimes(returns, window=20)
vol_reg.calculate_rolling_volatility()

# Quantile-based classification
regimes = vol_reg.classify_regimes_quantile(quantiles=[0.33, 0.67])

# HMM-based classification (more sophisticated)
regimes = vol_reg.classify_regimes_hmm(n_states=3)
```

### 3.2 HMM for Volatility Regimes

**Advantages over quantiles**:
- Accounts for persistence (regime stickiness)
- Models transition probabilities
- Soft probabilities (uncertainty quantification)
- Ordered by mean volatility

**Example** (3-state model):

| Regime | Mean Vol | Persistence | Interpretation |
|--------|----------|------------|-----------------|
| 0 (Low) | 8% | 0.95 | Calm market, sticky |
| 1 (Med) | 15% | 0.70 | Normal regime |
| 2 (High) | 35% | 0.60 | Crisis/stress, shorter duration |

### 3.3 Regime Statistics

**Analyze returns by volatility regime**:

```python
stats = vol_reg.regime_statistics()
# Includes: Count, Avg Return, Avg Volatility, Sharpe Ratio
```

**Key Insights**:
- Low vol regime often has positive Sharpe ratio
- High vol regime may have negative returns (tail risk)
- Transition dynamics are important for trading

---

## 4. Bull/Bear Regime Identification

### 4.1 Definition

**Bull Regime**:
- Positive trend (price > moving average)
- Returns above threshold
- Positive momentum

**Bear Regime**:
- Negative trend
- Negative returns
- Potential continuation of declines

### 4.2 Classification Method

**Code**:

```python
classification = vol_reg.bull_bear_classification(
    ma_window=200,  # Long-term trend
    return_threshold=0.0
)

# Returns: Market_Regime ('Bull', 'Bear', 'Neutral')
# Plus: Trend, Volatility, Trend Direction
```

**Interpretation**:
- Use multiple timeframes (daily trend vs weekly)
- Combine with volatility for full picture
- Bull + Low Vol = Best: growth with stability
- Bear + High Vol = Worst: losses with stress

---

## 5. Regime-Conditional Strategies

### 5.1 Momentum Strategy by Regime

**Intuition**: Market microstructure differs by regime
- Low vol: Longer trends, stronger momentum
- High vol: Whipsaws, shorter-term reversals

**Implementation**:

```python
from regime_detection import RegimeConditionalStrategies

strategy = RegimeConditionalStrategies(returns, regimes)
signals = strategy.momentum_strategy_by_regime(lookback=20)

# Position sizes adapted by regime:
# - Low vol: 1.0x position
# - Medium vol: 0.5x position
# - High vol: 0.25x position
```

**Logic**:
- High confidence in low vol → Full position
- Uncertainty in high vol → Defensive sizing

### 5.2 Mean Reversion by Regime

**Intuition**: Mean reversion stronger in stable regimes

**Implementation**:

```python
signals = strategy.mean_reversion_strategy_by_regime(
    lookback=20,
    threshold=1.5  # Std deviations
)

# Signal strength varies:
# Low vol + large deviation → Strong signal
# High vol + deviation → Weak/no signal
```

**Regime Adaptation**:
- Low vol: Act on 1.5σ deviations
- Medium vol: Require 2.25σ (higher threshold)
- High vol: Require 3.0σ (very strong signal)

### 5.3 Volatility Targeting

**Objective**: Maintain constant portfolio volatility

**Method**:
```
Position_Size = Target_Vol / Current_Vol

When vol increases → Position size decreases
When vol decreases → Position size increases
```

**Code**:

```python
signals = strategy.volatility_targeting_strategy(
    target_vol=0.15,  # 15% annual volatility
    vol_window=20
)
# Position size automatically adjusts
```

**Benefits**:
- Consistent risk exposure
- Reduces losses during vol spikes
- Automatically rebalances

### 5.4 Regime Change Detection

**Purpose**: Identify transitions between regimes

**Uses**:
- Entry/exit signals
- Portfolio rebalancing triggers
- Risk management adjustments

**Code**:

```python
changes = strategy.regime_change_detector(window=10)
# Detects: Regime change
# Measures: Stability of new regime
```

---

## 6. Model Selection and Diagnostics

### 6.1 Choosing Number of States

**Trade-offs**:
- **Too few states**: Over-simplification, missing regimes
- **Too many states**: Over-fitting, unstable parameters

**Information Criteria**:

```
AIC = 2k - 2*ln(L)
BIC = k*ln(n) - 2*ln(L)

Lower is better; BIC penalizes complexity more heavily
```

**Code**:

```python
from regime_detection import compare_hmm_models

comparison = compare_hmm_models(data, max_states=4)
# Returns: Log-likelihood, AIC, BIC for each model
# Select model with lowest BIC
```

### 6.2 Validation Checks

**Check 1: State Interpretability**
- Do states correspond to meaningful market conditions?
- Are transition probabilities realistic?

**Check 2: Persistence**
- Should be > 0.5 (regimes are sticky)
- Too high suggests over-differentiation

**Check 3: Duration**
- Low vol regime: typically 1-3 months
- High vol regime: typically 1-4 weeks
- Realistic duration validates model

### 6.3 Out-of-Sample Testing

**Important**: Don't evaluate on same data used for fitting

```python
# 1. Fit on training period
hmm.fit_gaussian_hmm()

# 2. Test on hold-out data
test_states = hmm.predict_states(test_data)

# 3. Evaluate strategy performance
performance = backtest_regime_strategy(test_returns, test_signals)
```

---

## 7. Practical Implementation

### 7.1 Complete Workflow

```python
from regime_detection import (
    HiddenMarkovRegimes,
    VolatilityRegimes,
    RegimeConditionalStrategies,
    backtest_regime_strategy
)
import pandas as pd

# 1. Load data
returns = pd.read_csv('returns.csv', index_col='Date')['Return']

# 2. HMM regime detection
hmm = HiddenMarkovRegimes(returns, n_states=2)
hmm.fit_gaussian_hmm()
hmm_states = hmm.predict_states()

# 3. Volatility regime classification
vol_reg = VolatilityRegimes(returns)
vol_regimes = vol_reg.classify_regimes_hmm(n_states=3)

# 4. Build strategy
strategy = RegimeConditionalStrategies(returns, vol_regimes)
signals = strategy.momentum_strategy_by_regime(lookback=20)

# 5. Backtest
performance = backtest_regime_strategy(returns, signals['Signal'])
print(f"Sharpe Ratio: {performance['Sharpe_Ratio']:.2f}")
print(f"Max Drawdown: {performance['Max_Drawdown']:.2%}")
```

### 7.2 Real-Time Monitoring

```python
# Rolling HMM update
recent_returns = returns.iloc[-252:]  # Last year
hmm.fit_gaussian_hmm()
current_states = hmm.predict_states(recent_returns)

# Current regime
current_regime = current_states[-1]
print(f"Current regime: {current_regime}")

# Confidence (probability)
probs = hmm.predict_proba_states(recent_returns)
confidence = probs[-1, current_regime]
print(f"Confidence: {confidence:.2%}")
```

---

## 8. Key Metrics for Regime-Based Trading

### 8.1 Performance by Regime

| Metric | Calculation | Interpretation |
|--------|-----------|-----------------|
| **Sharpe by Regime** | Return/Volatility * √252 | Risk-adjusted return per regime |
| **Win Rate** | Winning trades / Total trades | Frequency of correct signals |
| **Persistence** | P(same regime tomorrow) | Regime stickiness |
| **Transition Prob** | P(switch regimes) | Regime change likelihood |

### 8.2 Backtesting Code

```python
def backtest_regime_strategy(returns, signals, transaction_cost=0.001):
    """Evaluate strategy performance"""
    pnl = signals.shift(1) * returns
    costs = signals.diff().abs() * transaction_cost
    net_pnl = pnl - costs

    return {
        'Total_Return': (1 + net_pnl).prod() - 1,
        'Sharpe': net_pnl.mean() / net_pnl.std() * np.sqrt(252),
        'Max_Drawdown': (net_pnl.cumsum()).min(),
        'Win_Rate': (net_pnl > 0).sum() / len(net_pnl),
    }
```

---

## 9. Advanced Topics

### 9.1 Multivariate HMM

**Extension**: Model multiple assets with correlated regimes

```python
# Stack returns from multiple assets
multi_returns = np.column_stack([returns1, returns2, returns3])

hmm = HiddenMarkovRegimes(multi_returns, n_states=2)
hmm.fit_gaussian_hmm()
```

### 9.2 Time-Varying Transitions

**Motivation**: Transition probabilities may change over time

**Methods**:
- Rolling window HMM refitting
- Bayesian approaches with evolving parameters
- Regime-switching regression models

### 9.3 Jump-Diffusion Models

**Extension**: Combine HMM with jump component

**Advantage**: Captures crisis periods with sudden large moves

### 9.4 Machine Learning Extensions

**Recent developments**:
- Neural networks for regime classification
- LSTM/GRU for regime prediction
- Ensemble methods combining multiple detectors

---

## 10. Common Pitfalls and Solutions

### Pitfall 1: Over-Fitting

**Problem**: Too many states, fits noise not regimes

**Solution**:
- Use BIC for model selection (penalizes complexity)
- Validate on out-of-sample data
- Keep states interpretable (≤4 typically)

### Pitfall 2: Regime "Flip-Flopping"

**Problem**: Rapid regime switches, unstable predictions

**Solution**:
- Increase min_size parameter in PELT
- Use higher persistence threshold
- Combine multiple detection methods

### Pitfall 3: Look-Ahead Bias

**Problem**: Using current regime to trade today

**Solution**:
- Use regime signals with 1-day lag (shift)
- Validate on truly held-out test data
- Monitor forward performance, not backtest results

### Pitfall 4: Regime Changes During Crises

**Problem**: HMM adapts slowly to new regimes

**Solution**:
- Monitor regime change probability
- Use change point detection as early warning
- Consider hybrid approach (HMM + CUSUM)

---

## 11. Key References

### Academic Papers

1. **Hamilton, J. D. (1989)** - "A New Approach to the Economic Analysis of Nonstationary Time Series"
   - Original regime-switching models

2. **Guidolin, M., & Timmermann, A. (2007)** - "Asset allocation under multivariate regime switching"
   - Regime-switching portfolio management

3. **Ang, A., & Bekaert, G. (2002)** - "Regime Switches in Interest Rates"
   - Econometric modeling of regime switches

4. **Killick, R., Fearnhead, P., & Eckley, I. A. (2012)** - "Optimal detection of changepoints"
   - PELT algorithm reference

5. **Baum, L. E., & Petrie, T. (1966)** - "Statistical Inference for Probabilistic Functions of Finite State Markov Chains"
   - HMM foundations and Viterbi algorithm

### Software

- **hmmlearn**: Python library for HMM implementation
- **ruptures**: Change point detection algorithms
- **statsmodels**: Regime-switching regression models

---

## 12. Performance Monitoring

### 12.1 Strategy Dashboard

```python
# Track regime dynamics
regime_df = pd.DataFrame({
    'Date': returns.index,
    'Returns': returns.values,
    'Regime': states,
    'Signal': signals,
    'Position': signals.shift(1),
    'PnL': position * returns
})

# Visualizations:
# 1. Regimes over time
# 2. Cumulative returns by regime
# 3. Regime transition matrix (heatmap)
# 4. Signal strength vs regime
```

### 12.2 Rebalancing Schedule

```
Weekly:
- Check if regime has changed
- If changed, rebalance portfolio

Monthly:
- Refit HMM model with new data
- Update regime statistics
- Adjust strategy parameters if needed

Quarterly:
- Full performance review
- Consider model updates
- Assess regime persistence
```

---

## 13. Summary: Key Takeaways

1. **HMM**: Flexible framework capturing regime persistence and transitions
2. **Change Points**: Identify structural breaks, complementary to HMM
3. **Volatility Regimes**: Simple yet effective for risk management
4. **Regime Conditioning**: Adapt strategy parameters to market state
5. **Validation**: Always test on hold-out data, avoid over-fitting
6. **Implementation**: Use regime changes as portfolio management triggers

---

**Last Updated**: 2024
**Author**: Quantitative Analytics
**Status**: Production-Ready
**Library**: hmmlearn (Hidden Markov Models)
