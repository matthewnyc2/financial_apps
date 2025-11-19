"""
Order Flow and Market Making Module

Implements advanced order flow microstructure models:
- VPIN (Volume-Synchronized Probability of Informed Trading)
- Order Book Imbalance metrics
- Buy/Sell Pressure calculations
- Market Maker Spread Optimization
- Inventory Risk Management
"""

import numpy as np
import pandas as pd
from typing import Tuple, Dict, List
from dataclasses import dataclass
from scipy.stats import norm


@dataclass
class OrderFlowMetrics:
    """Container for order flow metrics"""
    vpin: float
    order_imbalance: float
    buy_pressure: float
    sell_pressure: float
    net_flow: float
    realized_spread: float
    effective_spread: float


@dataclass
class MarketMakerState:
    """Market maker inventory and quote state"""
    inventory: float
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    bid_volume: float
    ask_volume: float


class VPIN:
    """
    Volume-Synchronized Probability of Informed Trading

    Measures probability of informed trading by analyzing volume patterns.
    Higher VPIN indicates more likely informed trading activity.

    Formula:
    VPIN = E[|ΔV_B - ΔV_S|] / (ΔV_B + ΔV_S)
    where ΔV_B = buy volume in bucket, ΔV_S = sell volume in bucket
    """

    def __init__(self, window_size: int = 50, bucket_volume: float = 1e6):
        """
        Args:
            window_size: Number of buckets to use in calculation
            bucket_volume: Volume threshold per bucket
        """
        self.window_size = window_size
        self.bucket_volume = bucket_volume
        self.volume_buckets = []
        self.buy_volumes = []
        self.sell_volumes = []
        self.cumulative_volume = 0

    def classify_trade(self, price: float, volume: float,
                       previous_price: float) -> str:
        """
        Classify trade as buy or sell using tick rule.

        Formula:
        If price > previous_price: BUY
        If price < previous_price: SELL
        If price == previous_price: Use previous trade direction
        """
        if price > previous_price:
            return 'BUY'
        elif price < previous_price:
            return 'SELL'
        else:
            return 'NEUTRAL'

    def add_trade(self, price: float, volume: float,
                  previous_price: float) -> None:
        """Add trade and update bucket if threshold reached"""
        trade_type = self.classify_trade(price, volume, previous_price)
        self.cumulative_volume += volume

        if trade_type == 'BUY':
            self.buy_volumes.append(volume)
        elif trade_type == 'SELL':
            self.sell_volumes.append(volume)

        # Create bucket when volume threshold reached
        if self.cumulative_volume >= self.bucket_volume:
            buy_vol = sum(self.buy_volumes) if self.buy_volumes else 0
            sell_vol = sum(self.sell_volumes) if self.sell_volumes else 0

            self.volume_buckets.append({
                'buy': buy_vol,
                'sell': sell_vol
            })

            self.buy_volumes = []
            self.sell_volumes = []
            self.cumulative_volume = 0

    def calculate(self) -> float:
        """
        Calculate VPIN

        Formula:
        VPIN = (1/N) * Σ(|V_B_i - V_S_i|) / (V_B_i + V_S_i)
        where N = number of buckets
        """
        if len(self.volume_buckets) < self.window_size:
            return 0.0

        # Use last window_size buckets
        recent_buckets = self.volume_buckets[-self.window_size:]

        vpin_sum = 0.0
        for bucket in recent_buckets:
            total = bucket['buy'] + bucket['sell']
            if total > 0:
                imbalance = abs(bucket['buy'] - bucket['sell']) / total
                vpin_sum += imbalance

        vpin = vpin_sum / len(recent_buckets)
        return np.clip(vpin, 0, 1)


