# Machine Learning Methods for Trading

## Overview

This document describes machine learning approaches for algorithmic trading, including feature engineering, model selection, validation methodologies, and implementation details.

## Table of Contents

1. [Feature Engineering](#feature-engineering)
2. [Machine Learning Models](#machine-learning-models)
3. [Walk-Forward Validation](#walk-forward-validation)
4. [Feature Importance Analysis](#feature-importance-analysis)
5. [Implementation Guide](#implementation-guide)
6. [Best Practices](#best-practices)

---

## Feature Engineering

Effective feature engineering is critical for ML-based trading. Raw price data alone provides limited predictive power.

### Technical Indicators

#### Moving Averages (MA)

- **Simple Moving Average (SMA)**: Average of price over N periods
  - Common periods: 5, 10, 20, 50, 200
  - Captures trend direction
  - Slower response to recent changes

- **Exponential Moving Average (EMA)**: Weighted average giving more weight to recent prices
  - Faster response to price changes than SMA
  - Common periods: 12, 26
  - Used in MACD calculation

#### Relative Strength Index (RSI)

```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss
```

- **Period**: Typically 14 days
- **Interpretation**:
  - RSI > 70: Overbought (potential sell signal)
  - RSI < 30: Oversold (potential buy signal)
- **Use**: Momentum indicator, identifies extreme conditions

#### MACD (Moving Average Convergence Divergence)

```
MACD = EMA(12) - EMA(26)
Signal = EMA(9) of MACD
Histogram = MACD - Signal
```

- **Components**:
  - MACD line: Momentum indicator
  - Signal line: Trigger line
  - Histogram: Visual representation of divergence

- **Trading Signals**:
  - Buy: MACD crosses above signal line
  - Sell: MACD crosses below signal line

#### Bollinger Bands

```
Upper Band = SMA + (2 * Std Dev)
Middle Band = SMA
Lower Band = SMA - (2 * Std Dev)
```

- **Interpretation**:
  - Price touching upper band: Overbought
  - Price touching lower band: Oversold
  - Band width: Volatility measure

#### Average True Range (ATR)

```
TR = max(High - Low, |High - Close(prev)|, |Low - Close(prev)|)
ATR = SMA(TR, 14)
```

- **Measures**: Volatility in absolute terms
- **Use**: Position sizing, stop-loss placement
- **Period**: Typically 14 days

#### Stochastic Oscillator

```
%K = 100 * (Close - 14-Low) / (14-High - 14-Low)
%D = SMA(%K, 3)
```

- **Range**: 0-100
- **Signals**:
  - %K > 80: Overbought
  - %K < 20: Oversold
  - Crossover of %K and %D: Trading signal

#### Williams %R

```
%R = -100 * (14-High - Close) / (14-High - 14-Low)
```

- **Range**: -100 to 0
- **Similar to**: Stochastic oscillator
- **Use**: Identify overbought/oversold conditions

### Return-Based Features

#### Lagged Returns

Create features using historical returns:

```python
Returns = Close(t) / Close(t-1) - 1
Features:
  - Returns_Lag_1: Return from 1 day ago
  - Returns_Lag_2: Return from 2 days ago
  - Returns_Lag_5: Return from 5 days ago
  - Returns_Lag_10: Return from 10 days ago
```

**Rationale**: Market momentum and mean reversion effects

#### Volatility

```
Volatility_20 = Std(Returns[t-20:t])
Volatility_50 = Std(Returns[t-50:t])
```

- **Use**: Risk assessment, regime detection
- **Interpretation**: Higher volatility = higher risk

### Momentum Features

#### Rate of Change (ROC)

```
ROC_12 = (Close(t) - Close(t-12)) / Close(t-12)
ROC_25 = (Close(t) - Close(t-25)) / Close(t-25)
```

- **Measures**: Percent change over N periods
- **Use**: Trend strength detection

#### Volume Indicators

```
Volume_SMA = SMA(Volume, 20)
Volume_Ratio = Volume / Volume_SMA
```

- **Interpretation**:
  - Volume_Ratio > 1: Above average volume
  - High volume with price increases: Strong trend confirmation

---

## Machine Learning Models

### Random Forest

#### Classifier (Classification: Up/Down)

**Characteristics**:
- Ensemble of decision trees
- Each tree trained on random subset of features
- Predictions averaged across all trees
- Natural feature importance from tree splits
- Robust to outliers and nonlinear relationships

**Advantages**:
- Handles nonlinear relationships
- Feature importance provided
- Less prone to overfitting than single decision tree
- Works with mixed feature types

**Disadvantages**:
- Computationally expensive for large datasets
- Less interpretable than single tree
- May overfit if not tuned properly

**Hyperparameters**:
```python
n_estimators: Number of trees (100-500 typical)
max_depth: Maximum tree depth (10-30 typical)
min_samples_split: Minimum samples to split node (2-10)
min_samples_leaf: Minimum samples in leaf node (1-5)
```

#### Regressor (Regression: Continuous Targets)

**Use Cases**:
- Predicting next day's return magnitude
- Predicting price target
- Predicting volatility

**Key Differences from Classifier**:
- Minimizes MSE instead of classification error
- Outputs continuous values instead of class probabilities
- Better for magnitude prediction

### XGBoost

#### Advantages over Random Forest

1. **Gradient Boosting**: Sequential tree building minimizes loss
2. **Regularization**: Built-in L1/L2 regularization prevents overfitting
3. **Speed**: More efficient tree construction
4. **Missing Value Handling**: Learns best direction for missing values
5. **Feature Importance**: Multiple importance types (gain, cover, frequency)

#### XGBClassifier

**Use**: Binary/Multiclass classification
- Predicting direction: Up (1) vs Down (0)
- Predicting regime: Bull, Neutral, Bear

**Loss Function**: Binary crossentropy (for binary classification)

**Key Parameters**:
```python
n_estimators: Number of boosting rounds (100-1000)
max_depth: Maximum tree depth (3-10, typically smaller than RF)
learning_rate: Step size shrinkage (0.01-0.1)
subsample: Fraction of samples for tree building (0.5-1.0)
colsample_bytree: Fraction of features per tree (0.5-1.0)
```

#### XGBRegressor

**Use**: Predicting continuous values
- Next day return
- Price target
- Volatility forecast

**Loss Function**: Mean squared error (default)

### LSTM (Long Short-Term Memory)

#### Overview

- Recurrent Neural Network (RNN) variant
- Handles sequential/time-series data naturally
- Memory cells capture long-term dependencies
- Addresses vanishing gradient problem of standard RNNs

#### Architecture

```
Input Layer → LSTM Cells → Dense Layer → Output
    ↓            ↓
[Features]   [Memory]
```

#### Advantages

1. **Temporal Dependencies**: Captures patterns across time
2. **Variable Length Input**: Handles sequences of different lengths
3. **Memory Mechanism**: "Forgets" old irrelevant information
4. **Gradient Flow**: Mitigates vanishing gradient problem

#### Disadvantages

1. **Computational Cost**: More expensive than RF/XGBoost
2. **Training Time**: Requires more iterations
3. **Data Requirements**: Needs substantial training data
4. **Interpretability**: Black-box nature, harder to explain

#### When to Use LSTM

- Intraday trading with minute-level data
- Complex nonlinear temporal patterns
- Long-term dependency importance
- Sufficient historical data (1000+ samples)

#### Implementation Notes

```python
# Typical architecture
layers = [
    LSTM(64, input_shape=(lookback, n_features), return_sequences=True),
    Dropout(0.2),
    LSTM(32, return_sequences=False),
    Dropout(0.2),
    Dense(16, activation='relu'),
    Dense(1, activation='sigmoid')  # for classification
]
```

---

## Walk-Forward Validation

### Standard Backtesting Problem

Traditional k-fold cross-validation violates temporal ordering:
- **Issue**: Future data in training set
- **Result**: Unrealistic (overly optimistic) performance estimates
- **Example**: Using year 2023 data to train model, then testing on 2022 data

### Walk-Forward Validation Solution

Sequential validation respecting temporal order:

```
Period 1: Train on [1-100], Test on [101-120]
Period 2: Train on [1-120], Test on [121-140]  (or Train on [21-120])
Period 3: Train on [1-140], Test on [141-160]  (or Train on [41-140])
...
```

### Two Variants

#### 1. Growing Window (Anchored)

```
Train Set:  [===]
Test Set:       [==]

Train Set:  [=======]
Test Set:           [==]

Train Set:  [===========]
Test Set:               [==]
```

**Advantages**:
- Uses all historical data
- Accumulates more training data
- More stable estimates as more history available

**Disadvantages**:
- Longer training time for later folds
- Concept drift may be ignored (model trained on all history)

#### 2. Fixed/Rolling Window

```
Train Set:  [===]
Test Set:       [==]

Train Set:      [===]
Test Set:           [==]

Train Set:          [===]
Test Set:               [==]
```

**Advantages**:
- Uniform training set size
- Better for concept drift detection
- More consistent performance across folds

**Disadvantages**:
- Wastes early data
- Less data for initial models

### Implementation Example

```python
validator = WalkForwardValidator(n_splits=10, train_size=252, test_size=21)
# train_size=252: ~1 year of daily data
# test_size=21: ~1 month of daily data
# Rolling forward by test_size each period

results = validator.backtest(
    df=price_data,
    feature_cols=feature_list,
    target_col='Target',
    model_type='xgb_regressor'
)
```

### Metrics Calculation

```python
# Across all test periods
all_predictions = results['predictions']
all_actuals = results['actuals']

# Calculate performance metrics
mae = mean_absolute_error(all_actuals, all_predictions)
rmse = sqrt(mean_squared_error(all_actuals, all_predictions))
sharpe = calculate_sharpe_ratio(all_actuals)
```

---

## Feature Importance Analysis

### Random Forest Feature Importance

```python
# Measured by decrease in impurity (Gini)
importances = model.feature_importances_

# Interpretation: Sum of impurity decreases across all trees
# Higher value = more important
```

**Limitations**:
- Biased towards high-cardinality features
- Doesn't account for correlation
- Only measures in-sample importance

### XGBoost Feature Importance

Three types available:

#### 1. Gain (Default)

```python
importance_type='gain'
# Average loss reduction from feature
# Measures contribution to accuracy improvement
```

**Interpretation**: Most useful for understanding predictive contribution

#### 2. Cover

```python
importance_type='cover'
# Average number of samples where feature used
# Measures frequency of use
```

**Interpretation**: Shows robustness of feature usage

#### 3. Frequency

```python
importance_type='frequency'
# Number of times feature appears in trees
# Simple count of appearances
```

**Interpretation**: Basic usage frequency

### Permutation Importance

Model-agnostic approach:

```python
# 1. Get baseline performance (e.g., accuracy)
baseline_score = model.score(X_test, y_test)

# 2. For each feature:
#    a. Randomly shuffle feature values
#    b. Measure new performance
#    c. Importance = baseline - shuffled_score

# Interpretation: Higher drop in score = more important feature
```

**Advantages**:
- Model-agnostic
- Accounts for feature correlations
- More reliable for real importance

### Cumulative Importance Plot

```python
# Plot: X-axis = features (ranked by importance)
#       Y-axis = cumulative importance (%)

# Finding: 80/20 rule
# Typically: 20% of features drive 80% of predictions
# Use to select most important features
```

### Feature Interaction Analysis

Identify features that work together:

```python
# Method 1: SHAP values (model-agnostic)
# Shows each feature's contribution to prediction

# Method 2: Partial dependence plots
# Shows relationship between feature and prediction

# Method 3: Correlation analysis
# Identify multicollinear features
```

---

## Implementation Guide

### 1. Data Preparation

```python
from ml_trading import create_trading_dataset, get_feature_columns

# Load price data (OHLCV)
df = pd.read_csv('price_data.csv')

# Create features
trading_df = create_trading_dataset(df)

# Get feature column names
feature_cols = get_feature_columns(trading_df)
```

### 2. Model Selection and Training

```python
from ml_trading import MLTradingModel

# Initialize model
model = MLTradingModel(model_type='xgb_regressor', n_estimators=200)

# Prepare data
X_train, y_train = model.prepare_features(
    train_df,
    feature_cols=feature_cols,
    target_col='Target'
)

# Train
model.train(X_train, y_train)

# Feature importance
print(model.feature_importance.head(10))
```

### 3. Walk-Forward Backtest

```python
from ml_trading import WalkForwardValidator

# Setup validator
validator = WalkForwardValidator(n_splits=10, test_size=21)

# Run backtest
results = validator.backtest(
    df=trading_df,
    feature_cols=feature_cols,
    target_col='Target',
    model_type='xgb_regressor',
    n_estimators=200,
    max_depth=7
)

# Extract predictions and actuals
predictions = np.array(results['predictions'])
actuals = np.array(results['actuals'])
```

### 4. Performance Evaluation

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np

# Regression metrics
mse = mean_squared_error(actuals, predictions)
rmse = np.sqrt(mse)
mae = mean_absolute_error(actuals, predictions)

# Trading-specific metrics
returns = predictions  # Assuming predictions are returns
profit = np.sum(returns)
win_rate = np.sum(returns > 0) / len(returns)
sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-6)
max_drawdown = calculate_max_drawdown(np.cumprod(1 + returns))
```

### 5. Feature Importance Analysis

```python
# Aggregate importances from all walk-forward models
all_importances = []
for model in results['models']:
    if model.feature_importance is not None:
        all_importances.append(model.feature_importance)

# Average importance across folds
avg_importance = pd.concat(all_importances).groupby('feature')['importance'].mean()
avg_importance = avg_importance.sort_values(ascending=False)

# Plot
import matplotlib.pyplot as plt
avg_importance.head(20).plot(kind='barh')
plt.title('Average Feature Importance (Walk-Forward)')
plt.xlabel('Importance')
plt.show()

# Cumulative importance
cumsum = avg_importance.cumsum() / avg_importance.sum()
print("Features for 80% importance:", cumsum[cumsum <= 0.8].index.tolist())
```

---

## Best Practices

### Data Preparation

1. **Handle Missing Data**:
   - Forward fill for price data
   - Drop rows with NaN features
   - Don't use future information to fill past values

2. **Feature Scaling**:
   - StandardScaler for ML models
   - Fit on training data only, apply to test
   - Prevent leakage of future information

3. **Survivorship Bias**:
   - Include delisted stocks in backtest
   - Use historical composition of indices
   - Don't only test on survived stocks

### Model Development

1. **Start Simple**:
   - Begin with linear models (logistic regression)
   - Understand baseline performance
   - Add complexity gradually

2. **Hyperparameter Tuning**:
   - Use validation set (not test set) for tuning
   - Grid/random search with cross-validation
   - Monitor overfitting (train vs validation gap)

3. **Regularization**:
   - Use L1/L2 penalties
   - Adjust tree depth and leaf sizes
   - Early stopping with XGBoost

### Validation

1. **Proper Time Series Split**:
   - Always respect temporal order
   - Use walk-forward validation
   - Never look at future data in training

2. **Realistic Assumptions**:
   - Account for trading costs (commissions, slippage)
   - Realistic entry/exit prices
   - Market impact for large positions

3. **Statistical Significance**:
   - Test with sufficient samples
   - Calculate confidence intervals
   - Compare against benchmarks (buy-hold, random)

### Production Deployment

1. **Monitor Performance**:
   - Track real-world returns vs backtested
   - Detect model drift
   - Retrain regularly with new data

2. **Risk Management**:
   - Position sizing based on volatility
   - Stop-loss orders
   - Portfolio-level risk limits

3. **Documentation**:
   - Record hyperparameters and features
   - Version control models
   - Log all trades and reasoning

### Avoid Common Pitfalls

1. **Overfitting**:
   - Walk-forward validation catches this
   - Monitor complexity (number of trees, depth)
   - Regularization essential

2. **Look-Ahead Bias**:
   - Common in indicator calculation
   - Ensure features use only past data
   - Verify target is future information

3. **Data Snooping**:
   - Don't iterate on test set results
   - Use separate validation set for tuning
   - Report walk-forward results, not in-sample

4. **Concept Drift**:
   - Markets change over time
   - Retrain models periodically
   - Use rolling window validation

---

## Conclusion

Effective ML-based trading requires:

1. **Strong Features**: Technical indicators + momentum + returns
2. **Proper Models**: XGBoost usually outperforms Random Forest
3. **Correct Validation**: Walk-forward testing essential
4. **Risk Management**: Control position size and drawdown
5. **Continuous Monitoring**: Adapt to market changes

The implementation in `ml_trading.py` provides production-ready code for:
- Feature engineering (30+ indicators)
- Model training (RF and XGBoost)
- Walk-forward validation
- Feature importance analysis

Start with simple features and models, validate properly, and scale gradually.
