"""
Mean Reversion Trading Strategies Implementation

This module implements 5+ mean reversion trading strategies with mathematical foundations.
Strategies: Bollinger Bands, RSI, Z-score, Half-life calculation, Ornstein-Uhlenbeck process
"""

import numpy as np
import pandas as pd
from scipy.stats import linregress
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')


class MeanReversionStrategies:
    """
    Collection of mean reversion trading strategies with signal generation.
    """

    def __init__(self, data: pd.DataFrame, price_column: str = 'close'):
        """
        Initialize with price data.

        Args:
            data: DataFrame with OHLCV data
            price_column: Column name for prices (default: 'close')
        """
        self.data = data.copy()
        self.prices = data[price_column].values
        self.returns = np.diff(np.log(self.prices))
        self.length = len(self.prices)

    # ====================
    # 1. BOLLINGER BANDS
    # ====================

    def bollinger_bands(self, period: int = 20, num_std: float = 2.0) -> Dict:
        """
        Bollinger Bands Mean Reversion Strategy

        Formula:
            MA = SMA(prices, period)
            STD = standard_deviation(prices, period)
            Upper Band = MA + (num_std * STD)
            Lower Band = MA - (num_std * STD)

        Signal:
            BUY: price < Lower Band (oversold)
            SELL: price > Upper Band (overbought)

        Args:
            period: Moving average period (default: 20)
            num_std: Number of standard deviations (default: 2.0)

        Returns:
            Dictionary with bands and signals
        """
        ma = pd.Series(self.prices).rolling(period).mean().values
        std = pd.Series(self.prices).rolling(period).std().values

        upper_band = ma + (num_std * std)
        lower_band = ma - (num_std * std)

        # Generate signals: 1=buy (oversold), -1=sell (overbought), 0=neutral
        signals = np.zeros(self.length)
        signals[self.prices < lower_band] = 1      # Buy oversold
        signals[self.prices > upper_band] = -1     # Sell overbought

        return {
            'middle_band': ma,
            'upper_band': upper_band,
            'lower_band': lower_band,
            'signals': signals,
            'band_width': upper_band - lower_band,
            '%b': (self.prices - lower_band) / (upper_band - lower_band)
        }

    # ====================
    # 2. RSI (Relative Strength Index)
    # ====================

    def rsi_strategy(self, period: int = 14,
                     oversold: float = 30,
                     overbought: float = 70) -> Dict:
        """
        RSI Mean Reversion Strategy

        Formula:
            Δ = price[t] - price[t-1]
            RS = average_gain / average_loss
            RSI = 100 - (100 / (1 + RS))

        Signal:
            BUY: RSI < oversold_threshold
            SELL: RSI > overbought_threshold

        Args:
            period: RSI period (default: 14)
            oversold: Oversold threshold (default: 30)
            overbought: Overbought threshold (default: 70)

        Returns:
            Dictionary with RSI values and signals
        """
        # Calculate price changes
        delta = np.diff(self.prices, prepend=self.prices[0])

        # Separate gains and losses
        gains = np.where(delta > 0, delta, 0)
        losses = np.where(delta < 0, -delta, 0)

        # Calculate average gains and losses using EMA
        avg_gains = pd.Series(gains).ewm(span=period, adjust=False).mean().values
        avg_losses = pd.Series(losses).ewm(span=period, adjust=False).mean().values

        # Calculate RS and RSI
        rs = avg_gains / (avg_losses + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        # Generate signals
        signals = np.zeros(self.length)
        signals[rsi < oversold] = 1        # Buy oversold
        signals[rsi > overbought] = -1     # Sell overbought

        return {
            'rsi': rsi,
            'signals': signals,
            'avg_gains': avg_gains,
            'avg_losses': avg_losses,
            'oversold_level': oversold,
            'overbought_level': overbought
        }

    # ====================
    # 3. Z-SCORE METHOD
    # ====================

    def zscore_strategy(self, period: int = 20,
                       entry_threshold: float = 2.0,
                       exit_threshold: float = 1.0) -> Dict:
        """
        Z-Score Mean Reversion Strategy

        Formula:
            Z-score = (price - MA(period)) / STD(period)

        Signal:
            BUY: Z-score < -entry_threshold (below mean)
            SELL: Z-score > entry_threshold (above mean)
            EXIT: |Z-score| < exit_threshold (near mean)

        Args:
            period: Moving average period (default: 20)
            entry_threshold: Entry signal threshold (default: 2.0)
            exit_threshold: Exit signal threshold (default: 1.0)

        Returns:
            Dictionary with Z-scores and signals
        """
        ma = pd.Series(self.prices).rolling(period).mean().values
        std = pd.Series(self.prices).rolling(period).std().values

        # Calculate Z-scores
        zscore = (self.prices - ma) / (std + 1e-10)

        # Generate signals
        signals = np.zeros(self.length)
        signals[zscore < -entry_threshold] = 1      # Buy
        signals[zscore > entry_threshold] = -1      # Sell

        # Mark neutral zone
        neutral = np.abs(zscore) < exit_threshold

        return {
            'zscore': zscore,
            'signals': signals,
            'mean': ma,
            'std': std,
            'neutral_zone': neutral,
            'entry_threshold': entry_threshold,
            'exit_threshold': exit_threshold
        }

    # ====================
    # 4. HALF-LIFE CALCULATION
    # ====================

    def calculate_half_life(self, window: int = 252) -> Dict:
        """
        Calculate Half-Life of Mean Reversion

        Theory:
            For a mean-reverting series: x[t] = φ*x[t-1] + ε[t]
            Half-life = ln(2) / |ln(φ)|

        Where φ (phi) is the autocorrelation coefficient from AR(1) regression.

        Formula:
            x[t] - x[t-1] = -λ(x[t-1] - μ) + ε[t]
            λ = speed of mean reversion
            Half-life = ln(2) / λ

        Args:
            window: Regression window (default: 252 trading days)

        Returns:
            Dictionary with half-life metrics
        """
        half_lives = []
        half_life_dates = []

        # Rolling half-life calculation
        for i in range(window, len(self.prices)):
            price_window = self.prices[i-window:i]

            # AR(1) regression: price[t] = constant + phi * price[t-1] + error
            x = price_window[:-1]
            y = price_window[1:]

            # Add constant term
            x_with_const = np.column_stack([np.ones(len(x)), x])

            # OLS regression
            try:
                coeffs = np.linalg.lstsq(x_with_const, y, rcond=None)[0]
                phi = coeffs[1]

                # Calculate half-life
                if 0 < phi < 1:
                    half_life = np.log(2) / np.log(1 / phi)
                    half_lives.append(half_life)
                    half_life_dates.append(i)
                else:
                    half_lives.append(np.nan)
                    half_life_dates.append(i)
            except:
                half_lives.append(np.nan)
                half_life_dates.append(i)

        half_life_array = np.full(len(self.prices), np.nan)
        half_life_array[half_life_dates] = half_lives

        # Mean reversion strength: lower half-life = faster reversion
        mean_hl = np.nanmean(half_lives) if half_lives else np.nan

        return {
            'half_life': half_life_array,
            'mean_half_life': mean_hl,
            'half_lives_rolling': np.array(half_lives),
            'is_mean_reverting': mean_hl < 252 if not np.isnan(mean_hl) else False,
            'reversion_strength': 1 / (mean_hl + 1) if not np.isnan(mean_hl) else 0
        }

    # ====================
    # 5. ORNSTEIN-UHLENBECK PROCESS
    # ====================

    def ornstein_uhlenbeck_analysis(self, window: int = 252) -> Dict:
        """
        Ornstein-Uhlenbeck (OU) Process Parameter Estimation

        Continuous-time model:
            dX(t) = θ(μ - X(t))dt + σ dW(t)

        Discrete approximation:
            X[t] = X[t-1] + θ(μ - X[t-1])Δt + σ√Δt * Z[t]

        Where:
            θ = mean reversion speed (kappa)
            μ = long-term mean
            σ = volatility

        Parameters estimated via MLE or regression.

        Args:
            window: Estimation window (default: 252)

        Returns:
            Dictionary with OU parameters and signals
        """
        ou_params = []
        ou_dates = []

        for i in range(window, len(self.prices), 20):  # Step by 20 for efficiency
            price_window = self.prices[i-window:i]

            # Estimate long-term mean (μ)
            mu = np.mean(price_window)

            # Estimate mean reversion speed (θ/kappa) via AR regression
            x = price_window[:-1]
            y = price_window[1:]

            x_with_const = np.column_stack([np.ones(len(x)), x])
            try:
                coeffs = np.linalg.lstsq(x_with_const, y, rcond=None)[0]
                intercept, phi = coeffs[0], coeffs[1]

                # theta = -ln(phi) for discrete approximation with Δt=1
                theta = -np.log(max(phi, 1e-6))

                # Estimate volatility (σ) from residuals
                residuals = y - (intercept + phi * x)
                sigma = np.std(residuals)

                ou_params.append({
                    'mu': mu,
                    'theta': theta,
                    'sigma': sigma,
                    'phi': phi
                })
                ou_dates.append(i)
            except:
                pass

        if ou_params:
            latest_params = ou_params[-1]
            mu = latest_params['mu']
            theta = latest_params['theta']
            sigma = latest_params['sigma']

            # Generate signals based on distance from mean
            # Using OU-informed thresholds
            distance_from_mean = self.prices - mu
            normalized_distance = distance_from_mean / (sigma + 1e-10)

            signals = np.zeros(len(self.prices))
            signals[normalized_distance < -1.5] = 1    # Buy signal
            signals[normalized_distance > 1.5] = -1    # Sell signal

            return {
                'mu': mu,
                'theta': theta,                         # Mean reversion speed
                'sigma': sigma,                         # Volatility
                'signals': signals,
                'distance_from_mean': distance_from_mean,
                'normalized_distance': normalized_distance,
                'expected_value': mu,
                'parameter_history': ou_params,
                'expected_half_life': np.log(2) / (theta + 1e-10)
            }
        else:
            return {
                'mu': np.nan,
                'theta': np.nan,
                'sigma': np.nan,
                'signals': np.zeros(len(self.prices)),
                'distance_from_mean': np.zeros(len(self.prices)),
                'normalized_distance': np.zeros(len(self.prices))
            }

    # ====================
    # 6. PAIRS TRADING (BONUS)
    # ====================

    def pairs_trading_zscore(self, prices2: np.ndarray,
                            period: int = 60,
                            z_threshold: float = 2.0) -> Dict:
        """
        Pairs Trading with Z-Score Spread

        Formula:
            Spread = price1 - (β * price2)
            β = correlation / volatility ratio
            Z-score(spread) used for signals

        Signal:
            BUY pair1, SELL pair2: Z-score > threshold
            SELL pair1, BUY pair2: Z-score < -threshold

        Args:
            prices2: Second security prices (pair)
            period: Lookback period (default: 60)
            z_threshold: Z-score threshold (default: 2.0)

        Returns:
            Dictionary with spread and signals
        """
        # Calculate hedge ratio using regression
        x = np.column_stack([np.ones(len(self.prices)), prices2])
        y = self.prices

        try:
            coeffs = np.linalg.lstsq(x, y, rcond=None)[0]
            beta = coeffs[1]
        except:
            beta = 1.0

        # Calculate spread
        spread = self.prices - (beta * prices2)

        # Z-score the spread
        spread_ma = pd.Series(spread).rolling(period).mean().values
        spread_std = pd.Series(spread).rolling(period).std().values
        spread_zscore = (spread - spread_ma) / (spread_std + 1e-10)

        # Signals
        signals = np.zeros(len(self.prices))
        signals[spread_zscore > z_threshold] = 1      # Buy pair1
        signals[spread_zscore < -z_threshold] = -1    # Sell pair1

        return {
            'spread': spread,
            'beta': beta,
            'spread_zscore': spread_zscore,
            'signals': signals,
            'spread_mean': spread_ma,
            'spread_std': spread_std
        }

    # ====================
    # SIGNAL METRICS
    # ====================

    def evaluate_signal(self, signals: np.ndarray) -> Dict:
        """
        Evaluate signal quality and statistics.

        Args:
            signals: Array of trading signals (1, -1, 0)

        Returns:
            Dictionary with signal metrics
        """
        buy_signals = np.sum(signals == 1)
        sell_signals = np.sum(signals == -1)
        total_signals = buy_signals + sell_signals

        signal_changes = np.sum(np.abs(np.diff(signals)) > 0)

        return {
            'buy_signals': int(buy_signals),
            'sell_signals': int(sell_signals),
            'total_signals': int(total_signals),
            'signal_changes': int(signal_changes),
            'signal_frequency': total_signals / len(signals) if len(signals) > 0 else 0
        }


# ====================
# DEMONSTRATION
# ====================

if __name__ == "__main__":
    # Create synthetic mean-reverting price data
    np.random.seed(42)
    n = 500

    # Ornstein-Uhlenbeck process simulation
    dt = 1.0
    theta = 0.1      # Mean reversion speed
    mu = 100.0       # Long-term mean
    sigma = 2.0      # Volatility

    prices = np.zeros(n)
    prices[0] = 100

    for t in range(1, n):
        drift = theta * (mu - prices[t-1]) * dt
        shock = sigma * np.sqrt(dt) * np.random.normal()
        prices[t] = prices[t-1] + drift + shock

    # Create DataFrame
    df = pd.DataFrame({
        'close': prices
    })

    # Initialize strategies
    mr = MeanReversionStrategies(df)

    print("=" * 60)
    print("MEAN REVERSION STRATEGIES ANALYSIS")
    print("=" * 60)

    # 1. Bollinger Bands
    print("\n1. BOLLINGER BANDS")
    bb_result = mr.bollinger_bands(period=20, num_std=2.0)
    bb_metrics = mr.evaluate_signal(bb_result['signals'])
    print(f"   Buy Signals: {bb_metrics['buy_signals']}")
    print(f"   Sell Signals: {bb_metrics['sell_signals']}")
    print(f"   Band Width (current): {bb_result['band_width'][-1]:.2f}")

    # 2. RSI
    print("\n2. RSI STRATEGY (Period=14)")
    rsi_result = mr.rsi_strategy(period=14)
    rsi_metrics = mr.evaluate_signal(rsi_result['signals'])
    print(f"   Current RSI: {rsi_result['rsi'][-1]:.2f}")
    print(f"   Buy Signals: {rsi_metrics['buy_signals']}")
    print(f"   Sell Signals: {rsi_metrics['sell_signals']}")

    # 3. Z-Score
    print("\n3. Z-SCORE STRATEGY")
    zscore_result = mr.zscore_strategy(period=20, entry_threshold=2.0)
    zscore_metrics = mr.evaluate_signal(zscore_result['signals'])
    print(f"   Current Z-Score: {zscore_result['zscore'][-1]:.2f}")
    print(f"   Buy Signals: {zscore_metrics['buy_signals']}")
    print(f"   Sell Signals: {zscore_metrics['sell_signals']}")

    # 4. Half-Life
    print("\n4. HALF-LIFE ANALYSIS")
    hl_result = mr.calculate_half_life(window=100)
    print(f"   Mean Half-Life: {hl_result['mean_half_life']:.2f} periods")
    print(f"   Is Mean Reverting: {hl_result['is_mean_reverting']}")
    print(f"   Reversion Strength: {hl_result['reversion_strength']:.3f}")

    # 5. Ornstein-Uhlenbeck
    print("\n5. ORNSTEIN-UHLENBECK PROCESS")
    ou_result = mr.ornstein_uhlenbeck_analysis(window=100)
    print(f"   Long-term Mean (μ): {ou_result['mu']:.2f}")
    print(f"   Mean Reversion Speed (θ): {ou_result['theta']:.4f}")
    print(f"   Volatility (σ): {ou_result['sigma']:.2f}")
    print(f"   Expected Half-Life: {ou_result['expected_half_life']:.2f} periods")
    ou_metrics = mr.evaluate_signal(ou_result['signals'])
    print(f"   Buy Signals: {ou_metrics['buy_signals']}")
    print(f"   Sell Signals: {ou_metrics['sell_signals']}")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60)