class OrderBookImbalance:
    """
    Order Book Imbalance Metrics

    Measures pressure from buy/sell orders at different depth levels.
    """

    @staticmethod
    def calculate_imbalance(bids: np.ndarray, asks: np.ndarray,
                           depth: int = 5) -> float:
        """
        Calculate order book imbalance at given depth.

        Formula:
        Imbalance = (Σ Bid_Volume - Σ Ask_Volume) / (Σ Bid_Volume + Σ Ask_Volume)
        where sum is over first 'depth' levels
        """
        bid_volume = np.sum(bids[:depth, 1]) if len(bids) > 0 else 0
        ask_volume = np.sum(asks[:depth, 1]) if len(asks) > 0 else 0

        total = bid_volume + ask_volume
        if total == 0:
            return 0.0

        imbalance = (bid_volume - ask_volume) / total
        return np.clip(imbalance, -1, 1)

    @staticmethod
    def weighted_imbalance(bids: np.ndarray, asks: np.ndarray,
                          depth: int = 5) -> float:
        """
        Calculate depth-weighted order book imbalance.

        Formula:
        Weighted_Imbalance = Σ(w_i * (B_i - A_i)) / Σ(w_i * (B_i + A_i))
        where w_i = 1/i (decreasing weight with depth)
        """
        total_weighted_bid = 0.0
        total_weighted_ask = 0.0

        for i in range(min(depth, len(bids), len(asks))):
            weight = 1.0 / (i + 1)
            bid_vol = bids[i, 1] if len(bids) > i else 0
            ask_vol = asks[i, 1] if len(asks) > i else 0

            total_weighted_bid += weight * bid_vol
            total_weighted_ask += weight * ask_vol

        total = total_weighted_bid + total_weighted_ask
        if total == 0:
            return 0.0

        imbalance = (total_weighted_bid - total_weighted_ask) / total
        return np.clip(imbalance, -1, 1)

    @staticmethod
    def midprice_imbalance(best_bid: float, best_ask: float,
                          bid_vol: float, ask_vol: float) -> float:
        """
        Calculate imbalance at best bid-ask.

        Formula:
        Imbalance = (B_vol - A_vol) / (B_vol + A_vol)
        """
        total = bid_vol + ask_vol
        if total == 0:
            return 0.0

        return (bid_vol - ask_vol) / total


class BuySellPressure:
    """
    Buy and Sell Pressure Metrics

    Measures market pressure from buy vs sell side orders.
    """

    @staticmethod
    def calculate_pressure(buy_volume: float, sell_volume: float,
                          lookback: int = 20) -> Tuple[float, float]:
        """
        Calculate normalized buy and sell pressure.

        Formula:
        Buy_Pressure = Buy_Volume / (Buy_Volume + Sell_Volume)
        Sell_Pressure = Sell_Volume / (Buy_Volume + Sell_Volume)
        """
        total = buy_volume + sell_volume
        if total == 0:
            return 0.5, 0.5

        buy_pressure = buy_volume / total
        sell_pressure = sell_volume / total

        return np.clip(buy_pressure, 0, 1), np.clip(sell_pressure, 0, 1)

    @staticmethod
    def aggressive_buy_ratio(aggressive_buy_vol: float,
                            total_buy_vol: float) -> float:
        """
        Ratio of aggressive (market) buys to total buy volume.

        Formula:
        Aggressive_Buy_Ratio = Aggressive_Buy_Volume / Total_Buy_Volume
        """
        if total_buy_vol == 0:
            return 0.0
        return aggressive_buy_vol / total_buy_vol

    @staticmethod
    def net_buy_pressure(buy_vol: float, sell_vol: float) -> float:
        """
        Net buy pressure signed metric.

        Formula:
        Net_Pressure = (Buy_Vol - Sell_Vol) / (Buy_Vol + Sell_Vol)
        Range: [-1, 1], where 1 = all buys, -1 = all sells
        """
        total = buy_vol + sell_vol
        if total == 0:
            return 0.0

        return (buy_vol - sell_vol) / total


