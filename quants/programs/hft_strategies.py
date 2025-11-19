"""
High-Frequency Trading (HFT) Strategies Implementation

This module implements core HFT strategies including:
- Bid-ask spread analysis
- Order book imbalance detection
- Microstructure features extraction
- Quote stuffing detection
- VWAP/TWAP execution algorithms
- Order book processing
"""

import numpy as np
import pandas as pd
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import warnings


@dataclass
class OrderBookLevel:
    """Represents a single level in the order book"""
    price: float
    quantity: float
    count: int  # Number of orders at this price
    timestamp: datetime


@dataclass
class OrderBookSnapshot:
    """Snapshot of the complete order book at a point in time"""
    timestamp: datetime
    bids: List[OrderBookLevel]
    asks: List[OrderBookLevel]
    sequence: int


class OrderBook:
    """
    Efficient order book implementation for high-frequency trading analysis.
    Tracks bid/ask prices and quantities with timestamp data.
    """

    def __init__(self, symbol: str, max_levels: int = 20):
        self.symbol = symbol
        self.max_levels = max_levels
        self.bids = {}  # price -> (quantity, count, timestamp)
        self.asks = {}  # price -> (quantity, count, timestamp)
        self.sequence = 0
        self.snapshots = deque(maxlen=1000)
        self.last_update = None

    def update_bid(self, price: float, quantity: float, count: int = 1,
                   timestamp: Optional[datetime] = None):
        """Update or add bid level"""
        if timestamp is None:
            timestamp = datetime.now()

        if quantity == 0:
            self.bids.pop(price, None)
        else:
            self.bids[price] = (quantity, count, timestamp)

        self.last_update = timestamp
        self.sequence += 1

    def update_ask(self, price: float, quantity: float, count: int = 1,
                   timestamp: Optional[datetime] = None):
        """Update or add ask level"""
        if timestamp is None:
            timestamp = datetime.now()

        if quantity == 0:
            self.asks.pop(price, None)
        else:
            self.asks[price] = (quantity, count, timestamp)

        self.last_update = timestamp
        self.sequence += 1

    def get_best_bid_ask(self) -> Tuple[Optional[float], Optional[float]]:
        """Get best bid and ask prices"""
        best_bid = max(self.bids.keys()) if self.bids else None
        best_ask = min(self.asks.keys()) if self.asks else None
        return best_bid, best_ask

    def get_snapshot(self) -> OrderBookSnapshot:
        """Create current order book snapshot"""
        best_bid, best_ask = self.get_best_bid_ask()

        bids = []
        asks = []

        if self.bids:
            for price in sorted(self.bids.keys(), reverse=True)[:self.max_levels]:
                qty, count, ts = self.bids[price]
                bids.append(OrderBookLevel(price, qty, count, ts))

        if self.asks:
            for price in sorted(self.asks.keys())[:self.max_levels]:
                qty, count, ts = self.asks[price]
                asks.append(OrderBookLevel(price, qty, count, ts))

        snapshot = OrderBookSnapshot(
            timestamp=self.last_update or datetime.now(),
            bids=bids,
            asks=asks,
            sequence=self.sequence
        )
        self.snapshots.append(snapshot)
        return snapshot

    def clear(self):
        """Clear order book"""
        self.bids.clear()
        self.asks.clear()
        self.sequence = 0


