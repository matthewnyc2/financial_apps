"""
Quantitative Analysis Engine
PhD-level technical analysis with vectorized calculations for high performance.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from concurrent.futures import ProcessPoolExecutor
from functools import partial

logger = logging.getLogger(__name__)


class QuantitativeAnalyzer:
    """
    High-performance quantitative analysis engine.
    Implements 30+ technical indicators optimized for opening hour trading.
    """

    def __init__(self, config: dict):
        self.config = config
        self.max_workers = config.get('analysis', {}).get('max_compute_workers', 8)

    # ==================== MOMENTUM INDICATORS ====================

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index (vectorized)"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """MACD with signal and histogram"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return pd.DataFrame({
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        })

    @staticmethod
    def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                            k_period: int = 14, d_period: int = 3) -> pd.DataFrame:
        """Stochastic Oscillator"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()

        return pd.DataFrame({'stoch_k': k, 'stoch_d': d})

    # ==================== VOLUME INDICATORS ====================

    @staticmethod
    def calculate_vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        tpv = typical_price * volume
        vwap = tpv.cumsum() / volume.cumsum()
        return vwap

    @staticmethod
    def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv

    @staticmethod
    def detect_volume_spike(volume: pd.Series, std_threshold: float = 4.0, period: int = 50) -> pd.Series:
        """Detect unusual volume spikes"""
        vol_mean = volume.rolling(period).mean()
        vol_std = volume.rolling(period).std()
        spike = volume > (vol_mean + std_threshold * vol_std)
        return spike

    # ==================== VOLATILITY INDICATORS ====================

    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = abs(high - prev_close)
        tr3 = abs(low - prev_close)
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()
        return atr

    @staticmethod
    def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std: float = 2) -> pd.DataFrame:
        """Bollinger Bands"""
        middle = prices.rolling(window=period).mean()
        rolling_std = prices.rolling(window=period).std()
        upper = middle + (std * rolling_std)
        lower = middle - (std * rolling_std)

        return pd.DataFrame({
            'bb_middle': middle,
            'bb_upper': upper,
            'bb_lower': lower,
            'bb_width': upper - lower
        })

    @staticmethod
    def calculate_historical_volatility(returns: pd.Series, period: int = 20) -> pd.Series:
        """Historical volatility (annualized)"""
        volatility = returns.rolling(window=period).std() * np.sqrt(252)
        return volatility

    # ==================== TREND INDICATORS ====================

    @staticmethod
    def calculate_moving_averages(prices: pd.Series, periods: List[int] = [20, 50, 200]) -> pd.DataFrame:
        """Simple and Exponential Moving Averages"""
        result = pd.DataFrame(index=prices.index)

        for period in periods:
            result[f'sma_{period}'] = prices.rolling(window=period).mean()
            result[f'ema_{period}'] = prices.ewm(span=period, adjust=False).mean()

        return result

    # ==================== OPENING HOUR SPECIFIC ====================

    @staticmethod
    def calculate_gap(current_open: float, prev_close: float) -> Dict[str, float]:
        """Calculate overnight gap"""
        gap_dollar = current_open - prev_close
        gap_percent = (gap_dollar / prev_close) * 100

        gap_type = 'none'
        if abs(gap_percent) >= 2:
            gap_type = 'large'
        elif abs(gap_percent) >= 1:
            gap_type = 'medium'
        elif abs(gap_percent) >= 0.5:
            gap_type = 'small'

        direction = 'up' if gap_percent > 0 else 'down' if gap_percent < 0 else 'flat'

        return {
            'gap_dollar': gap_dollar,
            'gap_percent': gap_percent,
            'gap_type': gap_type,
            'direction': direction
        }

    @staticmethod
    def calculate_opening_range(df: pd.DataFrame, minutes: int = 15) -> Dict[str, float]:
        """Calculate Opening Range Breakout levels"""
        # Assume first N rows are the opening range
        or_data = df.head(minutes)

        if or_data.empty:
            return {'or_high': np.nan, 'or_low': np.nan, 'range_size': np.nan}

        or_high = or_data['high'].max()
        or_low = or_data['low'].min()
        range_size = or_high - or_low

        return {
            'or_high': or_high,
            'or_low': or_low,
            'range_size': range_size,
            'breakout_long': or_high,
            'breakout_short': or_low,
            'target_long': or_high + range_size,
            'target_short': or_low - range_size
        }

    # ==================== COMPREHENSIVE ANALYSIS ====================

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a stock"""
        result = df.copy()

        # Ensure required columns
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in result.columns for col in required_cols):
            raise ValueError(f"Missing required columns. Need: {required_cols}")

        try:
            # Returns
            result['returns'] = result['close'].pct_change()
            result['log_returns'] = np.log(result['close'] / result['close'].shift(1))

            # Momentum Indicators
            result['rsi_7'] = self.calculate_rsi(result['close'], 7)
            result['rsi_14'] = self.calculate_rsi(result['close'], 14)

            macd = self.calculate_macd(result['close'], 12, 26, 9)
            result = pd.concat([result, macd], axis=1)

            macd_fast = self.calculate_macd(result['close'], 8, 17, 9)
            result['macd_fast'] = macd_fast['macd']

            stoch = self.calculate_stochastic(result['high'], result['low'], result['close'])
            result = pd.concat([result, stoch], axis=1)

            # Volume Indicators
            result['vwap'] = self.calculate_vwap(result['high'], result['low'], result['close'], result['volume'])
            result['obv'] = self.calculate_obv(result['close'], result['volume'])
            result['volume_spike'] = self.detect_volume_spike(result['volume'])

            # Volatility Indicators
            result['atr'] = self.calculate_atr(result['high'], result['low'], result['close'])

            bbands = self.calculate_bollinger_bands(result['close'])
            result = pd.concat([result, bbands], axis=1)

            result['volatility'] = self.calculate_historical_volatility(result['returns'])

            # Trend Indicators
            mas = self.calculate_moving_averages(result['close'])
            result = pd.concat([result, mas], axis=1)

            # Position relative to MAs
            result['above_sma_20'] = result['close'] > result['sma_20']
            result['above_sma_50'] = result['close'] > result['sma_50']
            result['above_sma_200'] = result['close'] > result['sma_200']

            # Distance from VWAP
            result['dist_from_vwap'] = (result['close'] - result['vwap']) / result['vwap']

            # Overbought/Oversold flags
            result['rsi_overbought'] = result['rsi_14'] > 70
            result['rsi_oversold'] = result['rsi_14'] < 30

            logger.debug(f"Calculated {len(result.columns)} features")

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            raise

        return result

    # ==================== BATCH PROCESSING ====================

    def analyze_multiple_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Analyze multiple stocks using multiprocessing"""
        logger.info(f"Analyzing {len(stock_data)} stocks with {self.max_workers} workers...")

        # Use multiprocessing for CPU-bound indicator calculations
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                symbol: executor.submit(self.calculate_all_indicators, df)
                for symbol, df in stock_data.items()
            }

            # Collect results
            results = {}
            failed = []

            for symbol, future in futures.items():
                try:
                    results[symbol] = future.result(timeout=60)
                except Exception as e:
                    logger.error(f"Failed to analyze {symbol}: {e}")
                    failed.append(symbol)

        logger.info(f"Successfully analyzed: {len(results)}/{len(stock_data)}")
        if failed:
            logger.warning(f"Failed: {failed}")

        return results

    # ==================== SUMMARY STATISTICS ====================

    @staticmethod
    def get_latest_metrics(df: pd.DataFrame) -> Dict[str, float]:
        """Extract latest values for all indicators"""
        if df.empty:
            return {}

        latest = df.iloc[-1]
        metrics = {
            'latest_price': latest['close'],
            'latest_volume': latest['volume'],
            'rsi_7': latest.get('rsi_7', np.nan),
            'rsi_14': latest.get('rsi_14', np.nan),
            'macd': latest.get('macd', np.nan),
            'macd_signal': latest.get('signal', np.nan),
            'macd_histogram': latest.get('histogram', np.nan),
            'atr': latest.get('atr', np.nan),
            'volatility': latest.get('volatility', np.nan),
            'vwap': latest.get('vwap', np.nan),
            'dist_from_vwap': latest.get('dist_from_vwap', np.nan),
            'above_sma_20': latest.get('above_sma_20', False),
            'above_sma_50': latest.get('above_sma_50', False),
            'rsi_overbought': latest.get('rsi_overbought', False),
            'rsi_oversold': latest.get('rsi_oversold', False),
            'volume_spike': latest.get('volume_spike', False)
        }

        return {k: v for k, v in metrics.items() if not pd.isna(v)}


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Example data (would come from data_acquisition module)
    dates = pd.date_range('2024-01-01', periods=100, freq='5min')
    df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000000, 10000000, 100)
    }, index=dates)

    # Initialize analyzer
    config = {'analysis': {'max_compute_workers': 4}}
    analyzer = QuantitativeAnalyzer(config)

    # Calculate indicators
    print("=== Calculating Indicators ===")
    result = analyzer.calculate_all_indicators(df)
    print(f"Calculated {len(result.columns)} columns")
    print(result.tail())

    # Get latest metrics
    print("\n=== Latest Metrics ===")
    metrics = analyzer.get_latest_metrics(result)
    for key, value in metrics.items():
        print(f"{key}: {value}")

    # Calculate opening range
    print("\n=== Opening Range (15 min) ===")
    or_levels = analyzer.calculate_opening_range(result, minutes=15)
    for key, value in or_levels.items():
        print(f"{key}: {value}")

    # Calculate gap
    print("\n=== Gap Analysis ===")
    gap_metrics = analyzer.calculate_gap(df['open'].iloc[0], df['close'].iloc[-2])
    for key, value in gap_metrics.items():
        print(f"{key}: {value}")
