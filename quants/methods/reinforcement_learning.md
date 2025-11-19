# Reinforcement Learning for Trading

## Overview

This document covers reinforcement learning (RL) approaches to algorithmic trading, including theoretical foundations and practical implementations.

---

## 1. Trading as a Markov Decision Process (MDP)

### Definition
A Markov Decision Process is defined by the tuple (S, A, P, R, γ):

- **S (State Space)**: Market conditions + portfolio state
  - Price data (OHLCV)
  - Technical indicators (RSI, MACD, Bollinger Bands)
  - Portfolio metrics (cash, position, P&L)
  - Order book depth / volume profile

- **A (Action Space)**: Trading decisions
  - Discrete: {Buy, Hold, Sell}
  - Continuous: Order size ∈ [-1, 1]

- **P (Transition Probability)**: Market dynamics
  - Price movements follow stochastic processes
  - Order execution has slippage

- **R (Reward Function)**: Profit/loss signals
  - Immediate: Trade P&L
  - Cumulative: Risk-adjusted returns

- **γ (Discount Factor)**: Time preference (typically 0.95-0.99)

### Markov Property
The environment satisfies the Markov property: future state depends only on current state and action, not history.

---

## 2. Q-Learning

### Theoretical Foundation

Q-learning learns the action-value function Q(s, a) - the expected cumulative reward from taking action a in state s.

**Update Rule:**
```
Q(s, a) ← Q(s, a) + α[r + γ max_a' Q(s', a') - Q(s, a)]
```

Where:
- α: Learning rate (step size)
- r: Immediate reward
- γ: Discount factor
- max_a' Q(s', a'): Maximum Q-value in next state

### Advantages
- Model-free learning (no need to know transition dynamics)
- Off-policy learning (can learn from suboptimal data)
- Guaranteed convergence (with appropriate conditions)
- Simple implementation

### Disadvantages
- Requires discretized state space (limited scalability)
- Overestimation of Q-values
- Slow convergence in large state spaces

### Trading Application
```python
# State discretization example
def discretize_state(observation):
    # Bucket continuous features
    price_bins = pd.cut(observation[0], bins=10)
    volume_bins = pd.cut(observation[1], bins=5)
    position_bins = pd.cut(observation[2], bins=3)

    return (price_bins, volume_bins, position_bins)

# Q-table: {state: [Q(s,Buy), Q(s,Hold), Q(s,Sell)]}
```

### When to Use
- Discrete, small state spaces
- Interpretability requirements
- Quick prototyping

---

## 3. Deep Q-Network (DQN)

### Motivation
Q-learning doesn't scale to continuous or high-dimensional state spaces. DQN uses neural networks to approximate Q-values.

### Algorithm
1. Store experiences in a replay buffer
2. Sample minibatches from the buffer
3. Train Q-network on minibatches
4. Use separate target network for stability
5. Update target network periodically

**Loss Function:**
```
L = E[(r + γ max_a' Q_target(s', a') - Q(s, a))²]
```

### Key Components

