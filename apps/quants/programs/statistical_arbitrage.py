"""
Statistical Arbitrage Methods for Quantitative Trading
========================================================

This module implements key statistical arbitrage strategies including:
1. Pairs Trading with Cointegration Testing
2. Basket Arbitrage
3. Index Arbitrage
4. Statistical Mean Reversion
5. Distance-based Relative Value Trading

Author: Quantitative Research Team
Date: 2025
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

# Optional pandas import (for some advanced features)
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


class PairsTrading:
    """
    Pairs Trading Strategy using Cointegration Testing
    =====================================================

    Mathematical Foundation:
    - If two securities are cointegrated, they follow a long-run equilibrium relationship
    - Spread: Z_t = log(P1_t) - β*log(P2_t)
    - Where β is determined by OLS regression of log prices
    - When spread deviates from mean, we enter positions expecting mean reversion

    Formula:
        Z_t = Y_t - β*X_t
        Where:
        - Y_t, X_t are log prices of two assets
        - β = Cov(Y_t, X_t) / Var(X_t)
        - Mean reversion: E[Z_t - μ] → 0
    """

    def __init__(self, lookback_period: int = 252):
        """
        Initialize Pairs Trading Strategy

        Parameters:
        -----------
        lookback_period : int
            Number of historical periods for regression (default: 1 year of trading days)
        """
        self.lookback_period = lookback_period
        self.beta = None
        self.hedge_ratio = None
        self.mean_spread = None
        self.std_spread = None

    def calculate_hedge_ratio(self, price1: np.ndarray, price2: np.ndarray) -> float:
        """
        Calculate hedge ratio using OLS regression

        Formula: β = Cov(Price1, Price2) / Var(Price2)

        Parameters:
        -----------
        price1, price2 : np.ndarray
            Price series for both assets

        Returns:
        --------
        float : Hedge ratio (beta coefficient)
        """
        log_price1 = np.log(price1[-self.lookback_period:])
        log_price2 = np.log(price2[-self.lookback_period:])

        # OLS: log_price1 = alpha + beta * log_price2 + error
        X = np.column_stack([np.ones(len(log_price2)), log_price2])
        y = log_price1

        # β = (X'X)^(-1) X'y
        coef = np.linalg.lstsq(X, y, rcond=None)[0]
        self.beta = coef[1]
        self.hedge_ratio = coef[1]

        return self.beta

    def calculate_spread(self, price1: np.ndarray, price2: np.ndarray) -> np.ndarray:
        """
        Calculate the spread (stationary combination)

        Formula: Spread_t = log(Price1_t) - β * log(Price2_t)

        Parameters:
        -----------
        price1, price2 : np.ndarray
            Price series

        Returns:
        --------
        np.ndarray : Spread series
        """
        if self.hedge_ratio is None:
            self.calculate_hedge_ratio(price1, price2)

        log_price1 = np.log(price1)
        log_price2 = np.log(price2)

        spread = log_price1 - self.hedge_ratio * log_price2
        self.mean_spread = np.mean(spread[-self.lookback_period:])
        self.std_spread = np.std(spread[-self.lookback_period:])

        return spread

    def adf_test(self, series: np.ndarray) -> Dict:
        """
        Augmented Dickey-Fuller Test for Stationarity

        H0: Series has unit root (non-stationary)
        H1: Series is stationary

        Test Statistic: τ = (β̂ - 1) / SE(β̂)

        Parameters:
        -----------
        series : np.ndarray
            Time series to test

        Returns:
        --------
        Dict : Test results with p-value
        """
        try:
            from statsmodels.tsa.stattools import adfuller
        except ImportError:
            # Manual ADF approximation if statsmodels not available
            return self._manual_adf_test(series)

        adf_result = adfuller(series, autolag='AIC')

        return {
            'test_statistic': adf_result[0],
            'p_value': adf_result[1],
            'critical_values': adf_result[4],
            'is_stationary': adf_result[1] < 0.05
        }

    def _manual_adf_test(self, series: np.ndarray) -> Dict:
        """
        Manual ADF test implementation (simplified)
        """
        y = series[1:]
        x = series[:-1]
        n = len(y)

        # Add constant
        X = np.column_stack([np.ones(n), x])

        # OLS estimation
        coef = np.linalg.lstsq(X, y, rcond=None)[0]
        residuals = y - X @ coef
        rss = np.sum(residuals**2)
        sigma2 = rss / (n - 2)

        # t-statistic for β coefficient
        var_covar = sigma2 * np.linalg.inv(X.T @ X)
        t_stat = (coef[1] - 1) / np.sqrt(var_covar[1, 1])

        # Approximate p-value (crude)
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), n - 2))

        return {
            'test_statistic': t_stat,
            'p_value': p_value,
            'is_stationary': abs(t_stat) > 2.0  # Rough threshold
        }

    def generate_signals(self, spread: np.ndarray, entry_threshold: float = 2.0,
                        exit_threshold: float = 0.5) -> np.ndarray:
        """
        Generate trading signals based on spread mean reversion

        Logic:
        - Entry when |Z - μ| > entry_threshold * σ
        - Exit when |Z - μ| < exit_threshold * σ

        Parameters:
        -----------
        spread : np.ndarray
            Spread series
        entry_threshold : float
            Number of std devs for entry (default: 2σ)
        exit_threshold : float
            Number of std devs for exit (default: 0.5σ)

        Returns:
        --------
        np.ndarray : Signal array (1=long asset1, -1=short asset1, 0=no position)
        """
        z_score = (spread - self.mean_spread) / self.std_spread
        signals = np.zeros(len(spread))

        for i in range(len(z_score)):
            # Long spread when it's too negative (mean reversion)
            if z_score[i] < -entry_threshold:
                signals[i] = 1
            # Short spread when it's too positive
            elif z_score[i] > entry_threshold:
                signals[i] = -1
            # Exit positions
            elif abs(z_score[i]) < exit_threshold:
                signals[i] = 0
            # Maintain previous position
            else:
                signals[i] = signals[i-1] if i > 0 else 0

        return signals


class BasketArbitrage:
    """
    Basket Arbitrage Strategy
    =========================

    Mathematical Foundation:
    - Detects when basket of securities trades at discount/premium to index
    - Formula for synthetic index: I_t = Σ(w_i * P_i,t)
    - Arbitrage opportunity when: |Index_actual - Index_synthetic| > threshold

    Key Formulas:
        Basket Value: V = Σ(w_i * S_i)
        Where:
        - w_i = weights from index composition
        - S_i = spot prices of securities

        Mispricing: M = Index_price - Basket_value
        When M > transaction_costs: Sell index, buy basket (cash-and-carry)
        When M < -transaction_costs: Buy index, sell basket (reverse)
    """

    def __init__(self, weights: np.ndarray, transaction_cost_pct: float = 0.005):
        """
        Initialize Basket Arbitrage Strategy

        Parameters:
        -----------
        weights : np.ndarray
            Weights of securities in the basket
        transaction_cost_pct : float
            Transaction cost as percentage (default: 0.5%)
        """
        self.weights = weights / np.sum(weights)  # Normalize weights
        self.transaction_cost_pct = transaction_cost_pct
        self.synthetic_prices = None
        self.mispricing = None

    def calculate_synthetic_index(self, prices: np.ndarray) -> np.ndarray:
        """
        Calculate synthetic index value

        Formula: I_t^synthetic = Σ(w_i * P_i,t)

        Parameters:
        -----------
        prices : np.ndarray
            Price matrix (n_periods, n_securities)

        Returns:
        --------
        np.ndarray : Synthetic index prices
        """
        self.synthetic_prices = prices @ self.weights
        return self.synthetic_prices

    def calculate_mispricing(self, index_prices: np.ndarray,
                            synthetic_prices: np.ndarray) -> np.ndarray:
        """
        Calculate index vs synthetic basket mispricing

        Formula: Mispricing_pct = (Index_price - Synthetic_price) / Synthetic_price

        Parameters:
        -----------
        index_prices : np.ndarray
            Actual index prices
        synthetic_prices : np.ndarray
            Synthetic basket prices

        Returns:
        --------
        np.ndarray : Mispricing percentage
        """
        self.mispricing = (index_prices - synthetic_prices) / synthetic_prices
        return self.mispricing

    def generate_signals(self, mispricing: np.ndarray,
                        threshold: float = None) -> np.ndarray:
        """
        Generate arbitrage signals

        Logic:
        - If mispricing > threshold: Sell overpriced index, buy basket
        - If mispricing < -threshold: Buy underpriced index, sell basket

        Parameters:
        -----------
        mispricing : np.ndarray
            Mispricing percentage array
        threshold : float
            Threshold for arbitrage opportunity (default: transaction_cost * 2)

        Returns:
        --------
        np.ndarray : Signal array (1=long basket, -1=short basket, 0=no trade)
        """
        if threshold is None:
            threshold = self.transaction_cost_pct * 2

        signals = np.zeros(len(mispricing))
        signals[mispricing > threshold] = -1  # Sell index, buy basket
        signals[mispricing < -threshold] = 1  # Buy index, sell basket

        return signals

    def calculate_pnl(self, index_prices: np.ndarray,
                     component_prices: np.ndarray,
                     signals: np.ndarray) -> np.ndarray:
        """
        Calculate P&L from basket arbitrage positions

        Parameters:
        -----------
        index_prices : np.ndarray
            Index price series
        component_prices : np.ndarray
            Component prices matrix
        signals : np.ndarray
            Trading signals

        Returns:
        --------
        np.ndarray : Cumulative P&L
        """
        n_periods = len(index_prices)
        pnl = np.zeros(n_periods)

        for t in range(1, n_periods):
            if signals[t-1] != 0:
                # Cost of transaction
                transaction_cost = self.transaction_cost_pct * abs(index_prices[t-1])

                # Profit from index-basket spread mean reversion
                basket_return = (component_prices[t] @ self.weights -
                               component_prices[t-1] @ self.weights)
                index_return = index_prices[t] - index_prices[t-1]

                # P&L = -1 * (index return) + 1 * (basket return)
                pnl[t] = signals[t-1] * (basket_return - index_return) - transaction_cost

        return np.cumsum(pnl)


class IndexArbitrage:
    """
    Index Arbitrage (Cash-and-Carry / Reverse)
    ==========================================

    Mathematical Foundation:
    - Exploits pricing differences between futures and spot index
    - Cost-of-Carry Model: F_t = S_t * exp((r - q) * T)

    Key Formulas:
        Futures Price: F = S * e^((r-q)*T)
        Where:
        - S = spot index price
        - r = risk-free rate
        - q = dividend yield
        - T = time to maturity

        Cash-and-Carry Arbitrage:
        Profit = F - S*e^((r-q)*T) > 0 → Buy spot, sell futures

        Cost of Carry = r*S*T - q*S*T (in dollars)
    """

    def __init__(self, risk_free_rate: float = 0.05, dividend_yield: float = 0.02,
                 transaction_cost_pct: float = 0.003):
        """
        Initialize Index Arbitrage Strategy

        Parameters:
        -----------
        risk_free_rate : float
            Annual risk-free rate (default: 5%)
        dividend_yield : float
            Annual dividend yield (default: 2%)
        transaction_cost_pct : float
            Transaction cost as percentage (default: 0.3%)
        """
        self.r = risk_free_rate
        self.q = dividend_yield
        self.transaction_cost_pct = transaction_cost_pct
        self.net_carry_cost = risk_free_rate - dividend_yield

    def theoretical_futures_price(self, spot_price: float,
                                  time_to_maturity: float) -> float:
        """
        Calculate theoretical futures price using Cost-of-Carry Model

        Formula: F = S * e^((r-q)*T)

        Parameters:
        -----------
        spot_price : float
            Current spot index price
        time_to_maturity : float
            Time to futures maturity in years

        Returns:
        --------
        float : Theoretical futures price
        """
        return spot_price * np.exp(self.net_carry_cost * time_to_maturity)

    def identify_arbitrage_opportunity(self, spot_price: float,
                                       futures_price: float,
                                       time_to_maturity: float) -> Dict:
        """
        Identify arbitrage opportunity and direction

        Parameters:
        -----------
        spot_price : float
            Spot index price
        futures_price : float
            Futures contract price
        time_to_maturity : float
            Time to maturity in years

        Returns:
        --------
        Dict : Opportunity details with profit calculation
        """
        theoretical_price = self.theoretical_futures_price(spot_price, time_to_maturity)
        mispricing = futures_price - theoretical_price

        # Transaction cost for round trip (buy spot, sell futures or vice versa)
        round_trip_cost = 2 * self.transaction_cost_pct * spot_price

        opportunity = {
            'theoretical_price': theoretical_price,
            'actual_price': futures_price,
            'mispricing': mispricing,
            'mispricing_pct': (mispricing / theoretical_price) * 100,
            'round_trip_cost': round_trip_cost,
            'net_profit': abs(mispricing) - round_trip_cost
        }

        # Determine strategy
        if mispricing > round_trip_cost:
            opportunity['strategy'] = 'Reverse Cash-and-Carry (buy futures, sell spot)'
        elif mispricing < -round_trip_cost:
            opportunity['strategy'] = 'Cash-and-Carry (sell futures, buy spot)'
        else:
            opportunity['strategy'] = 'No arbitrage'

        return opportunity

    def carry_cost_pnl(self, spot_price: float, position_size: int,
                       holding_period_years: float) -> float:
        """
        Calculate P&L from financing cost of holding spot position

        Formula: PnL = Position_Size * Spot * [(r-q) * T]

        Parameters:
        -----------
        spot_price : float
            Index price
        position_size : int
            Number of units (e.g., value in dollars)
        holding_period_years : float
            Holding period in years

        Returns:
        --------
        float : P&L from carry costs
        """
        carry_cost = position_size * spot_price * self.net_carry_cost * holding_period_years
        return carry_cost

    def dividend_yield_pnl(self, spot_price: float, position_size: int,
                          holding_period_years: float) -> float:
        """
        Calculate P&L from dividend income

        Formula: PnL = Position_Size * Spot * q * T

        Parameters:
        -----------
        spot_price : float
            Index price
        position_size : int
            Number of units
        holding_period_years : float
            Holding period in years

        Returns:
        --------
        float : P&L from dividends
        """
        dividend_pnl = position_size * spot_price * self.q * holding_period_years
        return dividend_pnl


class MeanReversion:
    """
    Statistical Mean Reversion Strategy
    ====================================

    Mathematical Foundation:
    - Exploits tendency of prices to revert to long-run mean
    - Ornstein-Uhlenbeck Process: dX = θ(μ - X)dt + σdW
    - Half-life of mean reversion: λ = ln(2) / θ

    Key Formulas:
        Ornstein-Uhlenbeck: X_t = μ + (X_0 - μ)*e^(-θ*t) + σ*√((1-e^(-2θ*t))/(2θ))*Z_t

        Z-score: Z = (Price - MA) / Volatility
        - Entry when |Z| > 2.0
        - Exit when |Z| < 0.5

        Half-life: HalfLife = ln(2) / θ
    """

    def __init__(self, lookback_period: int = 252, half_life_threshold: float = 30):
        """
        Initialize Mean Reversion Strategy

        Parameters:
        -----------
        lookback_period : int
            Period for moving average and volatility calculation
        half_life_threshold : float
            Minimum half-life in days for mean reversion candidate
        """
        self.lookback_period = lookback_period
        self.half_life_threshold = half_life_threshold
        self.mean = None
        self.std = None
        self.half_life = None

    def calculate_mean_std(self, prices: np.ndarray) -> Tuple[float, float]:
        """
        Calculate mean and standard deviation

        Parameters:
        -----------
        prices : np.ndarray
            Price series

        Returns:
        --------
        Tuple : (mean, std) of the series
        """
        recent_prices = prices[-self.lookback_period:]
        self.mean = np.mean(recent_prices)
        self.std = np.std(recent_prices)
        return self.mean, self.std

    def estimate_mean_reversion_speed(self, prices: np.ndarray) -> Tuple[float, float]:
        """
        Estimate mean reversion speed (theta) and half-life

        Fitting AR(1) model: X_t - X_{t-1} = -θ(X_{t-1} - μ) + ε_t
        Rearrange: X_t = (1 - θ)X_{t-1} + θμ + ε_t

        Estimate θ = 1 - φ where φ is AR(1) coefficient
        Half-life = ln(2) / θ

        Parameters:
        -----------
        prices : np.ndarray
            Price series

        Returns:
        --------
        Tuple : (theta, half_life) in days
        """
        recent_prices = prices[-self.lookback_period:]

        # Fit AR(1) model
        y = recent_prices[1:]
        x = recent_prices[:-1]
        n = len(y)

        # OLS: y = φ*x + c + ε
        X = np.column_stack([np.ones(n), x])
        coef = np.linalg.lstsq(X, y, rcond=None)[0]
        phi = coef[1]  # AR(1) coefficient

        # Mean reversion speed
        theta = 1 - phi
        self.half_life = np.log(2) / max(theta, 0.001)  # Avoid division by zero

        return theta, self.half_life

    def calculate_z_score(self, price: float) -> float:
        """
        Calculate Z-score relative to mean

        Formula: Z = (Price - μ) / σ

        Parameters:
        -----------
        price : float
            Current price

        Returns:
        --------
        float : Z-score
        """
        if self.mean is None or self.std is None:
            raise ValueError("Must call calculate_mean_std() first")

        return (price - self.mean) / max(self.std, 1e-6)

    def generate_signals(self, prices: np.ndarray, entry_z: float = 2.0,
                        exit_z: float = 0.5) -> np.ndarray:
        """
        Generate mean reversion trading signals

        Logic:
        - Entry when |Z-score| > entry_z (deviation from mean)
        - Exit when |Z-score| < exit_z (reversion to mean)

        Parameters:
        -----------
        prices : np.ndarray
            Price series
        entry_z : float
            Z-score threshold for entry (default: 2.0)
        exit_z : float
            Z-score threshold for exit (default: 0.5)

        Returns:
        --------
        np.ndarray : Trading signals
        """
        self.calculate_mean_std(prices)
        theta, half_life = self.estimate_mean_reversion_speed(prices)

        signals = np.zeros(len(prices))
        position = 0  # 1 for long, -1 for short, 0 for flat

        for i in range(self.lookback_period, len(prices)):
            z_score = self.calculate_z_score(prices[i])

            # Entry signals
            if abs(z_score) > entry_z and position == 0:
                position = -np.sign(z_score)  # Long if z < -2, short if z > 2
                signals[i] = position
            # Exit signals
            elif abs(z_score) < exit_z and position != 0:
                position = 0
                signals[i] = 0
            # Hold position
            else:
                signals[i] = position

        return signals

    def expected_reversion_time(self) -> float:
        """
        Calculate expected time for price to revert to mean

        Based on half-life estimate

        Returns:
        --------
        float : Expected reversion time in days
        """
        if self.half_life is None:
            raise ValueError("Must estimate mean reversion speed first")
        return self.half_life


class DistanceRelativeValue:
    """
    Distance-Based Relative Value Trading
    ======================================

    Mathematical Foundation:
    - Uses Euclidean distance in price space to identify correlated moves
    - When correlated assets move apart, assume they'll converge
    - Distance metric: D = √(Σ(ΔP_i)²)

    Key Formulas:
        Normalized Distance: d_t = Σ(w_i * (P_i,t - P_i,MA)²)

        Correlation breakdown threshold:
        D_recent > D_historical * threshold
    """

    def __init__(self, lookback_period: int = 252, distance_threshold: float = 1.5):
        """
        Initialize Distance-Based Strategy

        Parameters:
        -----------
        lookback_period : int
            Period for historical distance calculation
        distance_threshold : float
            Threshold for distance deviation (default: 1.5x historical)
        """
        self.lookback_period = lookback_period
        self.distance_threshold = distance_threshold
        self.historical_distance_mean = None
        self.historical_distance_std = None

    def calculate_distance(self, prices: np.ndarray) -> np.ndarray:
        """
        Calculate Euclidean distance of price changes

        Formula: D_t = √(Σ(ΔP_i)²)

        Parameters:
        -----------
        prices : np.ndarray
            Price matrix (n_periods, n_securities)

        Returns:
        --------
        np.ndarray : Distance series
        """
        # Calculate returns
        returns = np.diff(prices, axis=0)

        # Euclidean distance of returns
        distances = np.sqrt(np.sum(returns**2, axis=1))

        return distances

    def calculate_spread_distance(self, prices: np.ndarray) -> np.ndarray:
        """
        Calculate distance from moving average (spread measure)

        Formula: d_i,t = (P_i,t - MA_i,t) / σ_i,t

        Parameters:
        -----------
        prices : np.ndarray
            Price matrix

        Returns:
        --------
        np.ndarray : Normalized spread distances
        """
        n_periods, n_assets = prices.shape
        ma = np.zeros_like(prices)
        std = np.zeros_like(prices)

        # Calculate rolling mean and std without pandas
        for i in range(n_periods):
            start_idx = max(0, i - self.lookback_period + 1)
            window = prices[start_idx:i+1]

            for j in range(n_assets):
                ma[i, j] = np.mean(window[:, j])
                std[i, j] = np.std(window[:, j])

        # Avoid division by zero
        std = np.where(std < 1e-6, 1, std)

        spread_distance = (prices - ma) / std

        # Calculate overall distance
        total_distance = np.sqrt(np.sum(spread_distance**2, axis=1))

        return total_distance

    def identify_correlation_breakdown(self, prices: np.ndarray) -> Dict:
        """
        Identify when correlations break down

        Parameters:
        -----------
        prices : np.ndarray
            Price matrix

        Returns:
        --------
        Dict : Breakdown events and severity
        """
        distances = self.calculate_spread_distance(prices)

        # Use historical data to establish baseline
        hist_distances = distances[:self.lookback_period]
        self.historical_distance_mean = np.mean(hist_distances)
        self.historical_distance_std = np.std(hist_distances)

        # Identify deviation
        recent_distances = distances[-60:]  # Last 60 periods

        deviation = (recent_distances - self.historical_distance_mean) / max(self.historical_distance_std, 1e-6)

        breakdowns = {
            'current_distance': distances[-1],
            'historical_mean': self.historical_distance_mean,
            'z_score': (distances[-1] - self.historical_distance_mean) / max(self.historical_distance_std, 1e-6),
            'is_breakdown': (distances[-1] > self.historical_distance_mean * self.distance_threshold)
        }

        return breakdowns


# Example Usage and Testing
def example_pairs_trading():
    """Example: Pairs Trading Implementation"""
    print("\n" + "="*60)
    print("EXAMPLE 1: PAIRS TRADING WITH COINTEGRATION")
    print("="*60)

    # Simulate two cointegrated stock prices
    np.random.seed(42)
    n = 252 * 2  # 2 years of daily data

    # Stock 1
    s1 = 100 + np.cumsum(np.random.normal(0.0005, 0.02, n))

    # Stock 2: Cointegrated with Stock 1
    s2 = 80 + 0.8 * (s1 - 100) + np.cumsum(np.random.normal(0.0003, 0.015, n))

    # Initialize and run pairs trading
    pt = PairsTrading(lookback_period=252)
    beta = pt.calculate_hedge_ratio(s1, s2)
    spread = pt.calculate_spread(s1, s2)

    print(f"Hedge Ratio (β): {beta:.4f}")
    print(f"Mean Spread: {pt.mean_spread:.4f}")
    print(f"Std Dev Spread: {pt.std_spread:.4f}")

    # Test for stationarity
    adf_results = pt.adf_test(spread[-252:])
    print(f"ADF Test p-value: {adf_results['p_value']:.4f}")
    print(f"Is Stationary: {adf_results['is_stationary']}")

    # Generate signals
    signals = pt.generate_signals(spread)
    print(f"Current Signal: {signals[-1]}")


def example_basket_arbitrage():
    """Example: Basket Arbitrage Implementation"""
    print("\n" + "="*60)
    print("EXAMPLE 2: BASKET ARBITRAGE")
    print("="*60)

    np.random.seed(42)
    n = 252

    # 5 stock portfolio with weights
    weights = np.array([0.30, 0.25, 0.20, 0.15, 0.10])

    # Generate correlated prices
    index_returns = np.random.normal(0.0005, 0.01, n)
    component_prices = np.zeros((n, 5))
    component_prices[0] = [100, 80, 120, 90, 110]

    for i in range(1, n):
        shocks = np.random.normal(0, 0.015, 5)
        component_prices[i] = component_prices[i-1] * (1 + index_returns[i] + shocks)

    # Create index (slightly mispriced)
    index_prices = component_prices @ weights * (1 + np.random.uniform(-0.01, 0.01, n))

    # Run basket arbitrage
    ba = BasketArbitrage(weights=weights)
    synthetic = ba.calculate_synthetic_index(component_prices)
    mispricing = ba.calculate_mispricing(index_prices, synthetic)
    signals = ba.generate_signals(mispricing, threshold=0.01)

    print(f"Latest Index Price: {index_prices[-1]:.2f}")
    print(f"Latest Synthetic Price: {synthetic[-1]:.2f}")
    print(f"Latest Mispricing: {mispricing[-1]*100:.2f}%")
    print(f"Arbitrage Signals (Last 5): {signals[-5:].astype(int)}")


def example_index_arbitrage():
    """Example: Index Arbitrage Implementation"""
    print("\n" + "="*60)
    print("EXAMPLE 3: INDEX ARBITRAGE")
    print("="*60)

    ia = IndexArbitrage(risk_free_rate=0.05, dividend_yield=0.02)

    spot_price = 4500
    futures_price = 4550
    time_to_maturity = 91/365  # 91 days

    opportunity = ia.identify_arbitrage_opportunity(
        spot_price, futures_price, time_to_maturity
    )

    print(f"Spot Price: ${spot_price}")
    print(f"Futures Price: ${futures_price}")
    print(f"Theoretical Price: ${opportunity['theoretical_price']:.2f}")
    print(f"Mispricing: ${opportunity['mispricing']:.2f}")
    print(f"Mispricing %: {opportunity['mispricing_pct']:.3f}%")
    print(f"Round Trip Cost: ${opportunity['round_trip_cost']:.2f}")
    print(f"Net Profit: ${opportunity['net_profit']:.2f}")
    print(f"Strategy: {opportunity['strategy']}")


def example_mean_reversion():
    """Example: Mean Reversion Strategy"""
    print("\n" + "="*60)
    print("EXAMPLE 4: MEAN REVERSION STRATEGY")
    print("="*60)

    np.random.seed(42)
    n = 252 * 2

    # Generate mean-reverting process
    prices = np.zeros(n)
    prices[0] = 100
    mu = 100
    theta = 0.05

    for i in range(1, n):
        prices[i] = prices[i-1] + theta * (mu - prices[i-1]) + np.random.normal(0, 2)

    # Run mean reversion analysis
    mr = MeanReversion(lookback_period=252)
    mean_val, std_val = mr.calculate_mean_std(prices[-252:])
    theta_est, half_life = mr.estimate_mean_reversion_speed(prices[-252:])

    print(f"Mean: {mean_val:.2f}")
    print(f"Std Dev: {std_val:.2f}")
    print(f"Estimated θ (reversion speed): {theta_est:.4f}")
    print(f"Half-life of Reversion: {half_life:.1f} days")

    # Generate signals for last 5 days
    signals = mr.generate_signals(prices)
    print(f"Last 5 Signals: {signals[-5:].astype(int)}")


if __name__ == "__main__":
    example_pairs_trading()
    example_basket_arbitrage()
    example_index_arbitrage()
    example_mean_reversion()

    print("\n" + "="*60)
    print("All examples completed successfully!")
    print("="*60)
