"""
Reinforcement Learning for Trading
===================================

This module implements various reinforcement learning algorithms for trading:
- Q-learning: Tabular value-based approach
- Deep Q-Network (DQN): Deep value-based approach with experience replay
- Policy Gradient Methods: Actor-Critic for continuous control
- Reward Shaping: Trading-specific reward engineering

Trading as an MDP:
- State: Market features (price, volume, technical indicators, portfolio state)
- Action: Buy, Hold, Sell (discrete) or order size (continuous)
- Reward: Profit/loss, Sharpe ratio, risk-adjusted returns
- Transition: Market dynamics and order execution
"""

import numpy as np
import pandas as pd
from collections import deque
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import warnings

# Try to import neural network library
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    warnings.warn("PyTorch not available. DQN and Policy Gradient methods require PyTorch.")


# ============================================================================
# TRADING ENVIRONMENT (GYM-LIKE INTERFACE)
# ============================================================================

@dataclass
class TradingState:
    """Represents the state of the trading environment."""
    market_features: np.ndarray  # OHLCV, indicators, etc.
    portfolio_value: float
    position: float  # Current position size (-1 to 1)
    cash: float
    timestamp: int


class TradingEnvironment:
    """
    Gym-like environment for trading.

    State: market features + portfolio state
    Actions: Buy (-1), Hold (0), Sell (1) or continuous order size
    Reward: P&L, risk-adjusted returns, trading costs
    """

    def __init__(
        self,
        data: np.ndarray,
        initial_balance: float = 100000,
        transaction_cost: float = 0.001,
        max_position: float = 1.0,
        reward_type: str = 'simple_pnl',
        window_size: int = 20,
    ):
        """
        Initialize trading environment.

        Args:
            data: OHLCV data (N, 5) where columns are [O, H, L, C, V]
            initial_balance: Starting capital
            transaction_cost: Percentage cost per transaction
            max_position: Maximum position size
            reward_type: 'simple_pnl', 'sharpe', 'sortino', 'calmar'
            window_size: Number of lookback bars for features
        """
        self.data = data
        self.initial_balance = initial_balance
        self.transaction_cost = transaction_cost
        self.max_position = max_position
        self.reward_type = reward_type
        self.window_size = window_size

        self.current_step = 0
        self.max_steps = len(data) - 1

        # Portfolio state
        self.balance = initial_balance
        self.position = 0.0  # Current position size
        self.entry_price = 0.0
        self.portfolio_values = [initial_balance]
        self.actions_taken = []
        self.rewards_history = []

        # State space info
        self.observation_space_shape = None
        self.action_space_n = 3  # Buy, Hold, Sell

    def reset(self) -> np.ndarray:
        """Reset environment to initial state."""
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.position = 0.0
        self.entry_price = 0.0
        self.portfolio_values = [self.initial_balance]
        self.actions_taken = []
        self.rewards_history = []

        return self._get_observation()

    def _get_observation(self) -> np.ndarray:
        """Extract state features from current market data."""
        if self.current_step < self.window_size:
            return np.zeros(self.window_size * 5 + 3)

        # Market features: OHLCV data
        market_window = self.data[
            self.current_step - self.window_size:self.current_step
        ].flatten()

        # Portfolio features
        current_price = self.data[self.current_step, 3]  # Close price
        portfolio_value = self.balance + self.position * current_price

        portfolio_features = np.array([
            self.position,
            self.balance,
            portfolio_value
        ])

        return np.concatenate([market_window, portfolio_features])

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute one step in the environment.

        Args:
            action: 0=Hold, 1=Buy, 2=Sell (or continuous position change)

        Returns:
            observation, reward, done, info
        """
        if self.current_step >= self.max_steps:
            return self._get_observation(), 0.0, True, {}

        current_price = self.data[self.current_step, 3]
        next_price = self.data[self.current_step + 1, 3]

        # Execute action
        old_portfolio_value = self.balance + self.position * current_price

        if action == 1:  # Buy
            tradeable_amount = self.balance / current_price
            trade_amount = min(tradeable_amount, self.max_position)
            cost = trade_amount * current_price * (1 + self.transaction_cost)

            if cost <= self.balance:
                self.balance -= cost
                self.position += trade_amount
                self.entry_price = current_price

        elif action == 2:  # Sell
            proceeds = self.position * current_price * (1 - self.transaction_cost)
            self.balance += proceeds
            self.position = 0.0

        # Market moves to next step
        self.current_step += 1

        # Calculate reward
        new_portfolio_value = self.balance + self.position * next_price
        reward = self._calculate_reward(old_portfolio_value, new_portfolio_value)

        # Track metrics
        self.portfolio_values.append(new_portfolio_value)
        self.actions_taken.append(action)
        self.rewards_history.append(reward)

        done = self.current_step >= self.max_steps

        info = {
            'portfolio_value': new_portfolio_value,
            'position': self.position,
            'balance': self.balance,
            'price': next_price,
        }

        observation = self._get_observation()

        return observation, reward, done, info

    def _calculate_reward(self, old_value: float, new_value: float) -> float:
        """Calculate reward based on specified reward type."""
        if self.reward_type == 'simple_pnl':
            return (new_value - old_value) / old_value

        elif self.reward_type == 'sharpe':
            # Approximate Sharpe ratio on recent performance
            if len(self.rewards_history) > 1:
                recent_returns = self.rewards_history[-20:]
                if len(recent_returns) > 1:
                    mean_return = np.mean(recent_returns)
                    std_return = np.std(recent_returns)
                    return mean_return / (std_return + 1e-8)
            return (new_value - old_value) / old_value

        elif self.reward_type in ['sortino', 'calmar']:
            # Downside risk metrics
            recent_returns = self.rewards_history[-20:]
            downside_returns = [r for r in recent_returns if r < 0]
            if downside_returns:
                downside_std = np.std(downside_returns)
                return np.mean(recent_returns) / (downside_std + 1e-8)
            return (new_value - old_value) / old_value

        return (new_value - old_value) / old_value


# ============================================================================
# Q-LEARNING TRADER (TABULAR)
# ============================================================================

class QLearningTrader:
    """
    Tabular Q-learning agent for discrete trading environment.

    Q(s,a) = Q(s,a) + α[r + γ max(Q(s',a')) - Q(s,a)]
    """

    def __init__(
        self,
        state_discretizer,
        n_actions: int = 3,
        learning_rate: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 1.0,
        epsilon_decay: float = 0.995,
    ):
        """
        Initialize Q-learning trader.

        Args:
            state_discretizer: Function to discretize continuous states
            n_actions: Number of discrete actions
            learning_rate: Learning rate (alpha)
            gamma: Discount factor
            epsilon: Exploration rate
            epsilon_decay: Epsilon decay rate
        """
        self.state_discretizer = state_discretizer
        self.n_actions = n_actions
        self.alpha = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay

        # Q-table: dictionary for sparse representation
        self.q_table = {}
        self.visit_counts = {}

    def _discretize_state(self, observation: np.ndarray) -> Tuple:
        """Convert continuous observation to discrete state."""
        return self.state_discretizer(observation)

    def select_action(self, observation: np.ndarray, training: bool = True) -> int:
        """
        Epsilon-greedy action selection.

        Args:
            observation: Current state
            training: If True, use epsilon-greedy; else use greedy

        Returns:
            Selected action (0, 1, or 2)
        """
        state = self._discretize_state(observation)

        if training and np.random.random() < self.epsilon:
            return np.random.randint(0, self.n_actions)

        # Greedy action
        if state not in self.q_table:
            return np.random.randint(0, self.n_actions)

        q_values = self.q_table[state]
        return np.argmax(q_values)

    def update(
        self,
        observation: np.ndarray,
        action: int,
        reward: float,
        next_observation: np.ndarray,
        done: bool,
    ):
        """Update Q-table using Q-learning update rule."""
        state = self._discretize_state(observation)
        next_state = self._discretize_state(next_observation)

        # Initialize Q-values if state not seen
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.n_actions)
            self.visit_counts[state] = np.zeros(self.n_actions)

        if next_state not in self.q_table:
            self.q_table[next_state] = np.zeros(self.n_actions)

        # Q-learning update
        old_q = self.q_table[state][action]
        max_next_q = np.max(self.q_table[next_state]) if not done else 0
        new_q = old_q + self.alpha * (reward + self.gamma * max_next_q - old_q)

        self.q_table[state][action] = new_q
        self.visit_counts[state][action] += 1

        # Decay epsilon
        self.epsilon *= self.epsilon_decay
        self.epsilon = max(0.01, self.epsilon)

    def train_episode(self, env: TradingEnvironment) -> float:
        """Run one training episode."""
        observation = env.reset()
        episode_reward = 0
        done = False

        while not done:
            action = self.select_action(observation, training=True)
            next_observation, reward, done, _ = env.step(action)

            self.update(observation, action, reward, next_observation, done)

            episode_reward += reward
            observation = next_observation

        return episode_reward


# ============================================================================
# DEEP Q-NETWORK (DQN)
# ============================================================================

if TORCH_AVAILABLE:
    class QNetwork(nn.Module):
        """Neural network for Q-value approximation."""

        def __init__(
            self,
            input_size: int,
            hidden_size: int = 128,
            n_actions: int = 3,
        ):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, n_actions),
            )

        def forward(self, x):
            return self.net(x)


    class DQNTrader:
        """
        Deep Q-Network agent for continuous state spaces.

        Features:
        - Experience replay buffer
        - Target network for stability
        - Double DQN for overestimation reduction
        """

        def __init__(
            self,
            input_size: int,
            n_actions: int = 3,
            hidden_size: int = 128,
            learning_rate: float = 0.001,
            gamma: float = 0.95,
            epsilon: float = 1.0,
            epsilon_decay: float = 0.995,
            buffer_size: int = 10000,
            batch_size: int = 32,
            update_frequency: int = 4,
        ):
            """Initialize DQN agent."""
            self.input_size = input_size
            self.n_actions = n_actions
            self.gamma = gamma
            self.epsilon = epsilon
            self.epsilon_decay = epsilon_decay
            self.batch_size = batch_size
            self.update_frequency = update_frequency

            # Networks
            self.device = torch.device('cpu')
            self.q_network = QNetwork(input_size, hidden_size, n_actions).to(self.device)
            self.target_network = QNetwork(input_size, hidden_size, n_actions).to(self.device)
            self.target_network.load_state_dict(self.q_network.state_dict())

            # Optimizer
            self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

            # Experience replay buffer
            self.replay_buffer = deque(maxlen=buffer_size)
            self.step_count = 0

        def select_action(self, observation: np.ndarray, training: bool = True) -> int:
            """Epsilon-greedy action selection."""
            if training and np.random.random() < self.epsilon:
                return np.random.randint(0, self.n_actions)

            # Greedy action
            with torch.no_grad():
                state_tensor = torch.FloatTensor(observation).unsqueeze(0).to(self.device)
                q_values = self.q_network(state_tensor)
                return q_values.argmax(dim=1).item()

        def remember(
            self,
            observation: np.ndarray,
            action: int,
            reward: float,
            next_observation: np.ndarray,
            done: bool,
        ):
            """Store experience in replay buffer."""
            self.replay_buffer.append((observation, action, reward, next_observation, done))

        def learn(self):
            """Learn from a batch of experiences."""
            if len(self.replay_buffer) < self.batch_size:
                return

            # Sample batch
            batch_indices = np.random.choice(len(self.replay_buffer), self.batch_size, replace=False)
            batch = [self.replay_buffer[i] for i in batch_indices]

            observations, actions, rewards, next_observations, dones = zip(*batch)

            # Convert to tensors
            obs_tensor = torch.FloatTensor(np.array(observations)).to(self.device)
            actions_tensor = torch.LongTensor(np.array(actions)).to(self.device)
            rewards_tensor = torch.FloatTensor(np.array(rewards)).to(self.device)
            next_obs_tensor = torch.FloatTensor(np.array(next_observations)).to(self.device)
            dones_tensor = torch.FloatTensor(np.array(dones)).to(self.device)

            # Compute Q-values
            q_values = self.q_network(obs_tensor)
            q_action_values = q_values.gather(1, actions_tensor.unsqueeze(1)).squeeze(1)

            # Compute target Q-values (Double DQN)
            with torch.no_grad():
                next_q_values = self.q_network(next_obs_tensor)
                best_next_actions = next_q_values.argmax(dim=1)

                target_q_values = self.target_network(next_obs_tensor)
                max_target_q_values = target_q_values.gather(1, best_next_actions.unsqueeze(1)).squeeze(1)

                targets = rewards_tensor + self.gamma * max_target_q_values * (1 - dones_tensor)

            # Loss and optimization
            loss = nn.functional.mse_loss(q_action_values, targets)

            self.optimizer.zero_grad()
            loss.backward()
            nn.functional.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
            self.optimizer.step()

            # Update epsilon
            self.epsilon *= self.epsilon_decay
            self.epsilon = max(0.01, self.epsilon)

            # Update target network periodically
            self.step_count += 1
            if self.step_count % 1000 == 0:
                self.target_network.load_state_dict(self.q_network.state_dict())

        def train_episode(self, env: TradingEnvironment) -> float:
            """Run one training episode."""
            observation = env.reset()
            episode_reward = 0
            done = False

            while not done:
                action = self.select_action(observation, training=True)
                next_observation, reward, done, _ = env.step(action)

                self.remember(observation, action, reward, next_observation, done)
                self.learn()

                episode_reward += reward
                observation = next_observation

            return episode_reward


# ============================================================================
# POLICY GRADIENT METHODS
# ============================================================================

if TORCH_AVAILABLE:
    class PolicyNetwork(nn.Module):
        """Policy network for actor-critic methods."""

        def __init__(
            self,
            input_size: int,
            hidden_size: int = 128,
            n_actions: int = 3,
        ):
            super().__init__()
            self.shared = nn.Sequential(
                nn.Linear(input_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
            )

            # Actor head: policy (logits)
            self.actor = nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, n_actions),
            )

            # Critic head: value function
            self.critic = nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, 1),
            )

        def forward(self, x):
            shared_repr = self.shared(x)
            action_logits = self.actor(shared_repr)
            state_value = self.critic(shared_repr)
            return action_logits, state_value


    class ActorCriticTrader:
        """
        Actor-Critic agent for policy gradient learning.

        Combines:
        - Policy (actor) that outputs action probabilities
        - Value function (critic) that estimates state values
        - Advantage-based updates
        """

        def __init__(
            self,
            input_size: int,
            n_actions: int = 3,
            hidden_size: int = 128,
            learning_rate: float = 0.001,
            gamma: float = 0.95,
            gae_lambda: float = 0.95,
            entropy_coef: float = 0.01,
        ):
            """Initialize Actor-Critic agent."""
            self.input_size = input_size
            self.n_actions = n_actions
            self.gamma = gamma
            self.gae_lambda = gae_lambda
            self.entropy_coef = entropy_coef

            # Network
            self.device = torch.device('cpu')
            self.policy_net = PolicyNetwork(input_size, hidden_size, n_actions).to(self.device)

            # Optimizer
            self.optimizer = optim.Adam(self.policy_net.parameters(), lr=learning_rate)

            # Trajectory storage
            self.trajectory = []
            self.step_count = 0

        def select_action(self, observation: np.ndarray) -> int:
            """Select action based on current policy."""
            with torch.no_grad():
                obs_tensor = torch.FloatTensor(observation).unsqueeze(0).to(self.device)
                action_logits, _ = self.policy_net(obs_tensor)

                probabilities = torch.softmax(action_logits, dim=1)
                action = torch.multinomial(probabilities, 1).item()

                return action

        def store_transition(
            self,
            observation: np.ndarray,
            action: int,
            reward: float,
            next_observation: np.ndarray,
            done: bool,
        ):
            """Store transition for later update."""
            self.trajectory.append({
                'obs': observation,
                'action': action,
                'reward': reward,
                'next_obs': next_observation,
                'done': done,
            })

        def update(self):
            """Update policy and value function from trajectory."""
            if not self.trajectory:
                return

            # Compute returns and advantages
            returns = []
            advantages = []

            # Get value estimates
            obs_list = np.array([t['obs'] for t in self.trajectory])
            obs_tensor = torch.FloatTensor(obs_list).to(self.device)

            with torch.no_grad():
                _, state_values = self.policy_net(obs_tensor)
                state_values = state_values.squeeze(-1).cpu().numpy()

            # Compute GAE (Generalized Advantage Estimation)
            next_value = 0
            gae = 0

            for t in reversed(range(len(self.trajectory))):
                transition = self.trajectory[t]
                value = state_values[t]

                delta = transition['reward'] + self.gamma * next_value * (1 - transition['done']) - value
                gae = delta + self.gamma * self.gae_lambda * (1 - transition['done']) * gae

                returns.insert(0, gae + value)
                advantages.insert(0, gae)

                next_value = value

            # Normalize advantages
            advantages = np.array(advantages)
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

            # Update policy
            actions_tensor = torch.LongTensor(
                np.array([t['action'] for t in self.trajectory])
            ).to(self.device)
            returns_tensor = torch.FloatTensor(returns).to(self.device)
            advantages_tensor = torch.FloatTensor(advantages).to(self.device)

            action_logits, state_values_pred = self.policy_net(obs_tensor)
            state_values_pred = state_values_pred.squeeze(-1)

            # Policy loss (with entropy regularization)
            log_probs = torch.log_softmax(action_logits, dim=1)
            selected_log_probs = log_probs.gather(1, actions_tensor.unsqueeze(1)).squeeze(1)

            entropy = -(torch.softmax(action_logits, dim=1) * log_probs).sum(dim=1).mean()

            policy_loss = -(selected_log_probs * advantages_tensor).mean()

            # Value loss
            value_loss = nn.functional.mse_loss(state_values_pred, returns_tensor)

            # Total loss
            total_loss = policy_loss + 0.5 * value_loss - self.entropy_coef * entropy

            self.optimizer.zero_grad()
            total_loss.backward()
            nn.functional.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)
            self.optimizer.step()

            # Clear trajectory
            self.trajectory = []
            self.step_count += 1

        def train_episode(self, env: TradingEnvironment) -> float:
            """Run one training episode."""
            observation = env.reset()
            episode_reward = 0
            done = False

            while not done:
                action = self.select_action(observation)
                next_observation, reward, done, _ = env.step(action)

                self.store_transition(observation, action, reward, next_observation, done)

                episode_reward += reward
                observation = next_observation

            self.update()

            return episode_reward


# ============================================================================
# REWARD SHAPING FOR TRADING
# ============================================================================

class RewardShaper:
    """
    Reward shaping utilities for trading RL agents.

    Techniques:
    - Simple P&L
    - Risk-adjusted returns (Sharpe, Sortino)
    - Drawdown penalties
    - Trade cost penalties
    - Stability bonuses
    """

    @staticmethod
    def simple_pnl(
        old_portfolio_value: float,
        new_portfolio_value: float,
    ) -> float:
        """Simple percentage change reward."""
        return (new_portfolio_value - old_portfolio_value) / old_portfolio_value

    @staticmethod
    def sharpe_reward(
        returns: List[float],
        risk_free_rate: float = 0.02,
    ) -> float:
        """Sharpe ratio-based reward."""
        if len(returns) < 2:
            return 0.0

        excess_returns = np.array(returns) - risk_free_rate / 252
        return np.mean(excess_returns) / (np.std(excess_returns) + 1e-8)

    @staticmethod
    def sortino_reward(
        returns: List[float],
        risk_free_rate: float = 0.02,
    ) -> float:
        """Sortino ratio-based reward (downside deviation)."""
        if len(returns) < 2:
            return 0.0

        excess_returns = np.array(returns) - risk_free_rate / 252
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0:
            return np.mean(excess_returns)

        downside_std = np.std(downside_returns)
        return np.mean(excess_returns) / (downside_std + 1e-8)

    @staticmethod
    def calmar_reward(
        returns: List[float],
        lookback: int = 252,
    ) -> float:
        """Calmar ratio-based reward (return / max drawdown)."""
        if len(returns) < lookback:
            returns = returns
        else:
            returns = returns[-lookback:]

        cumulative_returns = np.cumprod(1 + np.array(returns)) - 1
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = (cumulative_returns - running_max) / (running_max + 1e-8)
        max_drawdown = np.min(drawdown)

        total_return = cumulative_returns[-1] if len(cumulative_returns) > 0 else 0

        return total_return / (abs(max_drawdown) + 1e-8)

    @staticmethod
    def penalized_reward(
        pnl: float,
        transaction_costs: float,
        max_drawdown: float,
        n_trades: int,
        alpha: float = 1.0,
        beta: float = 0.1,
        gamma: float = 0.5,
    ) -> float:
        """
        Reward with penalties for costs and risk.

        Reward = alpha * PnL - beta * transaction_costs - gamma * max_drawdown
        """
        return alpha * pnl - beta * transaction_costs - gamma * max_drawdown

    @staticmethod
    def stability_bonus(
        returns: List[float],
        target_volatility: float = 0.15,
    ) -> float:
        """Bonus for stable returns close to target volatility."""
        if len(returns) < 2:
            return 0.0

        current_volatility = np.std(returns)
        volatility_diff = abs(current_volatility - target_volatility)

        # Bonus decreases with volatility difference
        return 1.0 / (1.0 + volatility_diff)


# ============================================================================
# TRAINING UTILITIES
# ============================================================================

def train_agent(
    agent,
    env: TradingEnvironment,
    n_episodes: int = 100,
    verbose: bool = True,
) -> List[float]:
    """
    Train a RL agent on the trading environment.

    Args:
        agent: RL agent (QLearningTrader, DQNTrader, or ActorCriticTrader)
        env: TradingEnvironment instance
        n_episodes: Number of training episodes
        verbose: Print progress

    Returns:
        List of episode rewards
    """
    episode_rewards = []

    for episode in range(n_episodes):
        episode_reward = agent.train_episode(env)
        episode_rewards.append(episode_reward)

        if verbose and (episode + 1) % 10 == 0:
            avg_reward = np.mean(episode_rewards[-10:])
            print(f"Episode {episode + 1}/{n_episodes} - Avg Reward: {avg_reward:.4f}")

    return episode_rewards


def evaluate_agent(
    agent,
    env: TradingEnvironment,
    n_episodes: int = 10,
) -> Dict[str, float]:
    """
    Evaluate a trained RL agent.

    Args:
        agent: Trained RL agent
        env: TradingEnvironment instance
        n_episodes: Number of evaluation episodes

    Returns:
        Dictionary with evaluation metrics
    """
    total_returns = []
    total_pnls = []
    max_drawdowns = []

    for _ in range(n_episodes):
        observation = env.reset()
        done = False

        while not done:
            action = agent.select_action(observation, training=False)
            observation, _, done, info = env.step(action)

        # Calculate metrics
        portfolio_values = np.array(env.portfolio_values)
        returns = np.diff(portfolio_values) / portfolio_values[:-1]
        pnl = portfolio_values[-1] - portfolio_values[0]

        # Max drawdown
        cumulative = np.cumprod(1 + returns) - 1
        running_max = np.maximum.accumulate(cumulative)
        max_dd = np.min((cumulative - running_max) / (running_max + 1e-8))

        total_returns.append(returns)
        total_pnls.append(pnl)
        max_drawdowns.append(max_dd)

    return {
        'avg_return': np.mean(np.concatenate(total_returns)),
        'avg_pnl': np.mean(total_pnls),
        'avg_max_drawdown': np.mean(max_drawdowns),
        'total_return': np.mean([pnl / env.initial_balance for pnl in total_pnls]),
    }


if __name__ == '__main__':
    print("Reinforcement Learning for Trading Module")
    print("=" * 50)

    # Example usage (requires data)
    print("\nAvailable classes:")
    print("- TradingEnvironment: Gym-like trading environment")
    print("- QLearningTrader: Tabular Q-learning")
    print("- DQNTrader: Deep Q-Network (requires PyTorch)")
    print("- ActorCriticTrader: Actor-Critic (requires PyTorch)")
    print("- RewardShaper: Trading reward engineering")