class BidAskSpreadAnalyzer:
    """
    Analyzes bid-ask spreads and their dynamics.

    Key metrics:
    - Absolute spread: ask_price - bid_price
    - Relative spread: spread / mid_price
    - Spread volatility: standard deviation of spreads
    - Spread depth: quantity available at best bid/ask
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.spreads = deque(maxlen=window_size)
        self.relative_spreads = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)

    def calculate_spread(self, best_bid: float, best_ask: float) -> Tuple[float, float]:
        """
        Calculate absolute and relative spread

        Args:
            best_bid: Best bid price
            best_ask: Best ask price

        Returns:
            Tuple of (absolute_spread, relative_spread)
        """
        if best_bid <= 0 or best_ask <= 0 or best_bid >= best_ask:
            return 0.0, 0.0

        absolute_spread = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2
        relative_spread = absolute_spread / mid_price if mid_price > 0 else 0

        return absolute_spread, relative_spread

    def add_spread(self, best_bid: float, best_ask: float,
                   timestamp: Optional[datetime] = None):
        """Track spread measurement"""
        abs_spread, rel_spread = self.calculate_spread(best_bid, best_ask)
        self.spreads.append(abs_spread)
        self.relative_spreads.append(rel_spread)
        self.timestamps.append(timestamp or datetime.now())

    def get_spread_stats(self) -> Dict[str, float]:
        """Get spread statistics"""
        if not self.spreads:
            return {}

        spreads = list(self.spreads)
        rel_spreads = list(self.relative_spreads)

        return {
            'mean_spread': np.mean(spreads),
            'std_spread': np.std(spreads),
            'min_spread': np.min(spreads),
            'max_spread': np.max(spreads),
            'median_spread': np.median(spreads),
            'mean_relative_spread': np.mean(rel_spreads),
            'std_relative_spread': np.std(rel_spreads),
        }


class OrderBookImbalanceAnalyzer:
    """
    Detects order book imbalances that may indicate directional bias.

    Key metrics:
    - Book imbalance ratio: (bid_volume - ask_volume) / (bid_volume + ask_volume)
    - Cumulative imbalance: sum of imbalances over time
    - Level imbalance: imbalance at specific depth levels
    - Volume-weighted imbalance
    """

    def __init__(self, window_size: int = 100, depth_levels: int = 5):
        self.window_size = window_size
        self.depth_levels = depth_levels
        self.imbalances = deque(maxlen=window_size)
        self.cumulative_imbalance = 0

    def calculate_imbalance(self, bids: List[OrderBookLevel],
                           asks: List[OrderBookLevel]) -> float:
        """
        Calculate order book imbalance ratio

        Positive values indicate more buy pressure (more bid volume)
        Negative values indicate more sell pressure (more ask volume)

        Args:
            bids: List of bid levels
            asks: List of ask levels

        Returns:
            Imbalance ratio in range [-1, 1]
        """
        bid_volume = sum(level.quantity for level in bids[:self.depth_levels])
        ask_volume = sum(level.quantity for level in asks[:self.depth_levels])

        total_volume = bid_volume + ask_volume
        if total_volume == 0:
            return 0.0

        imbalance = (bid_volume - ask_volume) / total_volume
        return max(-1.0, min(1.0, imbalance))

    def calculate_vwap_imbalance(self, bids: List[OrderBookLevel],
                                 asks: List[OrderBookLevel]) -> float:
        """
        Calculate volume-weighted imbalance using prices as weights
        Gives more importance to levels closer to mid-price
        """
        if not bids or not asks:
            return 0.0

        # Use price levels as weights (closer to mid = higher weight)
        mid_price = (bids[0].price + asks[0].price) / 2

        bid_weighted = sum(
            level.quantity * (level.price / mid_price)
            for level in bids[:self.depth_levels]
        )
        ask_weighted = sum(
            level.quantity * ((2 * mid_price - level.price) / mid_price)
            for level in asks[:self.depth_levels]
        )

        total = bid_weighted + ask_weighted
        if total == 0:
            return 0.0

        return (bid_weighted - ask_weighted) / total

    def add_imbalance(self, bids: List[OrderBookLevel],
                      asks: List[OrderBookLevel]):
        """Add imbalance measurement"""
        imbalance = self.calculate_imbalance(bids, asks)
        self.imbalances.append(imbalance)
        self.cumulative_imbalance += imbalance

    def get_imbalance_stats(self) -> Dict[str, float]:
        """Get imbalance statistics"""
        if not self.imbalances:
            return {}

        imbalances = list(self.imbalances)
        return {
            'mean_imbalance': np.mean(imbalances),
            'std_imbalance': np.std(imbalances),
            'cumulative_imbalance': self.cumulative_imbalance,
            'recent_imbalance': imbalances[-1] if imbalances else 0,
        }


class MicrostructureAnalyzer:
    """
    Extracts microstructure features relevant to HFT strategies.

    Features include:
    - Spread dynamics
    - Depth profile
    - Order arrival rates
    - Price impact
    - Volatility clustering
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.prices = deque(maxlen=window_size)
        self.returns = deque(maxlen=window_size)
        self.volumes = deque(maxlen=window_size)
        self.spreads = deque(maxlen=window_size)

    def calculate_log_returns(self, prices: List[float]) -> List[float]:
        """Calculate log returns from price series"""
        if len(prices) < 2:
            return []
        return [np.log(prices[i] / prices[i-1]) for i in range(1, len(prices))]

    def calculate_volatility(self, prices: List[float], window: int = 20) -> float:
        """Calculate realized volatility"""
        returns = self.calculate_log_returns(prices)
        if len(returns) < window:
            return 0.0
        return np.std(returns[-window:])

    def calculate_price_impact(self, mid_price_before: float,
                               mid_price_after: float,
                               volume: float) -> float:
        """
        Calculate price impact of a trade
        Impact = |price_after - price_before| / volume
        """
        if volume == 0:
            return 0.0
        return abs(mid_price_after - mid_price_before) / volume

    def extract_features(self, order_book: OrderBook) -> Dict[str, float]:
        """Extract microstructure features from order book"""
        snapshot = order_book.get_snapshot()

        if not snapshot.bids or not snapshot.asks:
            return {}

        best_bid = snapshot.bids[0].price
        best_ask = snapshot.asks[0].price
        mid_price = (best_bid + best_ask) / 2

        features = {
            'mid_price': mid_price,
            'spread': best_ask - best_bid,
            'relative_spread': (best_ask - best_bid) / mid_price,
            'bid_depth': snapshot.bids[0].quantity,
            'ask_depth': snapshot.asks[0].quantity,
            'depth_imbalance': (snapshot.bids[0].quantity - snapshot.asks[0].quantity) /
                              (snapshot.bids[0].quantity + snapshot.asks[0].quantity),
        }

        # Calculate depth profile
        cum_bid_vol = sum(level.quantity for level in snapshot.bids[:5])
        cum_ask_vol = sum(level.quantity for level in snapshot.asks[:5])
        features['cum_depth_5'] = cum_bid_vol + cum_ask_vol
        features['depth_5_imbalance'] = (cum_bid_vol - cum_ask_vol) / max(cum_bid_vol + cum_ask_vol, 1)

        return features

    def add_price(self, price: float):
        """Add price observation"""
        self.prices.append(price)
        if len(self.prices) > 1:
            ret = np.log(price / self.prices[-2])
            self.returns.append(ret)

    def get_microstructure_metrics(self) -> Dict[str, float]:
        """Get comprehensive microstructure metrics"""
        metrics = {}

        if len(self.returns) > 0:
            metrics['return_volatility'] = np.std(self.returns)
            metrics['mean_absolute_return'] = np.mean(np.abs(self.returns))

        if len(self.prices) > 1:
            metrics['price_momentum'] = np.log(self.prices[-1] / self.prices[0])

        return metrics


