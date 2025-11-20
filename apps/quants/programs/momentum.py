"""
Momentum and Trend Following Strategies Implementation

This module implements five key momentum trading strategies:
1. Dual Moving Average Crossover
2. Triple Moving Average System
3. MACD with Histogram
4. ADX Trend Strength
5. Turtle Trading System
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Signal:
    """Trading signal dataclass"""
    timestamp: int
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    price: float
    strategy: str
    strength: float = 0.5  # 0-1 confidence


class DualMovingAverageCrossover:
    """
    Dual Moving Average Crossover Strategy

    Buy Signal: When short-term MA crosses above long-term MA
    Sell Signal: When short-term MA crosses below long-term MA

    Formula:
        MA_short = SUM(price, period_short) / period_short
        MA_long = SUM(price, period_long) / period_long
        Signal: BUY when MA_short > MA_long (and was <= previously)
                SELL when MA_short < MA_long (and was >= previously)
    """

    def __init__(self, short_period: int = 20, long_period: int = 50):
        """Initialize with MA periods"""
        self.short_period = short_period
        self.long_period = long_period
        self.ma_short = None
        self.ma_long = None
        self.prev_ma_short = None
        self.prev_ma_long = None

    def calculate(self, prices: np.ndarray) -> Dict:
        """
        Calculate dual moving average crossover signals

        Args:
            prices: Array of closing prices

        Returns:
            Dictionary with MAs and signals
        """
        df = pd.DataFrame({'close': prices})

        # Simple Moving Averages
        self.ma_short = df['close'].rolling(window=self.short_period).mean().values
        self.ma_long = df['close'].rolling(window=self.long_period).mean().values

        signals = []

        for i in range(max(self.short_period, self.long_period), len(prices)):
            if np.isnan(self.ma_short[i]) or np.isnan(self.ma_long[i]):
                continue

            # Crossover detection
            prev_short = self.ma_short[i - 1]
            prev_long = self.ma_long[i - 1]
            curr_short = self.ma_short[i]
            curr_long = self.ma_long[i]

            if prev_short <= prev_long and curr_short > curr_long:
                signals.append(Signal(i, 'BUY', prices[i], 'Dual MA Crossover', 0.7))
            elif prev_short >= prev_long and curr_short < curr_long:
                signals.append(Signal(i, 'SELL', prices[i], 'Dual MA Crossover', 0.7))

        return {
            'ma_short': self.ma_short,
            'ma_long': self.ma_long,
            'signals': signals
        }


class TripleMovingAverageSystem:
    """
    Triple Moving Average System

    Uses three MAs for trend confirmation:
    - Fast (20-day)
    - Medium (50-day)
    - Slow (200-day)

    Buy Signal: All three in bullish alignment (fast > medium > slow) and fast crosses medium
    Sell Signal: All three in bearish alignment (fast < medium < slow) and fast crosses medium

    Formula:
        Bullish: MA_fast > MA_medium > MA_slow
        Bearish: MA_fast < MA_medium < MA_slow
    """

    def __init__(self, fast: int = 20, medium: int = 50, slow: int = 200):
        """Initialize with three MA periods"""
        self.fast = fast
        self.medium = medium
        self.slow = slow

    def calculate(self, prices: np.ndarray) -> Dict:
        """
        Calculate triple MA system

        Args:
            prices: Array of closing prices

        Returns:
            Dictionary with three MAs and signals
        """
        df = pd.DataFrame({'close': prices})

        ma_fast = df['close'].rolling(window=self.fast).mean().values
        ma_medium = df['close'].rolling(window=self.medium).mean().values
        ma_slow = df['close'].rolling(window=self.slow).mean().values

        signals = []
        trend_strength = []

        for i in range(max(self.fast, self.medium, self.slow), len(prices)):
            if np.isnan(ma_fast[i]) or np.isnan(ma_medium[i]) or np.isnan(ma_slow[i]):
                continue

            fast_val = ma_fast[i]
            medium_val = ma_medium[i]
            slow_val = ma_slow[i]

            prev_fast = ma_fast[i - 1]
            prev_medium = ma_medium[i - 1]

            # Bullish alignment and crossover
            if (fast_val > medium_val > slow_val and
                prev_fast <= prev_medium and fast_val > medium_val):
                strength = min(1.0, (fast_val - slow_val) / slow_val)
                signals.append(Signal(i, 'BUY', prices[i], 'Triple MA System', strength))
                trend_strength.append(strength)

            # Bearish alignment and crossover
            elif (fast_val < medium_val < slow_val and
                  prev_fast >= prev_medium and fast_val < medium_val):
                strength = min(1.0, (slow_val - fast_val) / slow_val)
                signals.append(Signal(i, 'SELL', prices[i], 'Triple MA System', strength))
                trend_strength.append(strength)

        return {
            'ma_fast': ma_fast,
            'ma_medium': ma_medium,
            'ma_slow': ma_slow,
            'signals': signals,
            'trend_strength': trend_strength
        }


class MACDIndicator:
    """
    MACD (Moving Average Convergence Divergence)

    Components:
    - MACD Line: 12-period EMA - 26-period EMA
    - Signal Line: 9-period EMA of MACD Line
    - Histogram: MACD Line - Signal Line

    Formulas:
        EMA_12 = price weighted by exponential factor (alpha = 2/13)
        EMA_26 = price weighted by exponential factor (alpha = 2/27)
        MACD = EMA_12 - EMA_26
        Signal = EMA_9(MACD)
        Histogram = MACD - Signal

    Signals:
    - BUY: MACD crosses above Signal line, or positive histogram increases
    - SELL: MACD crosses below Signal line, or negative histogram decreases
    """

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """Initialize with EMA periods"""
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def _ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calculate exponential moving average"""
        ema = np.zeros(len(prices))
        multiplier = 2 / (period + 1)

        ema[period - 1] = np.mean(prices[:period])

        for i in range(period, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i - 1] * (1 - multiplier))

        ema[:period - 1] = np.nan
        return ema

    def calculate(self, prices: np.ndarray) -> Dict:
        """
        Calculate MACD with histogram

        Args:
            prices: Array of closing prices

        Returns:
            Dictionary with MACD line, signal line, histogram, and signals
        """
        ema_fast = self._ema(prices, self.fast)
        ema_slow = self._ema(prices, self.slow)

        # MACD line
        macd_line = ema_fast - ema_slow

        # Signal line (EMA of MACD)
        signal_line = self._ema(macd_line, self.signal_period)

        # Histogram
        histogram = macd_line - signal_line

        signals = []

        for i in range(self.slow + self.signal_period - 1, len(prices)):
            if np.isnan(macd_line[i]) or np.isnan(signal_line[i]):
                continue

            prev_macd = macd_line[i - 1]
            prev_signal = signal_line[i - 1]
            curr_macd = macd_line[i]
            curr_signal = signal_line[i]

            # Crossover signals
            if prev_macd <= prev_signal and curr_macd > curr_signal and curr_macd > 0:
                strength = min(1.0, abs(histogram[i]) / (abs(macd_line[i]) + 1e-6))
                signals.append(Signal(i, 'BUY', prices[i], 'MACD', strength))

            elif prev_macd >= prev_signal and curr_macd < curr_signal and curr_macd < 0:
                strength = min(1.0, abs(histogram[i]) / (abs(macd_line[i]) + 1e-6))
                signals.append(Signal(i, 'SELL', prices[i], 'MACD', strength))

        return {
            'macd_line': macd_line,
            'signal_line': signal_line,
            'histogram': histogram,
            'signals': signals
        }