class MarketMakerSpread:
    """
    Market Maker Spread Optimization Models

    Determines optimal bid-ask spreads based on inventory and volatility.
    """

    @staticmethod
    def avellaneda_stoikov_spread(inventory: float, max_inventory: float,
                                  volatility: float, time_to_exit: float,
                                  risk_aversion: float = 0.1) -> Tuple[float, float]:
        """
        Avellaneda-Stoikov spread model for market makers.

        Formula:
        s* = (2/γ) * ln(1 + γ/k) + (γ * q * σ² * T) / k

        where:
        γ = risk aversion coefficient
        q = current inventory
        σ = volatility
        T = time to exit
        k = order arrival intensity

        Returns: (bid_spread, ask_spread)
        """
        # Reserve spread (baseline)
        reserve_spread = (2 / risk_aversion) * np.log(1 + risk_aversion / 100)

        # Inventory adjustment (skew spreads based on inventory)
        # If holding long, widen bid spread and narrow ask spread
        inventory_adjustment = (risk_aversion * inventory * volatility ** 2 * time_to_exit) / 100

        bid_spread = reserve_spread / 2 + inventory_adjustment / 2
        ask_spread = reserve_spread / 2 - inventory_adjustment / 2

        return np.clip(bid_spread, 1e-4, 0.5), np.clip(ask_spread, 1e-4, 0.5)

    @staticmethod
    def inventory_cost_spread(inventory: float, max_inventory: float,
                             volatility: float) -> Tuple[float, float]:
        """
        Spread adjustment based on inventory level.

        Formula:
        Spread_Adjustment = α * (q / Q_max) * σ

        where:
        q = current inventory
        Q_max = maximum inventory limit
        σ = volatility
        α = sensitivity parameter
        """
        alpha = 0.5

        # Normalize inventory to [-1, 1]
        if max_inventory == 0:
            inventory_ratio = 0
        else:
            inventory_ratio = inventory / max_inventory

        spread_adjustment = alpha * inventory_ratio * volatility

        base_spread = volatility * 0.1  # 10% of volatility as base

        bid_spread = base_spread + spread_adjustment
        ask_spread = base_spread - spread_adjustment

        return np.clip(bid_spread, 1e-4, 0.5), np.clip(ask_spread, 1e-4, 0.5)

    @staticmethod
    def volatility_scaled_spread(volatility: float, bid_ask_imbalance: float,
                                base_spread: float = 0.001) -> float:
        """
        Scale spread based on volatility and order imbalance.

        Formula:
        Spread = Base_Spread * (1 + α*σ) * (1 + β*Imbalance)

        where:
        Base_Spread = baseline spread
        σ = volatility
        Imbalance = order book imbalance
        α, β = sensitivity parameters
        """
        alpha = 2.0  # Volatility sensitivity
        beta = 0.5   # Imbalance sensitivity

        spread = base_spread * (1 + alpha * volatility) * (1 + beta * abs(bid_ask_imbalance))

        return np.clip(spread, 1e-4, 0.5)


class InventoryRiskManagement:
    """
    Inventory Risk Management for Market Makers

    Models inventory costs and optimal position management.
    """

    @staticmethod
    def inventory_cost(inventory: float, volatility: float,
                      time_horizon: float, liquidation_cost_rate: float = 0.001) -> float:
        """
        Calculate expected cost of holding inventory.

        Formula:
        C = (1/2) * λ * σ² * q² * T + L * |q|

        where:
        λ = risk aversion
        σ = volatility
        q = inventory
        T = time horizon
        L = liquidation cost rate
        """
        # Quadratic risk component (variance cost)
        risk_aversion = 0.5
        variance_cost = risk_aversion * volatility ** 2 * inventory ** 2 * time_horizon

        # Linear liquidation cost
        liquidation_cost = liquidation_cost_rate * abs(inventory)

        total_cost = variance_cost + liquidation_cost
        return total_cost

    @staticmethod
    def target_inventory(current_price: float, reference_price: float,
                        max_inventory: float, sensitivity: float = 0.5) -> float:
        """
        Calculate target inventory based on price changes.

        Formula:
        q_target = -α * (P - P_ref) * Q_max / σ

        where:
        P = current price
        P_ref = reference price
        Q_max = maximum inventory
        α = sensitivity parameter
        """
        if reference_price == 0:
            return 0.0

        price_change = (current_price - reference_price) / reference_price
        target = -sensitivity * price_change * max_inventory

        return np.clip(target, -max_inventory, max_inventory)

    @staticmethod
    def position_limit_breach_probability(inventory: float, max_inventory: float,
                                         volatility: float, time_horizon: float) -> float:
        """
        Probability of breaching inventory limits due to random price moves.

        Formula:
        P(breach) = 2 * [1 - N((Q_max - |q|) / (σ * √T))]

        where:
        q = current inventory
        Q_max = inventory limit
        σ = volatility
        T = time horizon
        N = standard normal CDF
        """
        if max_inventory == 0:
            return 0.0

        remaining_capacity = abs(max_inventory - abs(inventory))
        volatility_distance = remaining_capacity / (volatility * np.sqrt(time_horizon) + 1e-10)

        # Using standard normal distribution
        breach_prob = 2 * (1 - norm.cdf(volatility_distance))

        return np.clip(breach_prob, 0, 1)

    @staticmethod
    def inventory_adjustment_signal(inventory: float, max_inventory: float,
                                   volatility: float) -> Tuple[float, float]:
        """
        Generate adjustment signals for inventory rebalancing.

        Returns:
        - buy_intensity: Intensity to increase position
        - sell_intensity: Intensity to decrease position

        Formula:
        buy_intensity = max(0, -q) / Q_max
        sell_intensity = max(0, q) / Q_max
        """
        if max_inventory == 0:
            return 0.0, 0.0

        # Stronger signal the farther from neutral
        buy_intensity = max(0, -inventory) / max_inventory
        sell_intensity = max(0, inventory) / max_inventory

        return buy_intensity, sell_intensity