class QuoteStuffingDetector:
    """
    Detects quote stuffing behavior - rapid order placement and cancellation
    designed to create misleading impressions about trading interest.

    Detection mechanisms:
    - High order cancellation rate
    - Rapid order updates without execution
    - Large order imbalances relative to realized trades
    - Clustering of orders at same price levels
    """

    def __init__(self, window_size: int = 100, threshold_ratio: float = 0.8):
        self.window_size = window_size
        self.threshold_ratio = threshold_ratio  # Ratio of cancellations to placements

        self.orders_placed = deque(maxlen=window_size)
        self.orders_cancelled = deque(maxlen=window_size)
        self.orders_executed = deque(maxlen=window_size)
        self.timestamps = deque(maxlen=window_size)

    def add_order_event(self, event_type: str, quantity: float,
                        price: float, timestamp: Optional[datetime] = None):
        """
        Record order event

        Args:
            event_type: 'placed', 'cancelled', 'executed'
            quantity: Order quantity
            price: Order price
            timestamp: Event timestamp
        """
        if timestamp is None:
            timestamp = datetime.now()

        if event_type == 'placed':
            self.orders_placed.append(quantity)
        elif event_type == 'cancelled':
            self.orders_cancelled.append(quantity)
        elif event_type == 'executed':
            self.orders_executed.append(quantity)

        self.timestamps.append(timestamp)

    def calculate_cancellation_ratio(self) -> float:
        """Calculate ratio of cancelled to placed orders"""
        total_placed = sum(self.orders_placed) if self.orders_placed else 0
        total_cancelled = sum(self.orders_cancelled) if self.orders_cancelled else 0

        if total_placed == 0:
            return 0.0

        return total_cancelled / total_placed

    def detect_quote_stuffing(self) -> Tuple[bool, Dict[str, float]]:
        """
        Detect quote stuffing behavior

        Returns:
            Tuple of (is_quote_stuffing, metrics)
        """
        cancellation_ratio = self.calculate_cancellation_ratio()

        metrics = {
            'cancellation_ratio': cancellation_ratio,
            'orders_placed_total': sum(self.orders_placed) if self.orders_placed else 0,
            'orders_cancelled_total': sum(self.orders_cancelled) if self.orders_cancelled else 0,
            'orders_executed_total': sum(self.orders_executed) if self.orders_executed else 0,
        }

        # Quote stuffing likely if cancellation rate > threshold
        is_stuffing = cancellation_ratio > self.threshold_ratio

        return is_stuffing, metrics