class ADXTrendStrength:
    """
    ADX (Average Directional Index) - Trend Strength Indicator

    Components:
    - +DM (Positive Directional Movement)
    - -DM (Negative Directional Movement)
    - +DI (Positive Directional Indicator)
    - -DI (Negative Directional Indicator)
    - ADX (Average Directional Index)

    Formulas:
        True Range = max(high - low, |high - close_prev|, |low - close_prev|)
        +DM = high - high_prev (if positive, else 0)
        -DM = low_prev - low (if positive, else 0)
        +DI = 100 * (Smoothed +DM / ATR)
        -DI = 100 * (Smoothed -DM / ATR)
        ADX = EMA(|+DI - -DI| / (+DI + -DI) * 100, period=14)

    Interpretation:
    - ADX > 25: Strong trend
    - ADX 20-25: Moderate trend
    - ADX < 20: Weak trend or ranging market
    - +DI > -DI: Uptrend
    - -DI > +DI: Downtrend
    """

    def __init__(self, period: int = 14):
        """Initialize ADX with period"""
        self.period = period

    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
        """
        Calculate ADX and directional indicators

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Dictionary with +DI, -DI, ADX, and signals
        """
        length = len(close)

        # True Range
        tr = np.zeros(length)
        tr[0] = high[0] - low[0]

        for i in range(1, length):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )

        # Directional Movement
        plus_dm = np.zeros(length)
        minus_dm = np.zeros(length)

        for i in range(1, length):
            high_diff = high[i] - high[i - 1]
            low_diff = low[i - 1] - low[i]

            if high_diff > 0 and high_diff > low_diff:
                plus_dm[i] = high_diff

            if low_diff > 0 and low_diff > high_diff:
                minus_dm[i] = low_diff

        # Smoothed values (using Wilder's smoothing)
        smoothed_tr = np.zeros(length)
        smoothed_plus = np.zeros(length)
        smoothed_minus = np.zeros(length)

        smoothed_tr[self.period - 1] = np.sum(tr[:self.period])
        smoothed_plus[self.period - 1] = np.sum(plus_dm[:self.period])
        smoothed_minus[self.period - 1] = np.sum(minus_dm[:self.period])

        for i in range(self.period, length):
            smoothed_tr[i] = smoothed_tr[i - 1] - (smoothed_tr[i - 1] / self.period) + tr[i]
            smoothed_plus[i] = smoothed_plus[i - 1] - (smoothed_plus[i - 1] / self.period) + plus_dm[i]
            smoothed_minus[i] = smoothed_minus[i - 1] - (smoothed_minus[i - 1] / self.period) + minus_dm[i]

        # Directional Indicators
        plus_di = np.zeros(length)
        minus_di = np.zeros(length)

        for i in range(self.period - 1, length):
            if smoothed_tr[i] != 0:
                plus_di[i] = 100 * (smoothed_plus[i] / smoothed_tr[i])
                minus_di[i] = 100 * (smoothed_minus[i] / smoothed_tr[i])

        # ADX calculation
        dx = np.zeros(length)
        for i in range(self.period - 1, length):
            di_sum = plus_di[i] + minus_di[i]
            if di_sum != 0:
                dx[i] = 100 * (abs(plus_di[i] - minus_di[i]) / di_sum)

        # ADX (EMA of DX)
        adx = np.zeros(length)
        adx[2 * self.period - 2] = np.mean(dx[self.period - 1:2 * self.period - 1])

        multiplier = 2 / (self.period + 1)
        for i in range(2 * self.period - 1, length):
            adx[i] = (adx[i - 1] * (1 - multiplier)) + (dx[i] * multiplier)

        plus_di[:self.period - 1] = np.nan
        minus_di[:self.period - 1] = np.nan
        adx[:2 * self.period - 2] = np.nan

        # Generate signals
        signals = []
        for i in range(2 * self.period - 1, length):
            if np.isnan(adx[i]):
                continue

            prev_plus = plus_di[i - 1]
            prev_minus = minus_di[i - 1]
            curr_plus = plus_di[i]
            curr_minus = minus_di[i]

            # Buy: +DI crosses above -DI and ADX > 20
            if (prev_plus <= prev_minus and curr_plus > curr_minus and adx[i] > 20):
                strength = min(1.0, adx[i] / 50)
                signals.append(Signal(i, 'BUY', close[i], 'ADX', strength))

            # Sell: -DI crosses above +DI and ADX > 20
            elif (prev_plus >= prev_minus and curr_plus < curr_minus and adx[i] > 20):
                strength = min(1.0, adx[i] / 50)
                signals.append(Signal(i, 'SELL', close[i], 'ADX', strength))

        return {
            'plus_di': plus_di,
            'minus_di': minus_di,
            'adx': adx,
            'signals': signals
        }


