"""
Pairs Trading and Cointegration Analysis Module

This module implements comprehensive pairs trading strategies using:
- Engle-Granger (EG) cointegration test
- Johansen cointegration test
- Distance method for pair selection
- Correlation method for pair selection
- Spread calculation with z-score normalization
- Half-life estimation of mean reversion
- Entry/exit signal generation
- Portfolio construction with risk management

Author: Financial Apps Team
Date: 2025
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from typing import Tuple, Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')


class PairsTrading:
    """
    Comprehensive pairs trading and cointegration analysis framework.
    """

    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize the PairsTrading class.

        Parameters:
        -----------
        confidence_level : float
            Confidence level for statistical tests (default: 0.95)
        """
        self.confidence_level = confidence_level
        self.critical_values = {
            'eg': {0.90: -3.37, 0.95: -3.37, 0.99: -4.03},  # Engle-Granger critical values
            'johansen_trace': {0.90: 13.429, 0.95: 15.495, 0.99: 19.935},
            'johansen_eigenvalue': {0.90: 12.297, 0.95: 14.264, 0.99: 18.52}
        }

    # ============================================================================
    # PAIR SELECTION METHODS
    # ============================================================================

    def distance_method(self, prices1: np.ndarray, prices2: np.ndarray,
                       lookback: int = 60) -> float:
        """
        Distance method: Sum of squared price differences.

        Pairs with lower normalized distances are better candidates for mean reversion.

        Formula:
        Distance = sum((P1_t - P2_t)^2) for t in lookback period
        Normalized Distance = Distance / mean(P2)

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1
        prices2 : np.ndarray
            Price series for asset 2
        lookback : int
            Lookback period for distance calculation

        Returns:
        --------
        float
            Normalized distance metric
        """
        # Use only recent prices
        p1 = prices1[-lookback:]
        p2 = prices2[-lookback:]

        # Scale prices to same magnitude for fair comparison
        p1_scaled = p1 / p1[0]
        p2_scaled = p2 / p2[0]

        # Calculate sum of squared differences
        distance = np.sum((p1_scaled - p2_scaled) ** 2)

        # Normalize by mean price of asset 2
        normalized_distance = distance / np.mean(p2_scaled)

        return normalized_distance

    def correlation_method(self, prices1: np.ndarray, prices2: np.ndarray,
                          lookback: int = 60) -> float:
        """
        Correlation method: Pearson correlation coefficient.

        Higher correlations indicate better pairs for mean reversion strategies.

        Formula:
        r = cov(P1, P2) / (std(P1) * std(P2))

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1
        prices2 : np.ndarray
            Price series for asset 2
        lookback : int
            Lookback period for correlation calculation

        Returns:
        --------
        float
            Correlation coefficient
        """
        # Use only recent prices
        returns1 = np.log(prices1[-lookback:] / prices1[-lookback-1:-1])
        returns2 = np.log(prices2[-lookback:] / prices2[-lookback-1:-1])

        correlation = np.corrcoef(returns1, returns2)[0, 1]

        return correlation

    # ============================================================================
    # COINTEGRATION TESTS
    # ============================================================================

    def engle_granger_test(self, prices1: np.ndarray, prices2: np.ndarray) -> Dict:
        """
        Engle-Granger two-step cointegration test.

        Step 1: Regress Y_t = alpha + beta * X_t + epsilon_t
        Step 2: Test for unit root in residuals using ADF test

        Formula:
        1. Estimate: Y_t = alpha + beta * X_t + u_t
        2. Test H0: u_t has unit root vs H1: u_t is I(0) (stationary)
        3. Test statistic: ADF test on residuals

        Critical values (MacKinnon):
        - 90%: -3.37
        - 95%: -3.37
        - 99%: -4.03

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1 (dependent variable)
        prices2 : np.ndarray
            Price series for asset 2 (independent variable)

        Returns:
        --------
        dict
            Results including test statistic, p-value, hedge ratio, and cointegration status
        """
        # Ensure same length
        min_len = min(len(prices1), len(prices2))
        y = prices1[-min_len:]
        x = prices2[-min_len:]

        # Step 1: OLS regression
        x_with_const = np.vstack([np.ones(len(x)), x]).T
        beta = np.linalg.lstsq(x_with_const, y, rcond=None)[0]

        alpha = beta[0]
        hedge_ratio = beta[1]

        # Calculate residuals (spread)
        residuals = y - (alpha + hedge_ratio * x)

        # Step 2: ADF test on residuals
        adf_stat = self._adf_test(residuals)

        # Determine cointegration
        critical_value = self.critical_values['eg'][0.95]
        is_cointegrated = adf_stat < critical_value

        # Calculate p-value (approximate)
        p_value = self._adf_pvalue(adf_stat, len(residuals))

        return {
            'test_statistic': adf_stat,
            'p_value': p_value,
            'critical_value': critical_value,
            'is_cointegrated': is_cointegrated,
            'alpha': alpha,
            'hedge_ratio': hedge_ratio,
            'residuals': residuals,
            'test_name': 'Engle-Granger'
        }

    def johansen_test(self, prices: np.ndarray, k_ar_diff: int = 1) -> Dict:
        """
        Johansen cointegration test for multivariate systems.

        Tests for the number of cointegrating relationships in a system.

        Formula:
        1. Estimate VAR model: dX_t = alpha * beta' * X_t-1 + epsilon_t
        2. Test rank of cointegrating matrix
        3. Trace test: H0: r <= r0 vs H1: r > r0
        4. Eigenvalue test: H0: r = r0 vs H1: r = r0 + 1

        Test statistics:
        - Trace = -T * sum(ln(1 - lambda_i)) for i > r
        - Eigenvalue = -T * ln(1 - lambda_{r+1})

        Parameters:
        -----------
        prices : np.ndarray
            Array of shape (n_obs, n_assets) with price series
        k_ar_diff : int
            Number of AR lags in differenced VAR model

        Returns:
        --------
        dict
            Results including trace statistic, eigenvalues, and cointegrating relationships
        """
        # Ensure we have at least 2 assets
        if prices.ndim == 1:
            prices = prices.reshape(-1, 1)
        if prices.shape[1] < 2:
            raise ValueError("Need at least 2 price series for Johansen test")

        # Estimate VAR model parameters
        n_obs = prices.shape[0]
        n_assets = prices.shape[1]

        # Calculate differences
        dprices = np.diff(prices, axis=0)

        # Lagged prices (for cointegrating relationship)
        prices_lag = prices[:-1, :]

        # Create regression: dP = A * P_lag + B * dP_lag + error
        x = prices_lag
        y = dprices

        # OLS to get residuals
        x_aug = np.hstack([np.ones((x.shape[0], 1)), x])
        beta = np.linalg.lstsq(x_aug, y, rcond=None)[0][1:]  # Exclude constant

        residuals = y - x @ beta

        # Estimate covariance matrix
        cov_matrix = (residuals.T @ residuals) / n_obs

        # Calculate eigenvalues
        eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)
        eigenvalues = np.real(eigenvalues)
        eigenvalues = np.sort(eigenvalues)[::-1]  # Sort descending

        # Calculate trace statistic
        trace_stat = -n_obs * np.sum([np.log(1 - eig) if eig < 1 else 0
                                       for eig in eigenvalues])

        # Determine number of cointegrating relationships
        critical_value_trace = self.critical_values['johansen_trace'][0.95]
        n_cointegrating = np.sum([-n_obs * np.log(1 - eig) > critical_value_trace
                                   if eig < 1 else False
                                   for eig in eigenvalues])

        return {
            'test_statistic': trace_stat,
            'eigenvalues': eigenvalues,
            'eigenvectors': eigenvectors,
            'critical_value': critical_value_trace,
            'n_cointegrating': n_cointegrating,
            'is_cointegrated': n_cointegrating > 0,
            'test_name': 'Johansen'
        }

    def _adf_test(self, series: np.ndarray, lags: int = 1) -> float:
        """
        Augmented Dickey-Fuller test statistic.

        Tests for unit root: H0: series has unit root vs H1: series is stationary

        Formula:
        Model: dY_t = alpha + beta*t + gamma*Y_t-1 + sum(delta_i * dY_t-i) + epsilon_t
        Test statistic: t-ratio of gamma coefficient

        Parameters:
        -----------
        series : np.ndarray
            Time series to test
        lags : int
            Number of lagged differences to include

        Returns:
        --------
        float
            Test statistic
        """
        diffs = np.diff(series)
        lag1 = series[:-1]

        # Create regression matrix with lags
        x = np.vstack([np.ones(len(lag1)), lag1,
                      np.arange(len(lag1))]).T  # constant, lag, trend

        # Add lagged differences
        for i in range(1, lags + 1):
            if i < len(diffs):
                x = np.hstack([x, diffs[-(len(lag1)-i):-(i) if i > 0 else None, np.newaxis]])

        # OLS regression
        y = diffs[:len(x)]
        x = x[:len(y)]

        beta = np.linalg.lstsq(x, y, rcond=None)[0]
        residuals = y - x @ beta
        sigma2 = np.sum(residuals ** 2) / (len(residuals) - len(beta))

        # Calculate t-statistic for unit root coefficient (gamma)
        var_beta = sigma2 * np.linalg.inv(x.T @ x).diagonal()
        t_stat = beta[1] / np.sqrt(var_beta[1])

        return t_stat

    def _adf_pvalue(self, t_stat: float, n: int) -> float:
        """
        Approximate p-value for ADF test statistic.

        Uses MacKinnon approximation for critical values.

        Parameters:
        -----------
        t_stat : float
            ADF test statistic
        n : int
            Number of observations

        Returns:
        --------
        float
            Approximate p-value
        """
        # MacKinnon approximate p-value formula
        # Simplified version for demonstration
        if t_stat < -4.0:
            return 0.01
        elif t_stat < -3.5:
            return 0.025
        elif t_stat < -3.0:
            return 0.05
        elif t_stat < -2.5:
            return 0.10
        else:
            return 0.90

    # ============================================================================
    # SPREAD ANALYSIS
    # ============================================================================

    def calculate_spread(self, prices1: np.ndarray, prices2: np.ndarray,
                        hedge_ratio: Optional[float] = None) -> Tuple[np.ndarray, float]:
        """
        Calculate the spread (Z_t) between two cointegrated series.

        Formula:
        Spread_t = Y_t - beta * X_t (if beta provided)
        or
        Spread_t = Y_t - beta_OLS * X_t (if beta not provided)

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1 (Y)
        prices2 : np.ndarray
            Price series for asset 2 (X)
        hedge_ratio : float, optional
            Hedge ratio (beta). If None, estimated via OLS

        Returns:
        --------
        tuple
            (spread array, hedge_ratio used)
        """
        min_len = min(len(prices1), len(prices2))
        y = prices1[-min_len:]
        x = prices2[-min_len:]

        if hedge_ratio is None:
            # Estimate via OLS
            x_with_const = np.vstack([np.ones(len(x)), x]).T
            beta = np.linalg.lstsq(x_with_const, y, rcond=None)[0]
            hedge_ratio = beta[1]

        spread = y - hedge_ratio * x

        return spread, hedge_ratio

    def calculate_zscore(self, spread: np.ndarray, lookback: int = 20) -> np.ndarray:
        """
        Calculate z-score of the spread for normalized signal generation.

        Formula:
        Z_score_t = (Spread_t - mean(Spread)) / std(Spread)

        Parameters:
        -----------
        spread : np.ndarray
            Spread series
        lookback : int
            Lookback period for mean and std calculation

        Returns:
        --------
        np.ndarray
            Z-score series
        """
        zscore = np.zeros(len(spread))

        for i in range(lookback, len(spread)):
            mean_spread = np.mean(spread[i-lookback:i])
            std_spread = np.std(spread[i-lookback:i])

            if std_spread > 0:
                zscore[i] = (spread[i] - mean_spread) / std_spread
            else:
                zscore[i] = 0

        return zscore

    # ============================================================================
    # HALF-LIFE ESTIMATION
    # ============================================================================

    def estimate_halflife(self, spread: np.ndarray, method: str = 'ar1') -> float:
        """
        Estimate half-life of mean reversion using AR(1) model or log-decay.

        Formula (AR1 method):
        dS_t = lambda * S_t-1 + epsilon_t (demeaned)
        Half-life = ln(2) / (-ln(1 + lambda)) = ln(2) / (-lambda) when lambda is small

        Formula (Log-decay method):
        ln(|Spread_t|) = a + b*t
        Half-life = ln(2) / |b|

        Parameters:
        -----------
        spread : np.ndarray
            Spread series
        method : str
            'ar1' or 'log_decay'

        Returns:
        --------
        float
            Half-life in periods (days if daily data)
        """
        # Demean spread
        spread_demeaned = spread - np.mean(spread)

        if method == 'ar1':
            # AR(1) regression: dS_t = lambda * S_t-1
            x = spread_demeaned[:-1].reshape(-1, 1)
            y = np.diff(spread_demeaned)

            # OLS
            lambda_coef = np.linalg.lstsq(x, y, rcond=None)[0][0]

            # Half-life
            if lambda_coef < 0:
                halflife = np.log(2) / (-lambda_coef)
            else:
                halflife = np.inf

        elif method == 'log_decay':
            # Exponential decay: |S_t| = a * exp(-b*t)
            # ln(|S_t|) = ln(a) - b*t
            t = np.arange(len(spread)).reshape(-1, 1)

            # Avoid log of zero
            abs_spread = np.abs(spread) + 1e-8
            y = np.log(abs_spread)

            # OLS with constant
            x = np.hstack([np.ones((len(t), 1)), t])
            beta = np.linalg.lstsq(x, y, rcond=None)[0]
            b_coef = beta[1]

            # Half-life
            if b_coef < 0:
                halflife = np.inf
            else:
                halflife = np.log(2) / b_coef

        else:
            raise ValueError("Method must be 'ar1' or 'log_decay'")

        return float(halflife)

    # ============================================================================
    # SIGNAL GENERATION
    # ============================================================================

    def generate_signals(self, zscore: np.ndarray, entry_threshold: float = 2.0,
                        exit_threshold: float = 0.5) -> Dict[str, np.ndarray]:
        """
        Generate entry and exit signals based on z-score thresholds.

        Strategy:
        - Long entry: z-score < -entry_threshold (spread too low, mean reversion up)
        - Short entry: z-score > entry_threshold (spread too high, mean reversion down)
        - Exit long: z-score > exit_threshold
        - Exit short: z-score < -exit_threshold

        Parameters:
        -----------
        zscore : np.ndarray
            Z-score series
        entry_threshold : float
            Z-score threshold for entry signals (default: 2.0)
        exit_threshold : float
            Z-score threshold for exit signals (default: 0.5)

        Returns:
        --------
        dict
            Dictionary with signal arrays: 'long_entry', 'short_entry', 'exit'
        """
        long_entry = (zscore < -entry_threshold).astype(int)
        short_entry = (zscore > entry_threshold).astype(int)

        # Exit when crossing zero or hitting exit threshold
        exit_signal = (np.abs(zscore) < exit_threshold).astype(int)

        return {
            'long_entry': long_entry,
            'short_entry': short_entry,
            'exit': exit_signal,
            'zscore': zscore
        }

    # ============================================================================
    # PORTFOLIO CONSTRUCTION
    # ============================================================================

    def construct_portfolio(self, prices1: np.ndarray, prices2: np.ndarray,
                           hedge_ratio: float, position_size: float = 1.0) -> Dict:
        """
        Construct pairs trading portfolio with position sizing.

        Strategy construction:
        1. Long position_size units of Asset 1
        2. Short (position_size * hedge_ratio) units of Asset 2

        This creates a market-neutral spread trading position.

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1
        prices2 : np.ndarray
            Price series for asset 2
        hedge_ratio : float
            Hedge ratio (beta from cointegration regression)
        position_size : float
            Size of long position in asset 1

        Returns:
        --------
        dict
            Portfolio configuration and metrics
        """
        # Current prices
        current_price1 = prices1[-1]
        current_price2 = prices2[-1]

        # Position sizes
        long_units = position_size
        short_units = hedge_ratio * position_size

        # Portfolio value
        long_value = long_units * current_price1
        short_value = short_units * current_price2
        net_value = long_value - short_value

        # Hedge ratio validation
        ratio_check = long_value / short_value if short_value != 0 else np.inf

        return {
            'asset1': {
                'position': 'long',
                'units': long_units,
                'price': current_price1,
                'value': long_value
            },
            'asset2': {
                'position': 'short',
                'units': short_units,
                'price': current_price2,
                'value': short_value
            },
            'net_value': net_value,
            'hedge_ratio': hedge_ratio,
            'value_ratio': ratio_check,
            'is_neutral': abs(ratio_check - 1.0) < 0.05
        }

    def backtest_strategy(self, prices1: np.ndarray, prices2: np.ndarray,
                         signals: Dict, hedge_ratio: float,
                         initial_capital: float = 10000.0) -> Dict:
        """
        Backtest pairs trading strategy with given signals.

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1
        prices2 : np.ndarray
            Price series for asset 2
        signals : dict
            Dictionary containing 'long_entry', 'short_entry', 'exit' signals
        hedge_ratio : float
            Hedge ratio
        initial_capital : float
            Initial capital for the strategy

        Returns:
        --------
        dict
            Backtest results including returns, Sharpe ratio, max drawdown
        """
        min_len = min(len(prices1), len(prices2))
        p1 = prices1[-min_len:]
        p2 = prices2[-min_len:]

        # Initialize
        position = 0  # 0: flat, 1: long, -1: short
        portfolio_value = np.zeros(min_len)
        portfolio_value[0] = initial_capital

        long_entry = signals['long_entry'][-min_len:]
        short_entry = signals['short_entry'][-min_len:]
        exit_sig = signals['exit'][-min_len:]

        # Simulate trading
        for i in range(1, min_len):
            # Current portfolio value
            if position == 1:
                # Long spread: long asset1, short asset2
                spread_value = p1[i] - hedge_ratio * p2[i]
                prev_spread_value = p1[i-1] - hedge_ratio * p2[i-1]
                pnl = (spread_value - prev_spread_value)
            elif position == -1:
                # Short spread
                spread_value = p1[i] - hedge_ratio * p2[i]
                prev_spread_value = p1[i-1] - hedge_ratio * p2[i-1]
                pnl = -(spread_value - prev_spread_value)
            else:
                pnl = 0

            portfolio_value[i] = portfolio_value[i-1] + pnl

            # Update position
            if exit_sig[i]:
                position = 0
            elif long_entry[i]:
                position = 1
            elif short_entry[i]:
                position = -1

        # Calculate metrics
        returns = np.diff(portfolio_value) / portfolio_value[:-1]
        total_return = (portfolio_value[-1] - initial_capital) / initial_capital

        # Sharpe ratio (assuming 252 trading days)
        sharpe_ratio = np.mean(returns) / (np.std(returns) + 1e-8) * np.sqrt(252)

        # Max drawdown
        cummax = np.maximum.accumulate(portfolio_value)
        drawdown = (portfolio_value - cummax) / cummax
        max_drawdown = np.min(drawdown)

        # Win rate
        winning_returns = returns[returns > 0]
        win_rate = len(winning_returns) / len(returns) if len(returns) > 0 else 0

        return {
            'portfolio_value': portfolio_value,
            'returns': returns,
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'final_value': portfolio_value[-1]
        }

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def summary_statistics(self, prices1: np.ndarray, prices2: np.ndarray,
                          spread: np.ndarray) -> Dict:
        """
        Calculate summary statistics for pairs trading analysis.

        Parameters:
        -----------
        prices1 : np.ndarray
            Price series for asset 1
        prices2 : np.ndarray
            Price series for asset 2
        spread : np.ndarray
            Spread series

        Returns:
        --------
        dict
            Summary statistics
        """
        returns1 = np.log(prices1[1:] / prices1[:-1])
        returns2 = np.log(prices2[1:] / prices2[:-1])
        spread_changes = np.diff(spread)

        return {
            'asset1': {
                'mean_return': np.mean(returns1),
                'std_return': np.std(returns1),
                'sharpe': np.mean(returns1) / (np.std(returns1) + 1e-8),
                'correlation_with_spread': np.corrcoef(returns1, spread_changes[1:])[0, 1]
            },
            'asset2': {
                'mean_return': np.mean(returns2),
                'std_return': np.std(returns2),
                'sharpe': np.mean(returns2) / (np.std(returns2) + 1e-8),
                'correlation_with_spread': np.corrcoef(returns2, spread_changes[1:])[0, 1]
            },
            'spread': {
                'mean': np.mean(spread),
                'std': np.std(spread),
                'skewness': stats.skew(spread),
                'kurtosis': stats.kurtosis(spread),
                'min': np.min(spread),
                'max': np.max(spread)
            },
            'pair_metrics': {
                'correlation': np.corrcoef(returns1, returns2)[0, 1],
                'beta': np.cov(returns1, returns2)[0, 1] / (np.std(returns2) ** 2)
            }
        }