#### Experience Replay
- Stores transitions (s, a, r, s', done) in a circular buffer
- Breaks temporal correlations in data
- Allows reuse of past experiences
- Improves sample efficiency

#### Target Network
- Separate Q-network frozen periodically
- Reduces non-stationarity
- Improves convergence stability
- Updated every N steps

#### Double DQN
Addresses overestimation by decoupling action selection and evaluation:
```
targets = r + γ Q_target(s', argmax_a Q(s', a))
```

### Network Architecture
```
Input (state) → Hidden Layer (128 units, ReLU) →
Hidden Layer (128 units, ReLU) → Output (3 Q-values)
```

### Hyperparameters
- **Learning rate**: 0.001-0.0001
- **Replay buffer size**: 10,000-100,000
- **Batch size**: 32-64
- **Update frequency**: Every 1-4 steps
- **Target update frequency**: Every 1000-10000 steps
- **Epsilon decay**: 0.995-0.9999

### Trading-Specific Considerations
- State must include position and cash constraints
- Rewards scaled by portfolio value (for stability)
- Action space: {Buy, Hold, Sell} or continuous orders
- Transaction costs included in rewards

---

## 4. Policy Gradient Methods

### Actor-Critic Algorithm

Unlike Q-learning which learns values, policy gradient methods directly optimize the policy π(a|s).

**Policy Gradient Theorem:**
```
∇J(θ) = E[∇ log π(a|s) Q(s, a)]
```

The gradient is proportional to the advantage (Q-value minus baseline).

### Components

#### Actor (Policy Network)
- Outputs probability distribution over actions
- Updated via policy gradient

#### Critic (Value Network)
- Estimates state value V(s)
- Reduces variance in gradient estimates
- Baseline for advantage calculation

### Advantage Estimation

**Generalized Advantage Estimation (GAE):**
```
A_t = δ_t + (γλ)δ_{t+1} + (γλ)²δ_{t+2} + ...
δ_t = r_t + γV(s_{t+1}) - V(s_t)
```

Where λ ∈ [0, 1] trades off bias and variance.

### Loss Functions

**Actor Loss** (with entropy regularization):
```
L_actor = -E[log π(a|s) * A(s,a)] - β * H[π(a|s)]
```

**Critic Loss:**
```
L_critic = E[(V(s) - G_t)²]
```

Where G_t is the return.

### Advantages
- Can handle continuous action spaces
- More sample-efficient than Q-learning
- Better convergence properties
- Entropy bonus encourages exploration

### A3C (Asynchronous Advantage Actor-Critic)
- Multiple parallel workers
- Async gradient updates
- Reduced correlation in data
- Suitable for parallel/distributed training

### TRPO and PPO

**Proximal Policy Optimization (PPO):**
```
L^CLIP(θ) = E[min(r_t(θ)Â_t, clip(r_t(θ), 1-ε, 1+ε)Â_t)]
```

Where r_t(θ) = π(a|s,θ) / π(a|s,θ_old)

Advantages:
- Simpler than TRPO
- More stable training
- Better empirical performance

### Network Architecture
```
Input → Shared Trunk (128 units) →
Actor Head (128 units) → Policy (3 actions)
Critic Head (128 units) → Value (1)
```

---

## 5. Reward Shaping for Trading

### Challenge
Raw P&L rewards are sparse and noisy. Reward shaping guides learning toward profitable strategies.

### Reward Functions

#### 1. Simple P&L
```
r_t = (V_t - V_{t-1}) / V_{t-1}
```
- Direct, interpretable
- Noisy, sparse feedback

#### 2. Sharpe Ratio
```
Sharpe = (μ - r_f) / σ
```
- Incentivizes risk-adjusted returns
- Requires return history
- More complex optimization

#### 3. Sortino Ratio
```
Sortino = (μ - r_f) / σ_down
```
- Only penalizes downside volatility
- Better for trading with negative skew protection

#### 4. Calmar Ratio
```
Calmar = annual_return / max_drawdown
```
- Directly penalizes large losses
- Encourages consistent performance

#### 5. Composite Reward
```
r_t = α * P&L - β * transaction_cost - γ * max_drawdown + δ * stability_bonus
```
- Balances multiple objectives
- Tunable weights per strategy

### Reward Scaling
```python
# Normalize rewards to [-1, 1] for stable learning
r_normalized = tanh(r_raw / scale_factor)
```

### Implementation Considerations

1. **Frequency**: Reward at each step vs. episode end
2. **Scale**: Normalize by portfolio value for scale invariance
3. **Lookback**: Use rolling windows (20-60 bars) for metrics
4. **Penalties**: Transaction costs, holding costs, overnight gaps

### Reward Shaping Best Practices
- Keep rewards bounded (e.g., [-1, 1])
- Include both exploitation (returns) and exploration (diversity)
- Penalize risky behaviors (excessive leverage, concentration)
- Use potential-based shaping to preserve optimality

---

## 6. Implementation Comparison

| Method | State Space | Action Space | Scalability | Sample Efficiency | Convergence |
|--------|-------------|--------------|-------------|-------------------|-------------|
| Q-Learning | Discrete | Discrete | Low | Low | Guaranteed |
| DQN | Continuous | Discrete | Medium | Medium | Unstable |
| A3C | Continuous | Continuous | High | High | Good |
| PPO | Continuous | Continuous | High | High | Very Good |

---

## 7. Practical Trading Applications

### Pre-trade
1. **Feature engineering**: Normalize prices, compute indicators
2. **State design**: Include position constraints, risk limits
3. **Action design**: Discrete (buy/hold/sell) or continuous (position size)

### Training
1. **Data**: Use historical data, account for transaction costs
2. **Validation**: Walk-forward analysis, out-of-sample testing
3. **Monitoring**: Track returns, Sharpe, drawdown during training

### Deployment
1. **Exploration**: Maintain some randomness (epsilon-greedy)
2. **Position sizing**: Gradual scaling, risk limits
3. **Monitoring**: Real-time P&L, model drift detection

### Common Pitfalls
- **Overfitting**: Use walk-forward validation
- **Look-ahead bias**: Ensure state doesn't contain future information
- **Non-stationarity**: Retrain on recent data
- **Reward hacking**: Agents find unintended loopholes (e.g., exploit slippage)

---

## 8. Extensions and Advanced Topics

### Multi-Asset Trading
- State: Returns/features for N assets
- Action: Position for each asset
- Challenge: Curse of dimensionality

### Constrained RL
- Position limits, leverage constraints
- Lagrangian methods for constraint handling
- Reward penalties for violations

### Hierarchical RL
- High-level: Long/short bias
- Mid-level: Sector rotation
- Low-level: Individual trade execution

### Meta-Learning
- Adapt to market regimes quickly
- Learn across multiple assets
- Few-shot learning for new markets

### Risk-Sensitive RL
- CVaR (Conditional Value at Risk) objectives
- Risk constraints in optimization
- Pessimistic value estimates

---

## 9. Evaluation Metrics

### Return-based
- **Total Return**: (V_final - V_initial) / V_initial
- **Annualized Return**: (Total Return) ^ (252/n_days) - 1

### Risk-based
- **Volatility**: Standard deviation of daily returns
- **Max Drawdown**: Largest peak-to-trough decline
- **Sortino Ratio**: Return / downside volatility

### Risk-adjusted
- **Sharpe Ratio**: (Return - Rf) / Volatility
- **Calmar Ratio**: Return / Max Drawdown
- **Information Ratio**: Excess Return / Tracking Error

### Trading-specific
- **Win Rate**: % of profitable trades
- **Profit Factor**: Gross Profit / Gross Loss
- **Trade Count**: Frequency of trading
- **Avg Trade Duration**: Average holding time

---

## 10. Code Example

### Basic Q-Learning Trading Bot
```python
from reinforcement_learning import (
    TradingEnvironment,
    QLearningTrader,
    train_agent,
    evaluate_agent
)

# Prepare data
data = load_ohlcv_data('AAPL', '2020-01-01', '2023-12-31')

# Create environment
env = TradingEnvironment(
    data=data,
    initial_balance=100000,
    transaction_cost=0.001,
    reward_type='simple_pnl'
)

# Discretizer function
def state_discretizer(obs):
    # Implement discretization logic
    return tuple(np.digitize(obs[:5], bins=10))

# Create and train agent
agent = QLearningTrader(
    state_discretizer=state_discretizer,
    n_actions=3,
    learning_rate=0.1,
    gamma=0.95,
)

rewards = train_agent(agent, env, n_episodes=100)

# Evaluate
metrics = evaluate_agent(agent, env, n_episodes=10)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.3f}")
```

### Deep Q-Network Example
```python
from reinforcement_learning import TradingEnvironment, DQNTrader

# Create environment
env = TradingEnvironment(data, reward_type='sharpe')

# Create DQN agent
agent = DQNTrader(
    input_size=env.observation_space_shape[0],
    n_actions=3,
    hidden_size=128,
    learning_rate=0.001,
    buffer_size=10000,
)

# Train
rewards = train_agent(agent, env, n_episodes=100)
```

---

## References

1. **Q-Learning**: Watkins & Dayan (1992). "Q-learning"
2. **DQN**: Mnih et al. (2015). "Human-level control through deep RL"
3. **Policy Gradients**: Sutton et al. (2000). "Policy gradient methods"
4. **A3C**: Mnih et al. (2016). "Asynchronous Methods for Deep RL"
5. **PPO**: Schulman et al. (2017). "Proximal Policy Optimization"
6. **Trading RL**: Zhang et al. (2020). "Deep RL for Algorithmic Trading"

---

## Tools & Libraries

- **OpenAI Gym**: Standard RL environment interface
- **Stable Baselines3**: High-quality RL implementations
- **PyTorch/TensorFlow**: Neural network frameworks
- **Backtrader**: Backtesting framework (compatible)
- **Ray RLlib**: Distributed RL training