class OrderFlowAnalyzer:
    """
    Integrated Order Flow Analysis

    Combines multiple metrics for comprehensive order flow assessment.
    """

    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.vpin = VPIN(window_size=window_size)
        self.price_history = []
        self.volume_history = []
        self.bid_history = []
        self.ask_history = []

    def update(self, price: float, volume: float, bid_size: float,
               ask_size: float) -> OrderFlowMetrics:
        """
        Update analyzer with new market data and compute metrics.
        """
        # Add to history
        self.price_history.append(price)
        self.volume_history.append(volume)
        self.bid_history.append(bid_size)
        self.ask_history.append(ask_size)

        # Keep only recent history
        if len(self.price_history) > self.window_size * 10:
            self.price_history.pop(0)
            self.volume_history.pop(0)
            self.bid_history.pop(0)
            self.ask_history.pop(0)

        # Calculate VPIN
        prev_price = self.price_history[-2] if len(self.price_history) > 1 else price
        self.vpin.add_trade(price, volume, prev_price)
        vpin = self.vpin.calculate()

        # Calculate pressure metrics
        buy_vol = sum(v for v in self.volume_history if len(self.price_history) > 1
                     and self.price_history[self.volume_history.index(v)] >
                     (self.price_history[self.volume_history.index(v)-1] if self.volume_history.index(v) > 0 else 0))
        sell_vol = sum(self.volume_history) - buy_vol

        buy_pressure, sell_pressure = BuySellPressure.calculate_pressure(buy_vol, sell_vol)
        net_flow = BuySellPressure.net_buy_pressure(buy_vol, sell_vol)

        # Calculate spread metrics
        recent_bids = np.array(self.bid_history[-20:])
        recent_asks = np.array(self.ask_history[-20:])

        if len(recent_bids) > 0 and len(recent_asks) > 0:
            imbalance = OrderBookImbalance.calculate_imbalance(
                np.column_stack((np.arange(len(recent_bids)), recent_bids)),
                np.column_stack((np.arange(len(recent_asks)), recent_asks))
            )
        else:
            imbalance = 0.0

        # Compute spreads
        realized_spread = abs(price - (self.price_history[-2] if len(self.price_history) > 1 else price))
        effective_spread = (ask_size - bid_size) / (price + 1e-10) if price > 0 else 0

        return OrderFlowMetrics(
            vpin=vpin,
            order_imbalance=imbalance,
            buy_pressure=buy_pressure,
            sell_pressure=sell_pressure,
            net_flow=net_flow,
            realized_spread=realized_spread,
            effective_spread=effective_spread
        )


