"""
Market Microstructure Analysis Implementation
Includes Kyle's lambda, Amihud illiquidity, bid-ask spreads, and price impact models
Focus on order flow analysis and transaction costs quantification
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Tuple, Dict, Optional, Union


class MarketMicrostructure:
    """
    Comprehensive market microstructure analysis class
    Analyzes liquidity, spreads, and price impact from order flow data
    """

    def __init__(self, price_data: Union[pd.Series, np.ndarray],
                 volume_data: Union[pd.Series, np.ndarray],
                 bid_data: Optional[Union[pd.Series, np.ndarray]] = None,
                 ask_data: Optional[Union[pd.Series, np.ndarray]] = None):
        """
        Initialize with price and volume data

        Parameters:
        -----------
        price_data : pd.Series or np.array
            Asset prices (closing prices or midprices)
        volume_data : pd.Series or np.array
            Trading volumes (number of shares)
        bid_data : pd.Series or np.array, optional
            Bid prices for spread calculations
        ask_data : pd.Series or np.array, optional
            Ask prices for spread calculations
        """
        self.price = pd.Series(price_data).reset_index(drop=True)
        self.volume = pd.Series(volume_data).reset_index(drop=True)
        self.bid = pd.Series(bid_data).reset_index(drop=True) if bid_data is not None else None
        self.ask = pd.Series(ask_data).reset_index(drop=True) if ask_data is not None else None

        self.n = len(self.price)
        self.returns = np.log(self.price / self.price.shift(1)).dropna()

    # ==================== KYLE'S LAMBDA (Price Impact Parameter) ====================

    def kylos_lambda(self, window: int = 20, min_volume: float = 100) -> pd.Series:
        """
        Calculate Kyle's lambda - Price Impact Parameter

        Kyle's lambda measures the permanent price impact of order flow.
        It represents how much price moves per unit of net order flow.

        Formula:
        λ = Δ Price / |Net Order Flow|
        = |Δ P_t| / |Q_t|

        Where:
        - Δ P_t: Price change from t to t+1
        - Q_t: Net order flow (signed volume)

        High λ: Large price impact (illiquid asset)
        Low λ: Small price impact (liquid asset)

        Parameters:
        -----------
        window : int
            Rolling window size for calculation
        min_volume : float
            Minimum volume threshold (filter out low-volume periods)

        Returns:
        --------
        pd.Series : Kyle's lambda values (rolling estimate)
        """
        # Calculate price changes
        price_change = self.price.diff().abs()

        # Filter by volume threshold
        valid_vol = self.volume >= min_volume

        # Rolling lambda calculation
        lambda_values = []
        for i in range(window, len(self.price)):
            vol_window = self.volume[i-window:i]
            price_window = price_change[i-window:i]

            # Avoid division by zero
            if vol_window.sum() > 0:
                lambda_i = price_window.mean() / (vol_window.mean() + 1e-8)
            else:
                lambda_i = np.nan

            lambda_values.append(lambda_i)

        # Prepare output series
        result = pd.Series([np.nan] * (window - 1) + lambda_values, index=self.price.index)
        return result

    # ==================== AMIHUD ILLIQUIDITY RATIO ====================

    def amihud_illiquidity(self, window: int = 20) -> pd.Series:
        """
        Calculate Amihud Illiquidity Ratio

        Amihud's ILLIQ measure quantifies the price impact of trading volume.
        It's the ratio of absolute returns to trading volume (dollar volume in original).

        Formula:
        ILLIQ_t = |R_t| / V_t

        Where:
        - R_t: Return (log or simple) at time t
        - V_t: Volume at time t (or dollar volume: P_t * V_t)

        Interpretation:
        - High ILLIQ: Asset is illiquid (large price per unit volume)
        - Low ILLIQ: Asset is liquid (small price per unit volume)
        - Zero volume → infinite illiquidity (handled by filtering)

        Rolling Average:
        ILLIQ = (1/N) * Σ |R_t| / V_t over N days

        Parameters:
        -----------
        window : int
            Rolling window for averaging

        Returns:
        --------
        pd.Series : Rolling Amihud illiquidity ratio
        """
        # Calculate absolute returns
        abs_returns = np.abs(self.returns)

        # Align with original price index (drop first NaN)
        aligned_returns = pd.Series(abs_returns.values, index=self.price.index[1:])
        aligned_volume = self.volume[1:]

        # Calculate illiquidity ratio
        # Add small epsilon to avoid division by zero
        illiquidity = aligned_returns / (aligned_volume + 1e-8)

        # Rolling average
        amihud = illiquidity.rolling(window=window, min_periods=1).mean()

        return amihud

    # ==================== EFFECTIVE SPREAD (Realized Spread) ====================

    def effective_spread(self) -> pd.Series:
        """
        Calculate Effective Spread

        Effective spread measures the actual cost of trading, accounting for
        the difference between execution price and the midpoint.

        Formula (for buy orders):
        ES_buy = 2 * (P_executed - P_midpoint) / P_midpoint

        For sell orders:
        ES_sell = 2 * (P_midpoint - P_executed) / P_midpoint

        Two-sided (quote spread):
        Effective Spread = (Ask - Bid) / Midpoint

        Requires:
        - Bid and ask prices

        Returns:
        --------
        pd.Series : Effective spread as percentage of midpoint
        """
        if self.bid is None or self.ask is None:
            raise ValueError("Bid and ask prices required for effective spread calculation")

        # Calculate midpoint
        midpoint = (self.bid + self.ask) / 2

        # Calculate effective spread
        spread = (self.ask - self.bid) / midpoint

        return spread

    # ==================== REALIZED SPREAD (Trading Cost) ====================

    def realized_spread(self, hold_period: int = 1) -> pd.Series:
        """
        Calculate Realized Spread (Trading Cost)

        Realized spread measures actual profit/loss from transaction.
        Trader buys at ask, sells at subsequent midpoint (or vice versa).

        Formula:
        RS = 2 * |M_t+1 - P_execution| / M_t

        Where:
        - M_t: Midpoint at time t
        - M_t+1: Midpoint at time t + hold_period
        - P_execution: Execution price (ask for buy, bid for sell)

        Positive RS: Trader made profit (liquidity provision)
        Negative RS: Trader lost (paid for liquidity)

        Parameters:
        -----------
        hold_period : int
            Holding period for realized profit calculation

        Returns:
        --------
        pd.Series : Realized spread values
        """
        if self.bid is None or self.ask is None:
            raise ValueError("Bid and ask prices required for realized spread")

        midpoint = (self.bid + self.ask) / 2

        # Assume buy order (at ask) - shift forward by hold_period
        midpoint_future = midpoint.shift(-hold_period)

        realized = 2 * (midpoint_future - self.ask) / midpoint

        return realized

    # ==================== ROLL'S BID-ASK ESTIMATOR ====================

    def rolls_estimator(self, window: int = 20) -> pd.Series:
        """
        Calculate Roll's Bid-Ask Spread Estimator

        Roll (1984) developed a model to estimate bid-ask spread from price changes alone,
        without observing actual bid/ask data.

        Key Insight:
        Price changes come from two sources:
        1. New information → permanent component (Δ Mid)
        2. Order flow → transitory component (spread)

        Formula:
        Cov(ΔP_t, ΔP_{t-1}) = -S^2 / 4

        Where S is the bid-ask spread.

        Solving for spread:
        S = 2 * sqrt(-Cov(ΔP_t, ΔP_{t-1}))

        Notes:
        - Assumes efficient market hypothesis
        - Covariance should be negative (mean-reversion from spread)
        - Fails if no bid-ask spread exists (high-volume liquid assets)
        - Robust to stock splits and dividends (uses price changes)

        Parameters:
        -----------
        window : int
            Rolling window for covariance calculation

        Returns:
        --------
        pd.Series : Estimated spread as percentage of price
        """
        # Calculate price differences
        price_diff = self.price.diff()

        # Rolling covariance between ΔP_t and ΔP_{t-1}
        cov_values = []
        for i in range(window, len(price_diff)):
            window_cov = price_diff[i-window:i].cov(price_diff[i-window+1:i+1])
            cov_values.append(window_cov)

        # Convert to series
        cov_series = pd.Series([np.nan] * (window - 1) + cov_values, index=self.price.index)

        # Calculate spread from covariance
        # S = 2 * sqrt(-Cov(ΔP_t, ΔP_{t-1}))
        spread_values = 2 * np.sqrt(np.maximum(-cov_series, 0))

        # Convert to percentage of price
        spread_pct = (spread_values / self.price) * 100

        return spread_pct

    # ==================== HIGH-LOW SPREAD ESTIMATOR ====================

    def high_low_spread(self, high_price: Union[pd.Series, np.ndarray],
                       low_price: Union[pd.Series, np.ndarray]) -> pd.Series:
        """
        Estimate bid-ask spread from intraday high-low prices

        Simple formula:
        Spread ≈ (High - Low) / Midpoint

        Where Midpoint = (High + Low) / 2

        This assumes the high is executed at ask and low at bid.

        Parameters:
        -----------
        high_price : pd.Series or np.array
            Intraday high prices
        low_price : pd.Series or np.array
            Intraday low prices

        Returns:
        --------
        pd.Series : Estimated bid-ask spread
        """
        high = pd.Series(high_price).reset_index(drop=True)
        low = pd.Series(low_price).reset_index(drop=True)

        midpoint = (high + low) / 2
        spread = (high - low) / midpoint

        return spread

    # ==================== PRICE IMPACT ESTIMATION ====================

    def price_impact_linear(self, lookback: int = 50) -> Dict[str, float]:
        """
        Estimate Price Impact using Linear Regression

        Price impact models the relationship between order flow and price:
        ΔP = λ * |Q| + ε

        Where:
        - ΔP: Price change
        - Q: Order flow (volume with direction)
        - λ: Price impact coefficient

        Linear model:
        λ_linear = Cov(ΔP, |Q|) / Var(|Q|)

        Parameters:
        -----------
        lookback : int
            Number of observations for regression

        Returns:
        --------
        dict : Contains slope (price impact), R-squared, significance
        """
        price_changes = self.price.diff().dropna()
        volumes = self.volume[1:]  # Align indices

        # Ensure matching lengths
        min_len = min(len(price_changes), len(volumes))
        price_changes = price_changes[:min_len]
        volumes = volumes[:min_len]

        # Linear regression: Price_change = α + β * Volume + ε
        X = volumes.values.reshape(-1, 1)
        y = price_changes.values

        # Add constant
        X = np.column_stack([np.ones(len(X)), X])

        # OLS: β = (X'X)^-1 X'y
        try:
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]

            # Calculate R-squared
            y_pred = X @ coeffs
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot)

            # Standard error and t-statistic
            residuals = y - y_pred
            mse = ss_res / (len(y) - 2)
            var_covar = mse * np.linalg.inv(X.T @ X)
            se = np.sqrt(np.diag(var_covar))
            t_stat = coeffs / se
            p_values = 2 * (1 - stats.t.cdf(np.abs(t_stat), len(y) - 2))

            return {
                'price_impact': coeffs[1],
                'intercept': coeffs[0],
                'r_squared': r_squared,
                't_stat_impact': t_stat[1],
                'p_value_impact': p_values[1],
                'se_impact': se[1]
            }
        except:
            return {
                'price_impact': np.nan,
                'intercept': np.nan,
                'r_squared': np.nan,
                't_stat_impact': np.nan,
                'p_value_impact': np.nan,
                'se_impact': np.nan
            }

    def price_impact_nonlinear(self, lookback: int = 50) -> Dict[str, float]:
        """
        Estimate Price Impact using Nonlinear Model (Power Law)

        Empirical evidence suggests price impact follows a power law:
        ΔP = α * |Q|^β

        Taking logs:
        log(ΔP) = log(α) + β * log(|Q|)

        Where β typically ranges from 0.5 to 1.0

        Parameters:
        -----------
        lookback : int
            Number of observations

        Returns:
        --------
        dict : Contains power law exponent (β), alpha coefficient, R-squared
        """
        price_changes = np.abs(self.price.diff().dropna())
        volumes = self.volume[1:]

        # Align lengths
        min_len = min(len(price_changes), len(volumes))
        price_changes = price_changes[:min_len]
        volumes = volumes[:min_len]

        # Remove zeros for log transformation
        valid_idx = (price_changes > 0) & (volumes > 0)
        log_price_changes = np.log(price_changes[valid_idx])
        log_volumes = np.log(volumes[valid_idx])

        # Log-linear regression: log(ΔP) = α + β * log(V)
        X = np.column_stack([np.ones(len(log_volumes)), log_volumes])
        y = log_price_changes.values

        try:
            coeffs = np.linalg.lstsq(X, y, rcond=None)[0]

            # Calculate R-squared
            y_pred = X @ coeffs
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - y.mean()) ** 2)
            r_squared = 1 - (ss_res / ss_tot)

            return {
                'power_law_exponent': coeffs[1],  # β
                'alpha': np.exp(coeffs[0]),  # α from log
                'r_squared': r_squared,
                'elasticity': coeffs[1]  # % change in price per % change in volume
            }
        except:
            return {
                'power_law_exponent': np.nan,
                'alpha': np.nan,
                'r_squared': np.nan,
                'elasticity': np.nan
            }

    # ==================== VOLUME-WEIGHTED AVERAGE PRICE (VWAP) ====================

    def volume_weighted_average_price(self, window: int = 20) -> pd.Series:
        """
        Calculate Volume-Weighted Average Price (VWAP)

        VWAP is the average price weighted by trading volume.

        Formula:
        VWAP = Σ(Price_i * Volume_i) / Σ(Volume_i)

        Used for:
        - Assessing execution quality
        - Determining if trades were at fair value
        - Swing trading signals

        Parameters:
        -----------
        window : int
            Rolling window size

        Returns:
        --------
        pd.Series : VWAP values
        """
        pv = self.price * self.volume
        vwap = pv.rolling(window=window).sum() / self.volume.rolling(window=window).sum()
        return vwap

    # ==================== LIQUIDITY METRICS SUMMARY ====================

    def liquidity_report(self, window: int = 20) -> pd.DataFrame:
        """
        Generate comprehensive liquidity report

        Combines multiple liquidity metrics into a single dataframe

        Parameters:
        -----------
        window : int
            Rolling window size for calculations

        Returns:
        --------
        pd.DataFrame : Summary of liquidity metrics
        """
        report = pd.DataFrame(index=self.price.index)

        # Kyle's lambda
        report['kylos_lambda'] = self.kylos_lambda(window=window)

        # Amihud illiquidity
        report['amihud_illiq'] = self.amihud_illiquidity(window=window)

        # Roll's estimator
        report['rolls_spread_pct'] = self.rolls_estimator(window=window)

        # VWAP
        report['vwap'] = self.volume_weighted_average_price(window=window)

        # Price impact
        impact = self.price_impact_linear(lookback=window)
        report['price_impact'] = impact['price_impact']

        # Spread if bid/ask available
        if self.bid is not None and self.ask is not None:
            report['effective_spread_pct'] = self.effective_spread() * 100
            report['realized_spread_pct'] = self.realized_spread() * 100

        return report

    # ==================== UTILITY METHODS ====================

    def bid_ask_statistics(self) -> Dict[str, float]:
        """
        Calculate basic bid-ask spread statistics

        Returns:
        --------
        dict : Spread statistics (mean, std, min, max)
        """
        if self.bid is None or self.ask is None:
            raise ValueError("Bid and ask prices required")

        midpoint = (self.bid + self.ask) / 2
        spread_pct = ((self.ask - self.bid) / midpoint * 100)

        return {
            'mean_spread_pct': spread_pct.mean(),
            'median_spread_pct': spread_pct.median(),
            'std_spread_pct': spread_pct.std(),
            'min_spread_pct': spread_pct.min(),
            'max_spread_pct': spread_pct.max(),
            'mean_spread_bps': spread_pct.mean() * 100  # basis points
        }

    def order_flow_analysis(self) -> pd.DataFrame:
        """
        Analyze order flow characteristics

        Returns:
        --------
        pd.DataFrame : Order flow statistics
        """
        price_changes = self.price.diff()

        analysis = pd.DataFrame({
            'price': self.price,
            'volume': self.volume,
            'price_change': price_changes,
            'abs_price_change': np.abs(price_changes),
            'volume_price_product': self.volume * np.abs(price_changes)
        })

        return analysis


# ==================== CONVENIENCE FUNCTIONS ====================

def compare_spread_methods(prices: Union[pd.Series, np.ndarray],
                          volumes: Union[pd.Series, np.ndarray],
                          bid_prices: Optional[Union[pd.Series, np.ndarray]] = None,
                          ask_prices: Optional[Union[pd.Series, np.ndarray]] = None,
                          high_prices: Optional[Union[pd.Series, np.ndarray]] = None,
                          low_prices: Optional[Union[pd.Series, np.ndarray]] = None) -> pd.DataFrame:
    """
    Compare multiple spread estimation methods

    Parameters:
    -----------
    prices : pd.Series or np.array
        Asset prices
    volumes : pd.Series or np.array
        Trading volumes
    bid_prices : pd.Series or np.array, optional
    ask_prices : pd.Series or np.array, optional
    high_prices : pd.Series or np.array, optional
    low_prices : pd.Series or np.array, optional

    Returns:
    --------
    pd.DataFrame : Comparison of spread estimates
    """
    mm = MarketMicrostructure(prices, volumes, bid_prices, ask_prices)

    comparison = pd.DataFrame(index=pd.Series(prices).index)

    # Roll's estimator (always available)
    comparison['rolls_spread'] = mm.rolls_estimator()

    # Effective spread (if bid/ask available)
    if bid_prices is not None and ask_prices is not None:
        comparison['effective_spread'] = mm.effective_spread() * 100

    # High-low estimator (if available)
    if high_prices is not None and low_prices is not None:
        comparison['hl_spread'] = mm.high_low_spread(high_prices, low_prices) * 100

    return comparison