class VWAPExecutor:
    """
    Volume-Weighted Average Price (VWAP) execution algorithm.

    Splits a large order into smaller child orders to minimize market impact
    and achieve prices close to the VWAP.
    """

    def __init__(self, symbol: str, total_quantity: float,
                 start_time: datetime, end_time: datetime):
        self.symbol = symbol
        self.total_quantity = total_quantity
        self.start_time = start_time
        self.end_time = end_time

        self.executed_quantity = 0
        self.executed_price_sum = 0
        self.execution_prices = []
        self.child_orders = []

    def calculate_vwap(self, historical_prices: List[float],
                       historical_volumes: List[float]) -> float:
        """
        Calculate VWAP from historical data
        VWAP = sum(price * volume) / sum(volume)
        """
        if not historical_prices or not historical_volumes:
            return 0.0

        if len(historical_prices) != len(historical_volumes):
            warnings.warn("Price and volume lists have different lengths")
            min_len = min(len(historical_prices), len(historical_volumes))
            historical_prices = historical_prices[:min_len]
            historical_volumes = historical_volumes[:min_len]

        pv_sum = sum(p * v for p, v in zip(historical_prices, historical_volumes))
        v_sum = sum(historical_volumes)

        return pv_sum / v_sum if v_sum > 0 else 0.0

    def generate_child_orders(self, market_volumes: List[float],
                             num_intervals: int = 10) -> List[Dict]:
        """
        Generate child orders based on market volume profile

        Args:
            market_volumes: Expected volumes for each time interval
            num_intervals: Number of time intervals to divide execution period

        Returns:
            List of child order specifications
        """
        if not market_volumes or sum(market_volumes) == 0:
            market_volumes = [1.0] * num_intervals

        total_market_vol = sum(market_volumes)
        volume_ratios = [v / total_market_vol for v in market_volumes]

        time_delta = (self.end_time - self.start_time) / num_intervals
        child_orders = []

        for i, ratio in enumerate(volume_ratios):
            order_qty = self.total_quantity * ratio
            order_time = self.start_time + time_delta * i

            child_orders.append({
                'order_id': f"VWAP_{self.symbol}_{i}",
                'quantity': order_qty,
                'scheduled_time': order_time,
                'side': 'sell' if self.total_quantity > 0 else 'buy',  # Convention
            })

        self.child_orders = child_orders
        return child_orders

    def execute_order(self, executed_qty: float, executed_price: float):
        """Record order execution"""
        self.executed_quantity += executed_qty
        self.executed_price_sum += executed_qty * executed_price
        self.execution_prices.append(executed_price)

    def get_vwap_executed(self) -> float:
        """Get actual VWAP achieved"""
        if self.executed_quantity == 0:
            return 0.0
        return self.executed_price_sum / self.executed_quantity

    def get_execution_metrics(self) -> Dict[str, float]:
        """Get execution performance metrics"""
        vwap = self.get_vwap_executed()

        return {
            'executed_quantity': self.executed_quantity,
            'total_quantity': self.total_quantity,
            'execution_rate': self.executed_quantity / self.total_quantity if self.total_quantity > 0 else 0,
            'vwap_achieved': vwap,
            'avg_execution_price': vwap,
            'min_execution_price': min(self.execution_prices) if self.execution_prices else 0,
            'max_execution_price': max(self.execution_prices) if self.execution_prices else 0,
        }