# Example usage and testing
if __name__ == "__main__":
    # Test VPIN calculation
    print("=" * 60)
    print("Order Flow and Market Making Analysis")
    print("=" * 60)

    # Simulate market data
    vpin_calc = VPIN(window_size=50, bucket_volume=1e6)
    prices = np.random.uniform(100, 101, 1000)
    volumes = np.random.uniform(1000, 5000, 1000)

    for i in range(1, len(prices)):
        vpin_calc.add_trade(prices[i], volumes[i], prices[i-1])

    print(f"\nVPIN (Informed Trading Probability): {vpin_calc.calculate():.4f}")

    # Test order book imbalance
    print("\n" + "=" * 60)
    print("Order Book Analysis")
    print("=" * 60)

    bids = np.array([[100.0, 1000], [99.9, 1500], [99.8, 2000]])
    asks = np.array([[100.1, 800], [100.2, 1200], [100.3, 1800]])

    imbalance = OrderBookImbalance.calculate_imbalance(bids, asks)
    weighted_imbal = OrderBookImbalance.weighted_imbalance(bids, asks)

    print(f"Order Book Imbalance: {imbalance:.4f}")
    print(f"Weighted Imbalance: {weighted_imbal:.4f}")

    # Test buy/sell pressure
    print("\n" + "=" * 60)
    print("Buy/Sell Pressure Analysis")
    print("=" * 60)

    buy_vol = 50000
    sell_vol = 30000
    buy_p, sell_p = BuySellPressure.calculate_pressure(buy_vol, sell_vol)
    net_p = BuySellPressure.net_buy_pressure(buy_vol, sell_vol)

    print(f"Buy Pressure: {buy_p:.4f}")
    print(f"Sell Pressure: {sell_p:.4f}")
    print(f"Net Buy Pressure: {net_p:.4f}")

    # Test market maker spread optimization
    print("\n" + "=" * 60)
    print("Market Maker Spread Optimization")
    print("=" * 60)

    inventory = 100
    max_inventory = 500
    volatility = 0.02
    time_to_exit = 1.0

    bid_spread, ask_spread = MarketMakerSpread.avellaneda_stoikov_spread(
        inventory, max_inventory, volatility, time_to_exit
    )

    print(f"Avellaneda-Stoikov Bid Spread: {bid_spread:.6f}")
    print(f"Avellaneda-Stoikov Ask Spread: {ask_spread:.6f}")

    inv_bid, inv_ask = MarketMakerSpread.inventory_cost_spread(
        inventory, max_inventory, volatility
    )

    print(f"Inventory-Based Bid Spread: {inv_bid:.6f}")
    print(f"Inventory-Based Ask Spread: {inv_ask:.6f}")

    # Test inventory risk management
    print("\n" + "=" * 60)
    print("Inventory Risk Management")
    print("=" * 60)

    inv_cost = InventoryRiskManagement.inventory_cost(inventory, volatility, time_to_exit)
    target_inv = InventoryRiskManagement.target_inventory(100.5, 100.0, max_inventory)
    breach_prob = InventoryRiskManagement.position_limit_breach_probability(
        inventory, max_inventory, volatility, time_to_exit
    )

    print(f"Inventory Cost: ${inv_cost:.4f}")
    print(f"Target Inventory: {target_inv:.2f} units")
    print(f"Breach Probability: {breach_prob:.4f}")

    # Test integrated analyzer
    print("\n" + "=" * 60)
    print("Integrated Order Flow Analysis")
    print("=" * 60)

    analyzer = OrderFlowAnalyzer(window_size=100)

    for i in range(1, 100):
        price = 100 + np.cumsum(np.random.normal(0, 0.01, 100))[i]
        volume = np.random.uniform(1000, 5000)
        bid_size = np.random.uniform(500, 2000)
        ask_size = np.random.uniform(500, 2000)

        metrics = analyzer.update(price, volume, bid_size, ask_size)

    print(f"VPIN: {metrics.vpin:.4f}")
    print(f"Order Imbalance: {metrics.order_imbalance:.4f}")
    print(f"Buy Pressure: {metrics.buy_pressure:.4f}")
    print(f"Net Flow: {metrics.net_flow:.4f}")
    print(f"Realized Spread: {metrics.realized_spread:.6f}")
    print(f"Effective Spread: {metrics.effective_spread:.6f}")
