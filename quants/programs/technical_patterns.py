"""
Technical Analysis Pattern Recognition System

This module implements comprehensive technical analysis patterns:
1. Candlestick Pattern Recognition (Engulfing, Hammer, Doji, etc.)
2. Support/Resistance Level Identification
3. Fibonacci Retracement Levels
4. Chart Pattern Detection (Head & Shoulders, Triangles, etc.)
5. Pattern-Based Trading Signals
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class PatternSignalType(Enum):
    """Pattern signal types"""
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass
class PatternSignal:
    """Trading signal from pattern recognition"""
    timestamp: int
    pattern_name: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    price: float
    confidence: float  # 0-1 confidence score
    pattern_direction: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    entry_level: float
    stop_loss: float
    take_profit: Optional[float] = None


class CandlestickPatterns:
    """
    Candlestick Pattern Recognition

    Identifies reversal and continuation patterns in candlestick data.
    Uses open, high, low, close (OHLC) price data.
    """

    def __init__(self, atr_multiplier: float = 0.3):
        """Initialize with ATR multiplier for pattern thresholds"""
        self.atr_multiplier = atr_multiplier

    def _calculate_atr(self, high: np.ndarray, low: np.ndarray,
                       close: np.ndarray, period: int = 14) -> np.ndarray:
        """Calculate Average True Range"""
        tr = np.zeros(len(close))
        tr[0] = high[0] - low[0]

        for i in range(1, len(close)):
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1])
            )

        atr = pd.Series(tr).rolling(window=period).mean().values
        return atr

    def _get_body_size(self, open_price: float, close: float) -> float:
        """Get candlestick body size"""
        return abs(close - open_price)

    def _get_shadow_size(self, high: float, low: float, body_size: float) -> Tuple[float, float]:
        """Get upper and lower shadow sizes"""
        mid = (high + low) / 2
        upper_shadow = high - max(high - body_size / 2, low + body_size / 2)
        lower_shadow = min(high - body_size / 2, low + body_size / 2) - low
        return upper_shadow, lower_shadow

    def recognize_patterns(self, open_prices: np.ndarray, high: np.ndarray,
                          low: np.ndarray, close: np.ndarray) -> List[PatternSignal]:
        """
        Recognize candlestick patterns in OHLC data

        Args:
            open_prices: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            List of identified pattern signals
        """
        signals = []
        atr = self._calculate_atr(high, low, close)

        # Require at least 3 candles for patterns
        for i in range(2, len(close)):
            if np.isnan(atr[i]):
                continue

            threshold = atr[i] * self.atr_multiplier

            # Hammer (reversal)
            hammer = self._detect_hammer(open_prices, high, low, close, i, threshold)
            if hammer:
                signals.append(hammer)

            # Inverse Hammer (reversal)
            inv_hammer = self._detect_inverse_hammer(open_prices, high, low, close, i, threshold)
            if inv_hammer:
                signals.append(inv_hammer)

            # Doji (indecision)
            doji = self._detect_doji(open_prices, high, low, close, i, threshold)
            if doji:
                signals.append(doji)

            # Engulfing patterns (reversal)
            if i >= 1:
                engulfing = self._detect_engulfing(open_prices, high, low, close, i, threshold)
                if engulfing:
                    signals.append(engulfing)

            # Harami patterns (reversal)
            if i >= 1:
                harami = self._detect_harami(open_prices, high, low, close, i, threshold)
                if harami:
                    signals.append(harami)

        return signals

    def _detect_hammer(self, open_prices: np.ndarray, high: np.ndarray,
                      low: np.ndarray, close: np.ndarray, i: int, threshold: float) -> Optional[PatternSignal]:
        """
        Detect Hammer pattern (bullish reversal)
        - Small body at top
        - Long lower shadow (2x+ body length)
        - Minimal upper shadow
        """
        body = self._get_body_size(open_prices[i], close[i])
        upper_shadow, lower_shadow = self._get_shadow_size(high[i], low[i], body)

        if (body > 0 and lower_shadow > 2 * body and
            upper_shadow < body / 2 and close[i] >= open_prices[i]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Hammer",
                signal_type="BUY",
                price=close[i],
                confidence=0.7,
                pattern_direction="BULLISH",
                entry_level=close[i],
                stop_loss=low[i] - threshold,
                take_profit=close[i] + (close[i] - low[i])
            )
        return None

    def _detect_inverse_hammer(self, open_prices: np.ndarray, high: np.ndarray,
                              low: np.ndarray, close: np.ndarray, i: int, threshold: float) -> Optional[PatternSignal]:
        """
        Detect Inverse Hammer pattern (bullish reversal)
        - Small body at bottom
        - Long upper shadow (2x+ body length)
        - Minimal lower shadow
        """
        body = self._get_body_size(open_prices[i], close[i])
        upper_shadow, lower_shadow = self._get_shadow_size(high[i], low[i], body)

        if (body > 0 and upper_shadow > 2 * body and
            lower_shadow < body / 2 and close[i] <= open_prices[i]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Inverse Hammer",
                signal_type="BUY",
                price=close[i],
                confidence=0.65,
                pattern_direction="BULLISH",
                entry_level=close[i],
                stop_loss=low[i] - threshold,
                take_profit=high[i] + (high[i] - low[i])
            )
        return None

    def _detect_doji(self, open_prices: np.ndarray, high: np.ndarray,
                    low: np.ndarray, close: np.ndarray, i: int, threshold: float) -> Optional[PatternSignal]:
        """
        Detect Doji pattern (indecision)
        - Opening price approximately equals closing price
        - Long shadows on both sides
        - Indicates indecision and potential reversal
        """
        body = self._get_body_size(open_prices[i], close[i])
        total_range = high[i] - low[i]

        if body <= total_range * 0.05 and total_range > 0:
            return PatternSignal(
                timestamp=i,
                pattern_name="Doji",
                signal_type="HOLD",
                price=close[i],
                confidence=0.6,
                pattern_direction="NEUTRAL",
                entry_level=close[i],
                stop_loss=low[i] - threshold,
                take_profit=high[i] + threshold
            )
        return None

    def _detect_engulfing(self, open_prices: np.ndarray, high: np.ndarray,
                         low: np.ndarray, close: np.ndarray, i: int, threshold: float) -> Optional[PatternSignal]:
        """
        Detect Engulfing pattern (reversal)
        - Current candle completely engulfs previous candle
        - Bullish: white candle engulfs black candle
        - Bearish: black candle engulfs white candle
        """
        curr_body = self._get_body_size(open_prices[i], close[i])
        prev_body = self._get_body_size(open_prices[i-1], close[i-1])

        # Bullish engulfing
        if (close[i] > open_prices[i] and close[i-1] <= open_prices[i-1] and
            open_prices[i] < close[i-1] and close[i] > open_prices[i-1]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Bullish Engulfing",
                signal_type="BUY",
                price=close[i],
                confidence=0.75,
                pattern_direction="BULLISH",
                entry_level=close[i],
                stop_loss=low[i] - threshold,
                take_profit=close[i] + (close[i] - open_prices[i])
            )

        # Bearish engulfing
        if (close[i] < open_prices[i] and close[i-1] >= open_prices[i-1] and
            open_prices[i] > close[i-1] and close[i] < open_prices[i-1]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Bearish Engulfing",
                signal_type="SELL",
                price=close[i],
                confidence=0.75,
                pattern_direction="BEARISH",
                entry_level=close[i],
                stop_loss=high[i] + threshold,
                take_profit=close[i] - (open_prices[i] - close[i])
            )

        return None

    def _detect_harami(self, open_prices: np.ndarray, high: np.ndarray,
                      low: np.ndarray, close: np.ndarray, i: int, threshold: float) -> Optional[PatternSignal]:
        """
        Detect Harami pattern (reversal, weaker than engulfing)
        - Current candle is completely inside previous candle range
        - Indicates potential reversal
        """
        # Bullish harami
        if (close[i] > open_prices[i] and close[i-1] <= open_prices[i-1] and
            open_prices[i] > low[i-1] and close[i] < high[i-1] and
            open_prices[i] >= close[i-1] and close[i] <= open_prices[i-1]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Bullish Harami",
                signal_type="BUY",
                price=close[i],
                confidence=0.65,
                pattern_direction="BULLISH",
                entry_level=close[i],
                stop_loss=low[i] - threshold,
                take_profit=high[i-1]
            )

        # Bearish harami
        if (close[i] < open_prices[i] and close[i-1] >= open_prices[i-1] and
            open_prices[i] < high[i-1] and close[i] > low[i-1] and
            open_prices[i] <= open_prices[i-1] and close[i] >= close[i-1]):
            return PatternSignal(
                timestamp=i,
                pattern_name="Bearish Harami",
                signal_type="SELL",
                price=close[i],
                confidence=0.65,
                pattern_direction="BEARISH",
                entry_level=close[i],
                stop_loss=high[i] + threshold,
                take_profit=low[i-1]
            )

        return None


class SupportResistance:
    """
    Support and Resistance Level Identification

    Identifies key price levels where buying/selling pressure changes.
    Uses pivot points, local minima/maxima, and price clustering.
    """

    def __init__(self, lookback_period: int = 20, min_touches: int = 2):
        """
        Initialize support/resistance finder

        Args:
            lookback_period: Number of periods to analyze for levels
            min_touches: Minimum number of touches to confirm a level
        """
        self.lookback_period = lookback_period
        self.min_touches = min_touches

    def identify_levels(self, high: np.ndarray, low: np.ndarray,
                       close: np.ndarray) -> Dict:
        """
        Identify support and resistance levels

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Dictionary with support and resistance levels
        """
        # Find local extrema
        resistance_levels = self._find_resistance(high)
        support_levels = self._find_support(low)

        # Calculate pivot points (more recent)
        pivot_points = self._calculate_pivots(high, low, close)

        # Find price clusters
        clusters = self._find_price_clusters(close)

        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'pivot_points': pivot_points,
            'price_clusters': clusters
        }

    def _find_resistance(self, high: np.ndarray) -> List[Tuple[int, float]]:
        """Find resistance levels (local maxima)"""
        resistance = []
        window = 5

        for i in range(window, len(high) - window):
            if np.isnan(high[i]):
                continue

            # Check if local maximum
            is_local_max = high[i] >= np.max(high[i-window:i]) and \
                          high[i] >= np.max(high[i+1:i+window+1])

            if is_local_max:
                # Check for multiple touches
                touches = np.sum(np.abs(high[max(0, i-self.lookback_period):i+self.lookback_period] - high[i]) < high[i] * 0.01)

                if touches >= self.min_touches:
                    resistance.append((i, high[i]))

        return resistance

    def _find_support(self, low: np.ndarray) -> List[Tuple[int, float]]:
        """Find support levels (local minima)"""
        support = []
        window = 5

        for i in range(window, len(low) - window):
            if np.isnan(low[i]):
                continue

            # Check if local minimum
            is_local_min = low[i] <= np.min(low[i-window:i]) and \
                          low[i] <= np.min(low[i+1:i+window+1])

            if is_local_min:
                # Check for multiple touches
                touches = np.sum(np.abs(low[max(0, i-self.lookback_period):i+self.lookback_period] - low[i]) < low[i] * 0.01)

                if touches >= self.min_touches:
                    support.append((i, low[i]))

        return support

    def _calculate_pivots(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
        """
        Calculate pivot points for current period

        Formulas:
        Pivot = (High + Low + Close) / 3
        R1 = (2 * Pivot) - Low
        R2 = Pivot + (High - Low)
        S1 = (2 * Pivot) - High
        S2 = Pivot - (High - Low)
        """
        # Use last known values
        h = high[-1]
        l = low[-1]
        c = close[-1]

        pivot = (h + l + c) / 3
        r1 = (2 * pivot) - l
        r2 = pivot + (h - l)
        s1 = (2 * pivot) - h
        s2 = pivot - (h - l)

        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2
        }

    def _find_price_clusters(self, close: np.ndarray, num_clusters: int = 5) -> List[Tuple[float, int]]:
        """Find price clustering levels using histogram"""
        # Use last lookback_period for clustering
        recent_prices = close[-self.lookback_period:]

        # Create histogram of prices
        hist, bin_edges = np.histogram(recent_prices[~np.isnan(recent_prices)], bins=num_clusters)

        clusters = []
        for i, count in enumerate(hist):
            if count > 0:
                cluster_price = (bin_edges[i] + bin_edges[i+1]) / 2
                clusters.append((cluster_price, count))

        return sorted(clusters, key=lambda x: x[1], reverse=True)


class FibonacciRetracement:
    """
    Fibonacci Retracement Level Calculator

    Calculates standard Fibonacci retracement levels (23.6%, 38.2%, 50%, 61.8%, 78.6%)
    and extension levels for potential reversal zones.
    """

    # Standard Fibonacci ratios
    STANDARD_LEVELS = [0.236, 0.382, 0.5, 0.618, 0.786]
    EXTENSION_LEVELS = [1.618, 2.618, 3.618]

    def calculate_retracement(self, high: np.ndarray, low: np.ndarray,
                             price: float) -> Dict:
        """
        Calculate Fibonacci retracement levels

        Args:
            high: Array of high prices
            low: Array of low prices
            price: Current price for reference

        Returns:
            Dictionary with retracement levels
        """
        # Find the swing high and swing low in recent data
        swing_high = np.nanmax(high[-252:])  # Last year of data
        swing_low = np.nanmin(low[-252:])

        diff = swing_high - swing_low

        retracement_levels = {}

        # Calculate retracement levels
        for level in self.STANDARD_LEVELS:
            retracement_level = swing_high - (diff * level)
            retracement_levels[f'{level*100:.1f}%'] = retracement_level

        # Calculate extension levels (beyond the swing high)
        for level in self.EXTENSION_LEVELS:
            extension_level = swing_high + (diff * (level - 1))
            retracement_levels[f'{level*100:.1f}% Extension'] = extension_level

        retracement_levels['Swing High'] = swing_high
        retracement_levels['Swing Low'] = swing_low

        return retracement_levels

    def find_fibonacci_signals(self, high: np.ndarray, low: np.ndarray,
                               close: np.ndarray) -> List[PatternSignal]:
        """
        Generate signals when price reaches Fibonacci levels

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            List of signals at Fibonacci levels
        """
        signals = []
        fibs = self.calculate_retracement(high, low, close[-1])

        # Check current price relationship to Fibonacci levels
        current_price = close[-1]

        # Support at 61.8% (strongest Fibonacci support)
        fib_618 = fibs['61.8%']
        if current_price < fib_618 * 1.02 and current_price > fib_618 * 0.98:
            signals.append(PatternSignal(
                timestamp=len(close) - 1,
                pattern_name="Fibonacci 61.8% Support",
                signal_type="BUY",
                price=current_price,
                confidence=0.65,
                pattern_direction="BULLISH",
                entry_level=current_price,
                stop_loss=fibs['78.6%'],
                take_profit=fibs['38.2%']
            ))

        # Resistance at 38.2%
        fib_382 = fibs['38.2%']
        if current_price > fib_382 * 0.98 and current_price < fib_382 * 1.02:
            signals.append(PatternSignal(
                timestamp=len(close) - 1,
                pattern_name="Fibonacci 38.2% Resistance",
                signal_type="SELL",
                price=current_price,
                confidence=0.65,
                pattern_direction="BEARISH",
                entry_level=current_price,
                stop_loss=fibs['23.6%'],
                take_profit=fibs['61.8%']
            ))

        return signals


class ChartPatterns:
    """
    Chart Pattern Detection

    Detects larger chart patterns:
    - Head and Shoulders
    - Triangles (Ascending, Descending, Symmetric)
    - Double Top/Bottom
    - Cup and Handle
    """

    def __init__(self, min_pattern_bars: int = 10):
        """Initialize with minimum bars to form pattern"""
        self.min_pattern_bars = min_pattern_bars

    def detect_patterns(self, high: np.ndarray, low: np.ndarray,
                       close: np.ndarray) -> List[PatternSignal]:
        """
        Detect major chart patterns

        Args:
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            List of detected chart patterns
        """
        signals = []

        # Detect Head and Shoulders
        h_and_s = self._detect_head_and_shoulders(high, low, close)
        if h_and_s:
            signals.append(h_and_s)

        # Detect Triangles
        triangles = self._detect_triangles(high, low, close)
        signals.extend(triangles)

        # Detect Double Top/Bottom
        double_patterns = self._detect_double_patterns(high, low, close)
        signals.extend(double_patterns)

        # Detect Cup and Handle
        cup = self._detect_cup_and_handle(high, low, close)
        if cup:
            signals.append(cup)

        return signals

    def _detect_head_and_shoulders(self, high: np.ndarray, low: np.ndarray,
                                   close: np.ndarray) -> Optional[PatternSignal]:
        """
        Detect Head and Shoulders pattern
        - Three peaks: left shoulder, head (highest), right shoulder
        - Neckline connects the lows between peaks
        """
        # Look for pattern in last 50 bars
        window = min(50, len(high) - 1)
        recent_high = high[-window:]
        recent_low = low[-window:]

        if len(recent_high) < self.min_pattern_bars:
            return None

        # Find three local maxima
        peaks = []
        for i in range(2, len(recent_high) - 2):
            if (recent_high[i] > recent_high[i-1] and
                recent_high[i] > recent_high[i-2] and
                recent_high[i] > recent_high[i+1] and
                recent_high[i] > recent_high[i+2]):
                peaks.append((i, recent_high[i]))

        if len(peaks) >= 3:
            # Check for head and shoulders pattern (middle peak highest)
            if peaks[1][1] > peaks[0][1] and peaks[1][1] > peaks[2][1]:
                # Similar shoulder heights
                if 0.95 < peaks[0][1] / peaks[2][1] < 1.05:
                    neckline = (recent_low[peaks[0][0]] + recent_low[peaks[1][0]]) / 2

                    return PatternSignal(
                        timestamp=len(high) - 1,
                        pattern_name="Head and Shoulders",
                        signal_type="SELL",
                        price=close[-1],
                        confidence=0.7,
                        pattern_direction="BEARISH",
                        entry_level=neckline,
                        stop_loss=peaks[1][1],
                        take_profit=neckline - (peaks[1][1] - neckline)
                    )

        return None

    def _detect_triangles(self, high: np.ndarray, low: np.ndarray,
                         close: np.ndarray) -> List[PatternSignal]:
        """
        Detect triangle patterns (ascending, descending, symmetric)
        """
        signals = []
        window = min(40, len(high) - 1)

        if window < self.min_pattern_bars:
            return signals

        # Find trend lines
        recent_high = high[-window:]
        recent_low = low[-window:]

        # Calculate slopes of highs and lows
        x = np.arange(len(recent_high))

        # Fit lines to highs and lows
        try:
            poly_high = np.polyfit(x, recent_high, 1)
            poly_low = np.polyfit(x, recent_low, 1)

            slope_high = poly_high[0]
            slope_low = poly_low[0]

            # Ascending triangle: lows rising, highs flat
            if slope_low > 0.0005 and abs(slope_high) < 0.0005:
                return [PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Ascending Triangle",
                    signal_type="BUY",
                    price=close[-1],
                    confidence=0.65,
                    pattern_direction="BULLISH",
                    entry_level=recent_high[-1],
                    stop_loss=recent_low[-1],
                    take_profit=recent_high[-1] + (recent_high[-1] - recent_low[-1])
                )]

            # Descending triangle: highs falling, lows flat
            if slope_high < -0.0005 and abs(slope_low) < 0.0005:
                return [PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Descending Triangle",
                    signal_type="SELL",
                    price=close[-1],
                    confidence=0.65,
                    pattern_direction="BEARISH",
                    entry_level=recent_low[-1],
                    stop_loss=recent_high[-1],
                    take_profit=recent_low[-1] - (recent_high[-1] - recent_low[-1])
                )]

            # Symmetric triangle: both converging
            if slope_high < -0.0002 and slope_low > 0.0002:
                return [PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Symmetric Triangle",
                    signal_type="HOLD",
                    price=close[-1],
                    confidence=0.6,
                    pattern_direction="NEUTRAL",
                    entry_level=close[-1],
                    stop_loss=recent_low[-1],
                    take_profit=recent_high[-1]
                )]
        except:
            pass

        return signals

    def _detect_double_patterns(self, high: np.ndarray, low: np.ndarray,
                               close: np.ndarray) -> List[PatternSignal]:
        """
        Detect Double Top and Double Bottom patterns
        """
        signals = []
        window = min(50, len(high) - 1)

        recent_high = high[-window:]
        recent_low = low[-window:]

        if window < self.min_pattern_bars:
            return signals

        # Find two peaks with similar height
        max_idx = np.argsort(recent_high)[-3:]  # Top 3 highs
        if len(max_idx) >= 2:
            idx1, idx2 = max_idx[-1], max_idx[-2]

            if abs(recent_high[idx1] - recent_high[idx2]) / recent_high[idx1] < 0.02:
                # Double top
                midpoint_low = np.min(recent_low[min(idx1, idx2):max(idx1, idx2)])

                signals.append(PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Double Top",
                    signal_type="SELL",
                    price=close[-1],
                    confidence=0.65,
                    pattern_direction="BEARISH",
                    entry_level=midpoint_low,
                    stop_loss=max(recent_high[idx1], recent_high[idx2]),
                    take_profit=midpoint_low - (recent_high[idx1] - midpoint_low)
                ))

        # Find two troughs with similar depth
        min_idx = np.argsort(recent_low)[:3]  # Bottom 3 lows
        if len(min_idx) >= 2:
            idx1, idx2 = min_idx[0], min_idx[1]

            if abs(recent_low[idx1] - recent_low[idx2]) / recent_low[idx1] < 0.02:
                # Double bottom
                midpoint_high = np.max(recent_high[min(idx1, idx2):max(idx1, idx2)])

                signals.append(PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Double Bottom",
                    signal_type="BUY",
                    price=close[-1],
                    confidence=0.65,
                    pattern_direction="BULLISH",
                    entry_level=midpoint_high,
                    stop_loss=min(recent_low[idx1], recent_low[idx2]),
                    take_profit=midpoint_high + (midpoint_high - recent_low[idx1])
                ))

        return signals

    def _detect_cup_and_handle(self, high: np.ndarray, low: np.ndarray,
                              close: np.ndarray) -> Optional[PatternSignal]:
        """
        Detect Cup and Handle pattern (bullish continuation)
        - Cup: U-shaped with rounded bottom
        - Handle: Small pullback after cup
        """
        window = min(60, len(high) - 1)

        if window < self.min_pattern_bars:
            return None

        recent_high = high[-window:]
        recent_low = low[-window:]
        recent_close = close[-window:]

        # Find the cup (low point)
        cup_low_idx = np.nanargmin(recent_low)

        # Check if there's a handle (recent pullback)
        handle_high_idx = np.nanargmax(recent_high[cup_low_idx:])
        handle_high = recent_high[cup_low_idx + handle_high_idx]

        # Cup should be deeper than handle pullback
        if handle_high > recent_low[cup_low_idx] * 1.05:
            cup_size = handle_high - recent_low[cup_low_idx]

            if recent_close[-1] > handle_high * 0.99:
                return PatternSignal(
                    timestamp=len(high) - 1,
                    pattern_name="Cup and Handle",
                    signal_type="BUY",
                    price=close[-1],
                    confidence=0.68,
                    pattern_direction="BULLISH",
                    entry_level=handle_high,
                    stop_loss=recent_low[cup_low_idx],
                    take_profit=handle_high + cup_size
                )

        return None


class TechnicalPatternAnalyzer:
    """
    Comprehensive Technical Pattern Analyzer

    Combines all pattern recognition systems for complete technical analysis.
    """

    def __init__(self):
        """Initialize all pattern recognition systems"""
        self.candlestick = CandlestickPatterns()
        self.support_resistance = SupportResistance()
        self.fibonacci = FibonacciRetracement()
        self.chart_patterns = ChartPatterns()

    def analyze(self, open_prices: np.ndarray, high: np.ndarray,
               low: np.ndarray, close: np.ndarray) -> Dict:
        """
        Perform comprehensive technical pattern analysis

        Args:
            open_prices: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Dictionary with all pattern analysis results
        """
        results = {
            'candlestick_patterns': self.candlestick.recognize_patterns(
                open_prices, high, low, close
            ),
            'support_resistance': self.support_resistance.identify_levels(
                high, low, close
            ),
            'fibonacci_levels': self.fibonacci.calculate_retracement(
                high, low, close[-1]
            ),
            'fibonacci_signals': self.fibonacci.find_fibonacci_signals(
                high, low, close
            ),
            'chart_patterns': self.chart_patterns.detect_patterns(
                high, low, close
            )
        }

        return results

    def get_all_signals(self, open_prices: np.ndarray, high: np.ndarray,
                       low: np.ndarray, close: np.ndarray) -> List[PatternSignal]:
        """
        Get all signals from all pattern recognition systems

        Args:
            open_prices: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices

        Returns:
            Sorted list of all pattern signals
        """
        all_signals = []

        results = self.analyze(open_prices, high, low, close)

        all_signals.extend(results['candlestick_patterns'])
        all_signals.extend(results['fibonacci_signals'])
        all_signals.extend(results['chart_patterns'])

        # Sort by timestamp
        return sorted(all_signals, key=lambda x: x.timestamp)

    def get_high_confidence_signals(self, open_prices: np.ndarray, high: np.ndarray,
                                   low: np.ndarray, close: np.ndarray,
                                   min_confidence: float = 0.65) -> List[PatternSignal]:
        """
        Get only high-confidence signals

        Args:
            open_prices: Array of opening prices
            high: Array of high prices
            low: Array of low prices
            close: Array of closing prices
            min_confidence: Minimum confidence threshold (0-1)

        Returns:
            Filtered list of high-confidence signals
        """
        all_signals = self.get_all_signals(open_prices, high, low, close)
        return [s for s in all_signals if s.confidence >= min_confidence]


# Example usage and testing
if __name__ == "__main__":
    # Generate sample price data
    np.random.seed(42)
    n_periods = 300
    prices = 100 + np.cumsum(np.random.randn(n_periods) * 2)
    high = prices + np.abs(np.random.randn(n_periods) * 0.5)
    low = prices - np.abs(np.random.randn(n_periods) * 0.5)
    open_prices = prices + np.random.randn(n_periods) * 0.5

    print("=" * 70)
    print("TECHNICAL PATTERN RECOGNITION SYSTEM")
    print("=" * 70)

    # Initialize analyzer
    analyzer = TechnicalPatternAnalyzer()

    # Get all analysis
    results = analyzer.analyze(open_prices, high, low, prices)

    print("\n1. CANDLESTICK PATTERNS")
    print("-" * 70)
    print(f"Detected {len(results['candlestick_patterns'])} candlestick patterns")
    for signal in results['candlestick_patterns'][-3:]:
        print(f"  {signal.pattern_name}: {signal.signal_type} (confidence: {signal.confidence:.2f})")

    print("\n2. SUPPORT & RESISTANCE LEVELS")
    print("-" * 70)
    sr_levels = results['support_resistance']
    print(f"Support Levels: {len(sr_levels['support_levels'])}")
    print(f"Resistance Levels: {len(sr_levels['resistance_levels'])}")
    print(f"Pivot: {sr_levels['pivot_points']['pivot']:.2f}")
    print(f"S1: {sr_levels['pivot_points']['s1']:.2f}, R1: {sr_levels['pivot_points']['r1']:.2f}")

    print("\n3. FIBONACCI RETRACEMENT LEVELS")
    print("-" * 70)
    fib_levels = results['fibonacci_levels']
    print(f"Swing High: {fib_levels['Swing High']:.2f}")
    print(f"Swing Low: {fib_levels['Swing Low']:.2f}")
    print(f"61.8% Level: {fib_levels['61.8%']:.2f}")
    print(f"38.2% Level: {fib_levels['38.2%']:.2f}")

    print("\n4. CHART PATTERNS")
    print("-" * 70)
    print(f"Detected {len(results['chart_patterns'])} chart patterns")
    for signal in results['chart_patterns']:
        print(f"  {signal.pattern_name}: {signal.signal_type} (confidence: {signal.confidence:.2f})")

    print("\n5. HIGH CONFIDENCE SIGNALS")
    print("-" * 70)
    high_conf = analyzer.get_high_confidence_signals(open_prices, high, low, prices, min_confidence=0.70)
    print(f"Total high-confidence signals (>0.70): {len(high_conf)}")
    for signal in high_conf[-5:]:
        print(f"  {signal.pattern_name}: {signal.signal_type}")
