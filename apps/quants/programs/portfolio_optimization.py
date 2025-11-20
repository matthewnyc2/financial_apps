"""
Portfolio Optimization Module

Implements multiple portfolio optimization methodologies:
1. Mean-Variance Optimization (Markowitz)
2. Black-Litterman Model
3. Risk Parity Allocation
4. Hierarchical Risk Parity (HRP)
5. Kelly Criterion Position Sizing

Author: Financial Quants Team
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize, LinearConstraint, Bounds
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
from typing import Dict, Tuple, List, Optional, Union
import warnings

warnings.filterwarnings('ignore')


class PortfolioOptimizer:
    """Base class for portfolio optimization methods."""

    def __init__(self, returns: Union[np.ndarray, pd.DataFrame],
                 asset_names: Optional[List[str]] = None):
        """
        Initialize portfolio optimizer.

        Args:
            returns: (n_assets, n_periods) array or DataFrame of returns
            asset_names: List of asset names
        """
        if isinstance(returns, pd.DataFrame):
            self.returns = returns.values
            self.asset_names = returns.columns.tolist()
        else:
            self.returns = np.asarray(returns)
            self.asset_names = asset_names or [f'Asset_{i}' for i in range(self.returns.shape[0])]

        self.n_assets = self.returns.shape[0]
        self.mean_returns = np.mean(self.returns, axis=1)
        self.cov_matrix = np.cov(self.returns)
        self.corr_matrix = np.corrcoef(self.returns)

    def _validate_weights(self, weights: np.ndarray) -> bool:
        """Validate portfolio weights sum to 1 and are non-negative."""
        return np.allclose(weights.sum(), 1.0) and np.all(weights >= -1e-9)

    def portfolio_stats(self, weights: np.ndarray,
                       risk_free_rate: float = 0.02) -> Dict[str, float]:
        """Calculate portfolio statistics."""
        returns = np.dot(weights, self.mean_returns)
        variance = np.dot(weights, np.dot(self.cov_matrix, weights))
        std_dev = np.sqrt(variance)
        sharpe = (returns - risk_free_rate) / std_dev if std_dev > 0 else 0

        return {
            'return': returns,
            'volatility': std_dev,
            'variance': variance,
            'sharpe_ratio': sharpe
        }


class MeanVarianceOptimizer(PortfolioOptimizer):
    """
    Mean-Variance Optimization (Markowitz)

    Finds portfolio weights that minimize variance for target return,
    or maximize Sharpe ratio.
    """

    def optimize(self, target_return: Optional[float] = None,
                 risk_free_rate: float = 0.02,
                 long_only: bool = True) -> Dict:
        """
        Optimize portfolio weights.

        Args:
            target_return: Target return (if None, maximize Sharpe ratio)
            risk_free_rate: Risk-free rate for Sharpe calculation
            long_only: If True, enforce weights >= 0

        Returns:
            Dictionary with optimal weights and statistics
        """
        def objective(w):
            if target_return is None:
                # Maximize Sharpe ratio
                ret = np.dot(w, self.mean_returns)
                var = np.dot(w, np.dot(self.cov_matrix, w))
                std = np.sqrt(var)
                if std < 1e-9:
                    return 1000
                return -(ret - risk_free_rate) / std
            else:
                # Minimize variance for target return
                return np.dot(w, np.dot(self.cov_matrix, w))

        def return_constraint(w):
            if target_return is None:
                return 0
            return np.dot(w, self.mean_returns) - target_return

        # Initial guess: equal weight
        w0 = np.ones(self.n_assets) / self.n_assets

        # Constraints
        constraints = {'type': 'eq', 'fun': lambda w: w.sum() - 1.0}
        if target_return is not None:
            constraints = [
                constraints,
                {'type': 'eq', 'fun': return_constraint}
            ]

        # Bounds
        bounds = [(0, 1) if long_only else (-1, 1) for _ in range(self.n_assets)]

        # Optimize
        result = minimize(objective, w0, method='SLSQP', bounds=bounds,
                         constraints=constraints, options={'ftol': 1e-9})

        weights = result.x
        weights = weights / weights.sum()  # Normalize

        stats = self.portfolio_stats(weights, risk_free_rate)

        return {
            'weights': dict(zip(self.asset_names, weights)),
            'optimal_weights': weights,
            'return': stats['return'],
            'volatility': stats['volatility'],
            'sharpe_ratio': stats['sharpe_ratio'],
            'success': result.success
        }

    def efficient_frontier(self, n_points: int = 50,
                          risk_free_rate: float = 0.02) -> Dict:
        """Generate efficient frontier."""
        min_ret = self.mean_returns.min()
        max_ret = self.mean_returns.max()
        target_returns = np.linspace(min_ret, max_ret, n_points)

        frontier = {'returns': [], 'volatilities': [], 'weights': []}

        for target_ret in target_returns:
            result = self.optimize(target_ret, risk_free_rate)
            frontier['returns'].append(result['return'])
            frontier['volatilities'].append(result['volatility'])
            frontier['weights'].append(result['optimal_weights'])

        return frontier


class BlackLittermanOptimizer(PortfolioOptimizer):
    """
    Black-Litterman Model

    Combines market equilibrium returns with investor views.
    """

    def __init__(self, returns: Union[np.ndarray, pd.DataFrame],
                 market_cap_weights: Optional[np.ndarray] = None,
                 risk_free_rate: float = 0.02,
                 asset_names: Optional[List[str]] = None):
        """
        Initialize Black-Litterman optimizer.

        Args:
            returns: Historical returns
            market_cap_weights: Market capitalization weights (if None, equal weight)
            risk_free_rate: Risk-free rate
            asset_names: Asset names
        """
        super().__init__(returns, asset_names)
        self.risk_free_rate = risk_free_rate

        if market_cap_weights is None:
            self.market_cap_weights = np.ones(self.n_assets) / self.n_assets
        else:
            self.market_cap_weights = np.asarray(market_cap_weights)

        # Estimate market implied returns
        self.market_implied_returns = self._reverse_optimize()

    def _reverse_optimize(self, risk_aversion: float = 3.0) -> np.ndarray:
        """
        Reverse optimize to get market-implied returns.

        π = risk_aversion * Σ * w_market
        """
        excess_returns = self.market_cap_weights @ self.cov_matrix
        implied_returns = risk_aversion * excess_returns + self.risk_free_rate
        return implied_returns

    def update_with_views(self, views: List[Dict],
                         confidence: float = 0.5) -> Dict:
        """
        Update portfolio with investor views.

        Args:
            views: List of dicts with keys 'assets', 'return'
                  Example: [{'assets': [0, 1], 'return': 0.05}]
            confidence: Confidence level in views (0-1)

        Returns:
            Optimized weights incorporating views
        """
        # Posterior returns incorporating views
        posterior_returns = self.market_implied_returns.copy()

        # Simple view incorporation: weighted average
        if views:
            for view in views:
                asset_indices = view['assets']
                view_return = view['return']
                posterior_returns[asset_indices] = (
                    confidence * view_return +
                    (1 - confidence) * posterior_returns[asset_indices]
                )

        # Optimize using posterior returns
        def objective(w):
            ret = np.dot(w, posterior_returns)
            var = np.dot(w, np.dot(self.cov_matrix, w))
            std = np.sqrt(var) if var > 0 else 1e-9
            return -(ret - self.risk_free_rate) / std

        w0 = np.ones(self.n_assets) / self.n_assets
        constraints = {'type': 'eq', 'fun': lambda w: w.sum() - 1.0}
        bounds = [(0, 1) for _ in range(self.n_assets)]

        result = minimize(objective, w0, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        weights = result.x / result.x.sum()
        stats = self.portfolio_stats(weights, self.risk_free_rate)

        return {
            'weights': dict(zip(self.asset_names, weights)),
            'optimal_weights': weights,
            'return': stats['return'],
            'volatility': stats['volatility'],
            'sharpe_ratio': stats['sharpe_ratio'],
            'posterior_returns': dict(zip(self.asset_names, posterior_returns))
        }


class RiskParityOptimizer(PortfolioOptimizer):
    """
    Risk Parity Allocation

    Allocates capital so each asset contributes equally to portfolio risk.
    """

    def optimize(self, max_iterations: int = 1000,
                 tolerance: float = 1e-6) -> Dict:
        """
        Find risk parity weights using inverse volatility method.

        Returns:
            Dictionary with optimal weights and statistics
        """
        # Initial approximation: inverse volatility
        volatilities = np.sqrt(np.diag(self.cov_matrix))
        weights = 1.0 / volatilities
        weights = weights / weights.sum()

        # Iterative refinement for exact risk parity
        for iteration in range(max_iterations):
            # Risk contribution
            marginal_contrib = self.cov_matrix @ weights
            risk_contrib = weights * marginal_contrib / np.sqrt(weights @ self.cov_matrix @ weights)

            # Update weights to equalize risk contribution
            weights = weights * (1.0 / risk_contrib) ** 0.5
            weights = weights / weights.sum()

            # Check convergence
            target_rc = 1.0 / self.n_assets
            if np.allclose(risk_contrib, target_rc, atol=tolerance):
                break

        # Verify risk contributions are equal
        portfolio_var = weights @ self.cov_matrix @ weights
        marginal_contrib = self.cov_matrix @ weights
        risk_contrib = weights * marginal_contrib / np.sqrt(portfolio_var)

        stats = self.portfolio_stats(weights)

        return {
            'weights': dict(zip(self.asset_names, weights)),
            'optimal_weights': weights,
            'return': stats['return'],
            'volatility': stats['volatility'],
            'risk_contributions': dict(zip(self.asset_names, risk_contrib)),
            'iterations': iteration + 1
        }


class HierarchicalRiskParityOptimizer(PortfolioOptimizer):
    """
    Hierarchical Risk Parity (HRP)

    Uses hierarchical clustering on correlations to construct portfolio.
    """

    def optimize(self) -> Dict:
        """
        Construct HRP portfolio.

        Returns:
            Dictionary with optimal weights and statistics
        """
        # 1. Generate distance matrix from correlation
        distance_matrix = np.sqrt((1 - self.corr_matrix) / 2)

        # 2. Hierarchical clustering
        condensed_dist = squareform(distance_matrix)
        self.linkage_matrix = linkage(condensed_dist, method='ward')

        # 3. Recursive portfolio construction
        weights = self._recursive_bisection(self.linkage_matrix)
        weights = weights / weights.sum()

        stats = self.portfolio_stats(weights)

        return {
            'weights': dict(zip(self.asset_names, weights)),
            'optimal_weights': weights,
            'return': stats['return'],
            'volatility': stats['volatility'],
            'linkage_matrix': self.linkage_matrix
        }

    def _recursive_bisection(self, linkage_matrix: np.ndarray) -> np.ndarray:
        """
        Recursively bisect clusters and allocate capital.
        """
        n_clusters = linkage_matrix.shape[0] + 1
        weights = np.ones(self.n_assets)

        def _bisect_clusters(cluster_id: int, weight: float = 1.0):
            """Recursively allocate weights."""
            # Leaf node (asset)
            if cluster_id < n_clusters:
                weights[cluster_id] = weight
                return

            # Internal node: split into two sub-clusters
            cluster_idx = cluster_id - n_clusters
            left_id = int(linkage_matrix[cluster_idx, 0])
            right_id = int(linkage_matrix[cluster_idx, 1])

            # Get assets in each cluster
            left_assets = self._get_cluster_assets(left_id)
            right_assets = self._get_cluster_assets(right_id)

            # Allocate inversely proportional to volatility
            left_vol = self._cluster_volatility(left_assets)
            right_vol = self._cluster_volatility(right_assets)

            total_vol = left_vol + right_vol
            left_weight = weight * (right_vol / total_vol)
            right_weight = weight * (left_vol / total_vol)

            _bisect_clusters(left_id, left_weight)
            _bisect_clusters(right_id, right_weight)

        _bisect_clusters(len(linkage_matrix) + len(self.asset_names) - 1)
        return weights

    def _get_cluster_assets(self, cluster_id: int) -> List[int]:
        """Get asset indices in a cluster."""
        n_clusters = self.n_assets
        if cluster_id < n_clusters:
            return [cluster_id]

        cluster_idx = cluster_id - n_clusters
        left_id = int(self.linkage_matrix[cluster_idx, 0])
        right_id = int(self.linkage_matrix[cluster_idx, 1])

        return self._get_cluster_assets(left_id) + self._get_cluster_assets(right_id)

    def _cluster_volatility(self, asset_indices: List[int]) -> float:
        """Calculate cluster volatility."""
        if not asset_indices:
            return 1.0

        indices = np.ix_(asset_indices, asset_indices)
        cluster_cov = self.cov_matrix[indices]

        if len(asset_indices) == 1:
            return np.sqrt(cluster_cov[0, 0])

        # Equal-weighted cluster
        equal_weights = np.ones(len(asset_indices)) / len(asset_indices)
        cluster_var = equal_weights @ cluster_cov @ equal_weights
        return np.sqrt(cluster_var)


class KellyCriterionOptimizer(PortfolioOptimizer):
    """
    Kelly Criterion Position Sizing

    Determines optimal position sizing for maximum long-term growth.
    """

    def optimize(self, win_prob: Optional[np.ndarray] = None,
                 expected_payoff: Optional[np.ndarray] = None,
                 max_position: float = 0.25) -> Dict:
        """
        Calculate Kelly Criterion position sizes.

        Args:
            win_prob: Probability of positive return per asset (if None, estimate from returns)
            expected_payoff: Expected payoff per asset
            max_position: Maximum position size (0-1)

        Returns:
            Dictionary with Kelly-optimal weights
        """
        if win_prob is None:
            # Estimate from returns: proportion of positive periods
            win_prob = np.mean(self.returns > 0, axis=1)

        if expected_payoff is None:
            # Estimate from returns: mean return / std dev (Sharpe-like metric)
            expected_payoff = self.mean_returns

        # Kelly Criterion: f = (p * b - q) / b
        # Simplified for portfolio: f = (p * E[R]) / σ²
        kelly_fractions = np.zeros(self.n_assets)

        for i in range(self.n_assets):
            p = max(0.01, min(0.99, win_prob[i]))  # Avoid 0 or 1
            q = 1 - p

            if expected_payoff[i] > 0:
                # Full Kelly criterion
                b = expected_payoff[i] / (self.returns[i].std() if self.returns[i].std() > 0 else 1)
                kelly = (p * b - q) / b if b > 0 else 0
            else:
                kelly = 0

            # Apply constraints
            kelly_fractions[i] = max(0, min(kelly, max_position))

        # Normalize to portfolio weights
        if kelly_fractions.sum() > 0:
            weights = kelly_fractions / kelly_fractions.sum()
        else:
            weights = np.ones(self.n_assets) / self.n_assets

        stats = self.portfolio_stats(weights)

        return {
            'weights': dict(zip(self.asset_names, weights)),
            'optimal_weights': weights,
            'return': stats['return'],
            'volatility': stats['volatility'],
            'kelly_fractions': dict(zip(self.asset_names, kelly_fractions)),
            'win_probabilities': dict(zip(self.asset_names, win_prob))
        }

    def expected_value_ratio(self, weights: np.ndarray) -> float:
        """
        Calculate expected growth rate (log of (1 + portfolio return)).
        """
        portfolio_returns = self.returns.T @ weights  # Portfolio return each period
        growth_rates = np.log(1 + portfolio_returns)
        return np.mean(growth_rates)


def demonstrate_optimization():
    """Demonstrate all optimization methods."""

    # Generate sample data
    np.random.seed(42)
    n_assets = 5
    n_periods = 252

    # Create correlated returns
    cov_matrix = np.array([
        [0.04, 0.02, 0.01, 0.005, 0.001],
        [0.02, 0.06, 0.02, 0.01, 0.005],
        [0.01, 0.02, 0.03, 0.015, 0.01],
        [0.005, 0.01, 0.015, 0.05, 0.02],
        [0.001, 0.005, 0.01, 0.02, 0.07]
    ])

    returns = np.random.multivariate_normal(
        mean=np.array([0.08, 0.10, 0.06, 0.12, 0.15]),
        cov=cov_matrix,
        size=n_periods
    ).T

    asset_names = ['Asset_A', 'Asset_B', 'Asset_C', 'Asset_D', 'Asset_E']

    print("=" * 80)
    print("PORTFOLIO OPTIMIZATION DEMONSTRATION")
    print("=" * 80)

    # 1. Mean-Variance Optimization
    print("\n1. MEAN-VARIANCE OPTIMIZATION (Markowitz)")
    print("-" * 80)
    mv = MeanVarianceOptimizer(returns, asset_names)
    result = mv.optimize()
    print(f"Optimal Weights: {result['weights']}")
    print(f"Expected Return: {result['return']:.4f}")
    print(f"Volatility: {result['volatility']:.4f}")
    print(f"Sharpe Ratio: {result['sharpe_ratio']:.4f}")

    # 2. Black-Litterman
    print("\n2. BLACK-LITTERMAN MODEL")
    print("-" * 80)
    bl = BlackLittermanOptimizer(returns, asset_names=asset_names)
    views = [
        {'assets': [0, 1], 'return': 0.12}
    ]
    result = bl.update_with_views(views, confidence=0.6)
    print(f"Optimal Weights: {result['weights']}")
    print(f"Expected Return: {result['return']:.4f}")
    print(f"Volatility: {result['volatility']:.4f}")
    print(f"Sharpe Ratio: {result['sharpe_ratio']:.4f}")

    # 3. Risk Parity
    print("\n3. RISK PARITY ALLOCATION")
    print("-" * 80)
    rp = RiskParityOptimizer(returns, asset_names)
    result = rp.optimize()
    print(f"Optimal Weights: {result['weights']}")
    print(f"Risk Contributions: {result['risk_contributions']}")
    print(f"Expected Return: {result['return']:.4f}")
    print(f"Volatility: {result['volatility']:.4f}")

    # 4. Hierarchical Risk Parity
    print("\n4. HIERARCHICAL RISK PARITY (HRP)")
    print("-" * 80)
    hrp = HierarchicalRiskParityOptimizer(returns, asset_names)
    result = hrp.optimize()
    print(f"Optimal Weights: {result['weights']}")
    print(f"Expected Return: {result['return']:.4f}")
    print(f"Volatility: {result['volatility']:.4f}")

    # 5. Kelly Criterion
    print("\n5. KELLY CRITERION SIZING")
    print("-" * 80)
    kc = KellyCriterionOptimizer(returns, asset_names)
    result = kc.optimize()
    print(f"Optimal Weights: {result['weights']}")
    print(f"Kelly Fractions: {result['kelly_fractions']}")
    print(f"Win Probabilities: {result['win_probabilities']}")
    print(f"Expected Return: {result['return']:.4f}")
    print(f"Volatility: {result['volatility']:.4f}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    demonstrate_optimization()