class TurtleTradingSystem:
    """
    Turtle Trading System - Breakout Strategy

    Rules:
    1. Long Entry: Price breaks above highest high of last N periods (default 20)
    2. Short Entry: Price breaks below lowest low of last N periods (default 20)
    3. Exit Long: Price falls below lowest low of last N periods (default 10)
    4. Exit Short: Price rises above highest high of last N periods (default 10)
    5. Position Sizing: Based on Average True Range (ATR)

    Formulas:
        Long Entry = max(high[i-N:i])
        Short Entry = min(low[i-N:i])
        Long Exit = min(low[i-M:i])
        Short Exit = max(high[i-M:i])
        Stop Loss = Entry Price - (2 * ATR)
        Take Profit = Entry Price + (3 * ATR)

    The original Turtle Traders used a 20/10 system:
    - Entry: 20-day breakout
    - Exit: 10-day breakout
    """

    def __init__(self, entry_period: int = 20, exit_period: int = 10):
        """Initialize Turtle Trading parameters"""
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.position = None  # 'LONG', 'SHORT', or None
        self.entry_price = None

    def _atr(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        length = len(close)
        tr = np.zeros(length)
        tr[0] = high[0] - low[0]

        for i in range(1, length):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )

        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr

    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
        """
        Calculate Turtle Trading signals

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Dictionary with breakout levels and signals
        """
        length = len(close)
        atr = self._atr(high, low, close)

        highest_entry = np.zeros(length)
        lowest_entry = np.zeros(length)
        highest_exit = np.zeros(length)
        lowest_exit = np.zeros(length)

        # Calculate breakout levels
        for i in range(self.entry_period, length):
            highest_entry[i] = np.max(high[i - self.entry_period:i])
            lowest_entry[i] = np.min(low[i - self.entry_period:i])

        for i in range(self.exit_period, length):
            highest_exit[i] = np.max(high[i - self.exit_period:i])
            lowest_exit[i] = np.min(low[i - self.exit_period:i])

        signals = []
        position = None
        entry_price = None
        entry_atr = None

        for i in range(max(self.entry_period, self.exit_period), length):
            if np.isnan(atr[i]):
                continue

            # Entry signals
            if position is None:
                # Long entry: breakout above 20-day high
                if i > self.entry_period and close[i] > highest_entry[i - 1]:
                    position = 'LONG'
                    entry_price = close[i]
                    entry_atr = atr[i]
                    strength = min(1.0, (close[i] - lowest_entry[i - 1]) / (highest_entry[i - 1] - lowest_entry[i - 1] + 1e-6))
                    signals.append(Signal(i, 'BUY', close[i], 'Turtle Trading', strength))

                # Short entry: breakout below 20-day low
                elif i > self.entry_period and close[i] < lowest_entry[i - 1]:
                    position = 'SHORT'
                    entry_price = close[i]
                    entry_atr = atr[i]
                    strength = min(1.0, (highest_entry[i - 1] - close[i]) / (highest_entry[i - 1] - lowest_entry[i - 1] + 1e-6))
                    signals.append(Signal(i, 'SELL', close[i], 'Turtle Trading', strength))

            # Exit signals
            else:
                if position == 'LONG':
                    # Exit: 10-day low breakout
                    if close[i] < lowest_exit[i - 1]:
                        position = None
                        signals.append(Signal(i, 'SELL', close[i], 'Turtle Trading', 0.6))

                elif position == 'SHORT':
                    # Exit: 10-day high breakout
                    if close[i] > highest_exit[i - 1]:
                        position = None
                        signals.append(Signal(i, 'BUY', close[i], 'Turtle Trading', 0.6))

        return {
            'highest_entry': highest_entry,
            'lowest_entry': lowest_entry,
            'highest_exit': highest_exit,
            'lowest_exit': lowest_exit,
            'atr': atr,
            'signals': signals
        }