# ============================================================================
# EXAMPLE USAGE AND TESTING
# ============================================================================

def create_synthetic_cointegrated_series(n_periods: int = 500,
                                        seed: int = 42) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create synthetic cointegrated price series for testing.

    Parameters:
    -----------
    n_periods : int
        Number of periods to generate
    seed : int
        Random seed for reproducibility

    Returns:
    --------
    tuple
        (prices1, prices2) cointegrated series
    """
    np.random.seed(seed)

    # Common stochastic trend (I(1))
    trend = np.cumsum(np.random.normal(0, 1, n_periods))

    # Cointegrating relationship: Y = 1.5*X + stationary error
    error1 = np.cumsum(np.random.normal(0, 0.1, n_periods))  # I(1)
    error2 = np.random.normal(0, 0.5, n_periods)  # I(0)

    prices1 = trend + error1
    prices2 = (prices1 - error2) / 1.5 + np.random.normal(0, 1, n_periods)

    # Ensure positive prices
    prices1 = np.exp(prices1 / 100 + 5)
    prices2 = np.exp(prices2 / 100 + 5)

    return prices1, prices2


if __name__ == '__main__':
    # Example: Run pairs trading analysis
    print("=" * 80)
    print("PAIRS TRADING AND COINTEGRATION ANALYSIS")
    print("=" * 80)

    # Generate synthetic data
    print("\n1. Generating synthetic cointegrated price series...")
    prices1, prices2 = create_synthetic_cointegrated_series(n_periods=500)

    # Initialize
    pt = PairsTrading(confidence_level=0.95)

    # Pair selection
    print("\n2. Pair Selection Metrics:")
    dist = pt.distance_method(prices1, prices2, lookback=60)
    corr = pt.correlation_method(prices1, prices2, lookback=60)
    print(f"   Distance metric: {dist:.4f}")
    print(f"   Correlation: {corr:.4f}")

    # Cointegration tests
    print("\n3. Engle-Granger Cointegration Test:")
    eg_result = pt.engle_granger_test(prices1, prices2)
    print(f"   Test statistic: {eg_result['test_statistic']:.4f}")
    print(f"   Critical value: {eg_result['critical_value']:.4f}")
    print(f"   Cointegrated: {eg_result['is_cointegrated']}")
    print(f"   Hedge ratio: {eg_result['hedge_ratio']:.4f}")

    print("\n4. Johansen Cointegration Test:")
    prices_array = np.column_stack([prices1, prices2])
    joh_result = pt.johansen_test(prices_array)
    print(f"   Trace statistic: {joh_result['test_statistic']:.4f}")
    print(f"   Critical value: {joh_result['critical_value']:.4f}")
    print(f"   Cointegrating relationships: {joh_result['n_cointegrating']}")

    # Spread analysis
    print("\n5. Spread Analysis:")
    spread, hedge_ratio = pt.calculate_spread(prices1, prices2)
    zscore = pt.calculate_zscore(spread, lookback=20)
    print(f"   Hedge ratio: {hedge_ratio:.4f}")
    print(f"   Spread mean: {np.mean(spread):.4f}")
    print(f"   Spread std: {np.std(spread):.4f}")

    # Half-life estimation
    print("\n6. Half-life of Mean Reversion:")
    halflife_ar1 = pt.estimate_halflife(spread, method='ar1')
    halflife_log = pt.estimate_halflife(spread, method='log_decay')
    print(f"   Half-life (AR1): {halflife_ar1:.2f} periods")
    print(f"   Half-life (Log-decay): {halflife_log:.2f} periods")

    # Signal generation
    print("\n7. Signal Generation:")
    signals = pt.generate_signals(zscore, entry_threshold=2.0, exit_threshold=0.5)
    n_long = np.sum(signals['long_entry'])
    n_short = np.sum(signals['short_entry'])
    n_exit = np.sum(signals['exit'])
    print(f"   Long entry signals: {n_long}")
    print(f"   Short entry signals: {n_short}")
    print(f"   Exit signals: {n_exit}")

    # Portfolio construction
    print("\n8. Portfolio Construction:")
    portfolio = pt.construct_portfolio(prices1, prices2, hedge_ratio, position_size=1.0)
    print(f"   Long position (Asset 1): {portfolio['asset1']['units']:.4f} units @ {portfolio['asset1']['price']:.2f}")
    print(f"   Short position (Asset 2): {portfolio['asset2']['units']:.4f} units @ {portfolio['asset2']['price']:.2f}")
    print(f"   Market neutral: {portfolio['is_neutral']}")

    # Backtest
    print("\n9. Backtest Results:")
    backtest = pt.backtest_strategy(prices1, prices2, signals, hedge_ratio, initial_capital=10000)
    print(f"   Total return: {backtest['total_return']*100:.2f}%")
    print(f"   Sharpe ratio: {backtest['sharpe_ratio']:.4f}")
    print(f"   Max drawdown: {backtest['max_drawdown']*100:.2f}%")
    print(f"   Win rate: {backtest['win_rate']*100:.2f}%")
    print(f"   Final portfolio value: ${backtest['final_value']:.2f}")

    # Summary statistics
    print("\n10. Summary Statistics:")
    stats_dict = pt.summary_statistics(prices1, prices2, spread)
    print(f"    Asset 1 Sharpe: {stats_dict['asset1']['sharpe']:.4f}")
    print(f"    Asset 2 Sharpe: {stats_dict['asset2']['sharpe']:.4f}")
    print(f"    Pair correlation: {stats_dict['pair_metrics']['correlation']:.4f}")

    print("\n" + "=" * 80)