class TWAPExecutor:
    """
    Time-Weighted Average Price (TWAP) execution algorithm.

    Divides orders equally across time intervals to achieve TWAP pricing.
    Simpler than VWAP but doesn't adapt to market volume.
    """

    def __init__(self, symbol: str, total_quantity: float,
                 start_time: datetime, end_time: datetime,
                 num_intervals: int = 10):
        self.symbol = symbol
        self.total_quantity = total_quantity
        self.start_time = start_time
        self.end_time = end_time
        self.num_intervals = num_intervals

        self.executed_quantity = 0
        self.executed_price_sum = 0
        self.execution_prices = []
        self.child_orders = self._generate_orders()

    def _generate_orders(self) -> List[Dict]:
        """Generate evenly-spaced child orders"""
        order_qty = self.total_quantity / self.num_intervals
        time_delta = (self.end_time - self.start_time) / self.num_intervals

        orders = []
        for i in range(self.num_intervals):
            order_time = self.start_time + time_delta * (i + 0.5)
            orders.append({
                'order_id': f"TWAP_{self.symbol}_{i}",
                'quantity': order_qty,
                'scheduled_time': order_time,
            })

        return orders

    def execute_order(self, executed_qty: float, executed_price: float):
        """Record order execution"""
        self.executed_quantity += executed_qty
        self.executed_price_sum += executed_qty * executed_price
        self.execution_prices.append(executed_price)

    def get_twap_executed(self) -> float:
        """Get actual TWAP achieved"""
        if self.executed_quantity == 0:
            return 0.0
        return self.executed_price_sum / self.executed_quantity

    def get_execution_metrics(self) -> Dict[str, float]:
        """Get execution performance metrics"""
        twap = self.get_twap_executed()

        return {
            'executed_quantity': self.executed_quantity,
            'total_quantity': self.total_quantity,
            'execution_rate': self.executed_quantity / self.total_quantity if self.total_quantity > 0 else 0,
            'twap_achieved': twap,
            'avg_execution_price': twap,
        }


class HFTStrategyAnalyzer:
    """
    Integrated analyzer combining multiple HFT analysis components.
    Provides unified interface for analyzing high-frequency trading scenarios.
    """

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.order_book = OrderBook(symbol)
        self.spread_analyzer = BidAskSpreadAnalyzer()
        self.imbalance_analyzer = OrderBookImbalanceAnalyzer()
        self.microstructure = MicrostructureAnalyzer()
        self.quote_stuffing_detector = QuoteStuffingDetector()

    def update(self, bid_price: float, bid_qty: float, ask_price: float,
               ask_qty: float, bid_count: int = 1, ask_count: int = 1,
               timestamp: Optional[datetime] = None):
        """Update all analyzers with new market data"""
        if timestamp is None:
            timestamp = datetime.now()

        # Update order book
        self.order_book.update_bid(bid_price, bid_qty, bid_count, timestamp)
        self.order_book.update_ask(ask_price, ask_qty, ask_count, timestamp)

        # Update spread analyzer
        self.spread_analyzer.add_spread(bid_price, ask_price, timestamp)

        # Get snapshot for imbalance analysis
        snapshot = self.order_book.get_snapshot()
        if snapshot.bids and snapshot.asks:
            self.imbalance_analyzer.add_imbalance(snapshot.bids, snapshot.asks)

        # Update microstructure
        mid_price = (bid_price + ask_price) / 2
        self.microstructure.add_price(mid_price)

    def get_analysis(self) -> Dict:
        """Get comprehensive HFT analysis"""
        return {
            'spread_stats': self.spread_analyzer.get_spread_stats(),
            'imbalance_stats': self.imbalance_analyzer.get_imbalance_stats(),
            'microstructure_metrics': self.microstructure.get_microstructure_metrics(),
        }

    def detect_trading_signals(self) -> Dict[str, bool]:
        """
        Detect potential trading signals from HFT analysis

        Returns:
            Dictionary of signal indicators
        """
        signals = {}

        imbalance_stats = self.imbalance_analyzer.get_imbalance_stats()
        if imbalance_stats:
            # Strong buy signal if high positive imbalance
            signals['strong_buy_pressure'] = imbalance_stats.get('recent_imbalance', 0) > 0.5
            # Strong sell signal if high negative imbalance
            signals['strong_sell_pressure'] = imbalance_stats.get('recent_imbalance', 0) < -0.5

        spread_stats = self.spread_analyzer.get_spread_stats()
        if spread_stats:
            # Tight spread may indicate good liquidity
            signals['tight_spread'] = spread_stats.get('mean_relative_spread', 1) < 0.001
            # Wide spread may indicate low liquidity
            signals['wide_spread'] = spread_stats.get('mean_relative_spread', 0) > 0.01

        return signals


# Example usage and testing
if __name__ == "__main__":
    print("HFT Strategies Module Loaded Successfully")
    print("\nAvailable Classes:")
    print("- OrderBook: Efficient order book tracking")
    print("- BidAskSpreadAnalyzer: Spread analysis")
    print("- OrderBookImbalanceAnalyzer: Imbalance detection")
    print("- MicrostructureAnalyzer: Microstructure feature extraction")
    print("- QuoteStuffingDetector: Quote stuffing detection")
    print("- VWAPExecutor: Volume-weighted execution")
    print("- TWAPExecutor: Time-weighted execution")
    print("- HFTStrategyAnalyzer: Integrated analyzer")