class MomentumStrategy:
    """
    Comprehensive Momentum Strategy Manager

    Combines all five momentum strategies for signal generation and analysis
    """

    def __init__(self):
        """Initialize all strategies"""
        self.dual_ma = DualMovingAverageCrossover()
        self.triple_ma = TripleMovingAverageSystem()
        self.macd = MACDIndicator()
        self.adx = ADXTrendStrength()
        self.turtle = TurtleTradingSystem()

    def analyze(self, prices: np.ndarray, high: Optional[np.ndarray] = None,
                low: Optional[np.ndarray] = None) -> Dict:
        """
        Run all momentum strategies

        Args:
            prices: Array of closing prices
            high: Array of high prices (required for ADX and Turtle)
            low: Array of low prices (required for ADX and Turtle)

        Returns:
            Dictionary with results from all strategies
        """
        results = {
            'dual_ma': self.dual_ma.calculate(prices),
            'triple_ma': self.triple_ma.calculate(prices),
            'macd': self.macd.calculate(prices),
        }

        if high is not None and low is not None:
            results['adx'] = self.adx.calculate(high, low, prices)
            results['turtle'] = self.turtle.calculate(high, low, prices)

        return results

    def get_consensus_signal(self, prices: np.ndarray, high: Optional[np.ndarray] = None,
                            low: Optional[np.ndarray] = None) -> List[Signal]:
        """
        Get consensus signals from multiple strategies

        Args:
            prices: Array of closing prices
            high: Array of high prices (optional)
            low: Array of low prices (optional)

        Returns:
            List of signals with consensus strength
        """
        results = self.analyze(prices, high, low)

        # Collect all signals
        all_signals = {}

        for strategy_name, strategy_results in results.items():
            for signal in strategy_results.get('signals', []):
                key = (signal.timestamp, signal.signal_type)
                if key not in all_signals:
                    all_signals[key] = []
                all_signals[key].append(signal)

        # Calculate consensus
        consensus_signals = []
        for (timestamp, signal_type), signals in all_signals.items():
            avg_strength = np.mean([s.strength for s in signals])
            consensus_signal = Signal(
                timestamp,
                signal_type,
                signals[0].price,
                f"Consensus ({len(signals)} strategies)",
                avg_strength
            )
            consensus_signals.append(consensus_signal)

        return sorted(consensus_signals, key=lambda x: x.timestamp)


# Example usage and testing
if __name__ == "__main__":
    # Generate sample price data (in production, use real market data)
    np.random.seed(42)
    n_periods = 300
    prices = 100 + np.cumsum(np.random.randn(n_periods) * 2)
    high = prices + np.abs(np.random.randn(n_periods))
    low = prices - np.abs(np.random.randn(n_periods))

    print("=" * 60)
    print("MOMENTUM AND TREND FOLLOWING STRATEGIES")
    print("=" * 60)

    # Test each strategy
    print("\n1. DUAL MOVING AVERAGE CROSSOVER")
    print("-" * 60)
    dual_ma = DualMovingAverageCrossover(short_period=20, long_period=50)
    dual_result = dual_ma.calculate(prices)
    print(f"Generated {len(dual_result['signals'])} signals")
    if dual_result['signals']:
        print(f"First signal: {dual_result['signals'][0]}")

    print("\n2. TRIPLE MOVING AVERAGE SYSTEM")
    print("-" * 60)
    triple_ma = TripleMovingAverageSystem(fast=20, medium=50, slow=200)
    triple_result = triple_ma.calculate(prices)
    print(f"Generated {len(triple_result['signals'])} signals")
    if triple_result['signals']:
        print(f"First signal: {triple_result['signals'][0]}")

    print("\n3. MACD WITH HISTOGRAM")
    print("-" * 60)
    macd = MACDIndicator(fast=12, slow=26, signal=9)
    macd_result = macd.calculate(prices)
    print(f"Generated {len(macd_result['signals'])} signals")
    if macd_result['signals']:
        print(f"First signal: {macd_result['signals'][0]}")
    print(f"MACD range: [{np.nanmin(macd_result['macd_line']):.2f}, {np.nanmax(macd_result['macd_line']):.2f}]")

    print("\n4. ADX TREND STRENGTH")
    print("-" * 60)
    adx = ADXTrendStrength(period=14)
    adx_result = adx.calculate(high, low, prices)
    print(f"Generated {len(adx_result['signals'])} signals")
    if adx_result['signals']:
        print(f"First signal: {adx_result['signals'][0]}")
    print(f"ADX range: [{np.nanmin(adx_result['adx']):.2f}, {np.nanmax(adx_result['adx']):.2f}]")

    print("\n5. TURTLE TRADING SYSTEM")
    print("-" * 60)
    turtle = TurtleTradingSystem(entry_period=20, exit_period=10)
    turtle_result = turtle.calculate(high, low, prices)
    print(f"Generated {len(turtle_result['signals'])} signals")
    if turtle_result['signals']:
        print(f"First signal: {turtle_result['signals'][0]}")

    print("\n6. CONSENSUS SIGNALS")
    print("-" * 60)
    momentum = MomentumStrategy()
    consensus = momentum.get_consensus_signal(prices, high, low)
    print(f"Generated {len(consensus)} consensus signals")
    if consensus:
        print(f"First consensus signal: {consensus[0]}")
        high_confidence = [s for s in consensus if s.strength > 0.7]
        print(f"High confidence signals: {len(high_confidence)}")
