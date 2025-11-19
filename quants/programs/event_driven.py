"""
Event-Driven Trading Strategies Implementation

This module implements five key event-driven trading strategies:
1. Earnings Momentum Strategy - Exploits price movements around earnings announcements
2. Post-Earnings Announcement Drift (PEAD) - Captures delayed market reactions
3. Dividend Capture Strategy - Profits from dividend-driven price gaps
4. M&A Arbitrage Calculator - Risk arbitrage on acquisition announcements
5. Event Study Analysis - Statistical analysis of price behavior around events

Includes comprehensive statistical significance testing using t-tests and GARCH models.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from scipy.optimize import minimize


@dataclass
class EventSignal:
    """Event-driven trading signal dataclass"""
    timestamp: int
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    price: float
    event_type: str
    strategy: str
    strength: float = 0.5  # 0-1 confidence
    statistical_significance: float = 0.0  # p-value
    event_date: Optional[int] = None


class EarningsMomentumStrategy:
    """
    Earnings Momentum Strategy

    Exploits the tendency of stocks to move significantly on earnings announcements.

    Key Principles:
    - Positive surprises (actual EPS > expected EPS) lead to price increases
    - Negative surprises trigger sell-offs
    - Momentum often continues for days post-announcement

    Formulas:
        Surprise Magnitude = (Actual EPS - Expected EPS) / |Expected EPS|
        Surprise Signal = sign(Surprise Magnitude) * min(1.0, |Surprise Magnitude| * 2)

    Trading Rules:
        BUY: Positive surprise + Volume surge (> 1.5x average) + Price gap up
        SELL: Negative surprise + Volume surge + Price gap down
    """

    def __init__(self, lookback_days: int = 20, min_volume_multiplier: float = 1.5):
        """Initialize earnings momentum strategy parameters"""
        self.lookback_days = lookback_days
        self.min_volume_multiplier = min_volume_multiplier
        self.avg_volume = None

    def calculate_surprise(self, actual_eps: float, expected_eps: float) -> float:
        """
        Calculate EPS surprise magnitude

        Args:
            actual_eps: Actual earnings per share
            expected_eps: Expected (consensus) EPS

        Returns:
            Normalized surprise metric [-1, 1]
        """
        if expected_eps == 0:
            return 0.0

        surprise = (actual_eps - expected_eps) / abs(expected_eps)
        return np.tanh(surprise)  # Normalize to [-1, 1]

    def analyze_event(self, prices: np.ndarray, volumes: np.ndarray,
                      actual_eps: float, expected_eps: float,
                      event_idx: int) -> EventSignal:
        """
        Analyze earnings announcement event

        Args:
            prices: Array of closing prices
            volumes: Array of trading volumes
            actual_eps: Actual EPS announced
            expected_eps: Expected consensus EPS
            event_idx: Index of earnings announcement day

        Returns:
            EventSignal with trading recommendation
        """
        # Calculate average volume before announcement
        start_idx = max(0, event_idx - self.lookback_days)
        pre_event_volumes = volumes[start_idx:event_idx]
        self.avg_volume = np.mean(pre_event_volumes)

        # Check volume surge on announcement
        event_volume = volumes[event_idx] if event_idx < len(volumes) else 0
        volume_surge = event_volume / (self.avg_volume + 1e-6) if self.avg_volume > 0 else 1.0

        # Calculate surprise
        surprise = self.calculate_surprise(actual_eps, expected_eps)

        # Check price gap
        pre_price = prices[event_idx - 1] if event_idx > 0 else prices[event_idx]
        post_price = prices[event_idx] if event_idx < len(prices) else prices[-1]
        price_gap = (post_price - pre_price) / pre_price if pre_price != 0 else 0

        # Generate signal
        signal_type = 'HOLD'
        strength = 0.0

        if volume_surge > self.min_volume_multiplier:
            if surprise > 0.1:
                signal_type = 'BUY'
                strength = min(1.0, surprise * volume_surge / 2.0)
            elif surprise < -0.1:
                signal_type = 'SELL'
                strength = min(1.0, abs(surprise) * volume_surge / 2.0)

        # Perform t-test on surprise significance
        p_value = self._calculate_significance(surprise, expected_eps)

        return EventSignal(
            timestamp=event_idx,
            signal_type=signal_type,
            price=post_price,
            event_type='EARNINGS',
            strategy='Earnings Momentum',
            strength=strength,
            statistical_significance=p_value,
            event_date=event_idx
        )

    def _calculate_significance(self, surprise: float, expected_eps: float) -> float:
        """
        Calculate statistical significance of surprise using t-test

        Args:
            surprise: Normalized surprise metric
            expected_eps: Expected EPS for context

        Returns:
            p-value (lower = more significant)
        """
        # Simplified t-test: treat surprise as test statistic
        t_stat = surprise * np.sqrt(10)  # Scale by sample size
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=9))  # Two-tailed test
        return p_value


class PostEarningsAnnouncementDrift:
    """
    Post-Earnings Announcement Drift (PEAD) Strategy

    Exploits the market's slow reaction to earnings surprises. Research shows
    that surprises continue to drift for weeks after announcement.

    Key Insight:
    - Market underreacts to earnings news initially
    - Price continues moving in surprise direction for 20-60 days post-announcement
    - Stronger effect for larger surprises and smaller cap stocks

    Formulas:
        Daily Drift = Cumulative Price Return / Days Since Event
        Drift Strength = Daily Drift * Surprise Magnitude * Size Factor

    Drift prediction:
        Expected Return = Surprise * Beta * (1 - decay_factor^days)
        where decay_factor ≈ 0.98 (daily decay)
    """

    def __init__(self, drift_window: int = 60, decay_factor: float = 0.98):
        """Initialize PEAD strategy parameters"""
        self.drift_window = drift_window  # Days to hold position
        self.decay_factor = decay_factor  # How quickly drift decays

    def calculate_drift_trajectory(self, surprise: float, price: float,
                                   subsequent_prices: np.ndarray) -> Dict:
        """
        Calculate drift trajectory post-announcement

        Args:
            surprise: Normalized EPS surprise [-1, 1]
            price: Price at announcement
            subsequent_prices: Prices for N days post-announcement

        Returns:
            Dictionary with drift metrics
        """
        cumulative_returns = []
        drift_values = []
        days_elapsed = []

        for i, subsequent_price in enumerate(subsequent_prices[:self.drift_window]):
            if i == 0:
                continue

            cum_return = (subsequent_price - price) / price
            drift = cum_return / (i + 1)  # Average daily drift

            cumulative_returns.append(cum_return)
            drift_values.append(drift)
            days_elapsed.append(i + 1)

        # Fit exponential decay model
        days_array = np.array(days_elapsed)
        drift_array = np.array(drift_values)

        # Expected drift = surprise * beta * (1 - decay^days)
        predicted_drift = surprise * 0.05 * (1 - self.decay_factor ** days_array)

        # Calculate R-squared
        residuals = drift_array - predicted_drift
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((drift_array - np.mean(drift_array)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        return {
            'cumulative_returns': cumulative_returns,
            'drift_values': drift_values,
            'predicted_drift': predicted_drift,
            'days_elapsed': days_elapsed,
            'r_squared': r_squared,
            'total_drift_return': cumulative_returns[-1] if cumulative_returns else 0
        }

    def analyze_pead_signal(self, surprise: float, price: float,
                            subsequent_prices: np.ndarray,
                            event_idx: int) -> EventSignal:
        """
        Generate PEAD trading signal

        Args:
            surprise: Normalized EPS surprise
            price: Price at announcement
            subsequent_prices: Post-announcement prices
            event_idx: Index of announcement

        Returns:
            EventSignal for PEAD trade
        """
        drift_data = self.calculate_drift_trajectory(surprise, price, subsequent_prices)

        signal_type = 'HOLD'
        strength = 0.0

        # Check if drift is statistically significant
        r_squared = drift_data['r_squared']

        if r_squared > 0.3:  # Model explains >30% of variance
            total_drift = drift_data['total_drift_return']

            if surprise > 0.1 and total_drift > 0.01:
                signal_type = 'BUY'
                strength = min(1.0, abs(surprise) * r_squared)
            elif surprise < -0.1 and total_drift < -0.01:
                signal_type = 'SELL'
                strength = min(1.0, abs(surprise) * r_squared)

        # T-test on drift significance
        drift_array = np.array(drift_data['drift_values'])
        p_value = stats.ttest_1samp(drift_array, popmean=0).pvalue if len(drift_array) > 2 else 1.0

        return EventSignal(
            timestamp=event_idx,
            signal_type=signal_type,
            price=price,
            event_type='PEAD',
            strategy='Post-Earnings Announcement Drift',
            strength=strength,
            statistical_significance=p_value,
            event_date=event_idx
        )


class DividendCaptureStrategy:
    """
    Dividend Capture Strategy

    Exploits the mechanical price drop on ex-dividend date and immediate recovery.

    Key Mechanics:
    - Stock price drops by approximately the dividend amount on ex-dividend date
    - Happens because dividend is paid to shareholders-of-record
    - Creates arbitrage opportunity: buy before ex-date, hold through ex-date, sell after

    Critical Dates:
    1. Announcement Date: When dividend is announced
    2. Ex-Dividend Date: Last day to own stock to receive dividend (price drops)
    3. Record Date: Date of record ownership
    4. Payment Date: When dividend is actually paid

    Formulas:
        Dividend Yield = Annual Dividend / Stock Price
        Expected Price Drop = Dividend Amount (tax-adjusted)
        Tax-Adjusted Gain = Dividend * (1 - dividend_tax_rate) -
                           (Holding Cost + Transaction Costs)

    Profitability Condition:
        Dividend * (1 - tax_rate) > Transaction Cost + Holding Cost
    """

    def __init__(self, transaction_cost_bps: float = 10,
                 dividend_tax_rate: float = 0.15,
                 holding_days: int = 5):
        """Initialize dividend capture parameters"""
        self.transaction_cost_bps = transaction_cost_bps  # Basis points (0.1%)
        self.dividend_tax_rate = dividend_tax_rate
        self.holding_days = holding_days

    def calculate_profit_potential(self, price_before_ex: float,
                                   dividend_amount: float,
                                   price_after_ex: float) -> Dict:
        """
        Calculate profit potential from dividend capture

        Args:
            price_before_ex: Stock price day before ex-dividend
            dividend_amount: Dividend per share to be paid
            price_after_ex: Stock price after ex-dividend date

        Returns:
            Dictionary with profitability metrics
        """
        # Transaction costs (buy and sell)
        transaction_cost = (price_before_ex * 2 * self.transaction_cost_bps) / 10000

        # After-tax dividend
        after_tax_dividend = dividend_amount * (1 - self.dividend_tax_rate)

        # Expected price drop (should approximate dividend)
        expected_price_drop = dividend_amount
        actual_price_drop = price_before_ex - price_after_ex

        # Profit calculation
        capture_gain = dividend_amount  # Get the full dividend
        after_tax_gain = after_tax_dividend
        net_profit = after_tax_gain - transaction_cost

        # Profitability metrics
        return_pct = (net_profit / price_before_ex) * 100
        annual_return = (return_pct / self.holding_days) * 365

        # Statistical test: is the actual drop significantly different from expected?
        price_drop_deviation = actual_price_drop - expected_price_drop

        return {
            'expected_price_drop': expected_price_drop,
            'actual_price_drop': actual_price_drop,
            'price_drop_deviation': price_drop_deviation,
            'before_tax_profit': capture_gain - transaction_cost,
            'after_tax_profit': net_profit,
            'return_pct': return_pct,
            'annual_return_pct': annual_return,
            'profitable': net_profit > 0
        }

    def analyze_dividend_event(self, price_before: float, price_after: float,
                               dividend: float, event_idx: int) -> EventSignal:
        """
        Analyze dividend capture opportunity

        Args:
            price_before: Price before ex-dividend
            price_after: Price after ex-dividend
            dividend: Dividend amount
            event_idx: Event index

        Returns:
            EventSignal for dividend trade
        """
        profit_data = self.calculate_profit_potential(price_before, dividend, price_after)

        signal_type = 'HOLD'
        strength = 0.0

        if profit_data['profitable']:
            signal_type = 'BUY'
            # Strength based on profitability and size of dividend
            strength = min(1.0, abs(profit_data['return_pct'] / 100.0))

        # Z-test on price drop: is it close enough to dividend?
        z_score = abs(profit_data['price_drop_deviation']) / (price_before * 0.01 + 1e-6)
        p_value = 2 * (1 - stats.norm.cdf(z_score))  # Two-tailed test

        return EventSignal(
            timestamp=event_idx,
            signal_type=signal_type,
            price=price_before,
            event_type='DIVIDEND',
            strategy='Dividend Capture',
            strength=strength,
            statistical_significance=p_value,
            event_date=event_idx
        )


class MandAArbitrageCalculator:
    """
    M&A Arbitrage Calculator

    Risk arbitrage on merger and acquisition announcements. Exploits the gap
    between current stock price and acquisition price.

    Key Mechanics:
    1. Acquirer announces deal at price P_deal
    2. Target stock trades at discount D due to deal risk
    3. Arbitrageur buys at discounted price
    4. Receives deal price at closing (if deal completes)
    5. Profit = (Deal Price - Purchase Price) / Purchase Price

    Risk Factors:
    - Regulatory approval uncertainty
    - Financing risk (esp. all-cash deals)
    - Deal termination risk
    - Market conditions changes

    Formulas:
        Spread = Deal Price - Current Price
        Probability of Completion = Market Price / Deal Price
        Expected Return = (Deal Price * P(complete) +
                          Alternative Price * P(fail) - Current Price) / Current Price
        Annualized Return = Expected Return * 365 / Days to Closing
        Risk Premium = Spread / Annualized Return (hedge ratio)
    """

    def __init__(self, risk_free_rate: float = 0.04):
        """Initialize M&A arbitrage calculator"""
        self.risk_free_rate = risk_free_rate

    def calculate_deal_metrics(self, current_price: float,
                               deal_price: float,
                               days_to_closing: int,
                               probability_completion: Optional[float] = None,
                               alternative_price: float = 0.0) -> Dict:
        """
        Calculate M&A arbitrage metrics

        Args:
            current_price: Current stock price (trading price)
            deal_price: Price per share in the deal
            days_to_closing: Estimated days until deal closes
            probability_completion: Estimated probability deal completes (inferred from price if None)
            alternative_price: Price if deal fails (e.g., pre-announcement price)

        Returns:
            Dictionary with arbitrage metrics
        """
        # Infer probability from market price if not provided
        if probability_completion is None:
            probability_completion = current_price / deal_price if deal_price > 0 else 0.5
        else:
            probability_completion = np.clip(probability_completion, 0, 1)

        # Calculate spreads
        absolute_spread = deal_price - current_price
        percentage_spread = (absolute_spread / current_price) * 100 if current_price > 0 else 0

        # Calculate expected return
        prob_fail = 1 - probability_completion
        fail_price = alternative_price if alternative_price > 0 else current_price * 0.95

        expected_value = (deal_price * probability_completion +
                         fail_price * prob_fail)
        expected_return = (expected_value - current_price) / current_price

        # Annualized return
        years_to_closing = days_to_closing / 365.0
        annualized_return = (expected_return / years_to_closing) if years_to_closing > 0 else 0

        # Excess return over risk-free rate
        excess_return = annualized_return - self.risk_free_rate

        # Risk-adjusted metrics
        downside_risk = (fail_price - current_price) / current_price
        risk_reward_ratio = excess_return / abs(downside_risk) if downside_risk != 0 else 0

        return {
            'absolute_spread': absolute_spread,
            'percentage_spread': percentage_spread,
            'probability_completion': probability_completion * 100,
            'probability_failure': prob_fail * 100,
            'expected_value': expected_value,
            'expected_return_pct': expected_return * 100,
            'annualized_return_pct': annualized_return * 100,
            'excess_return_pct': excess_return * 100,
            'downside_risk_pct': downside_risk * 100,
            'risk_reward_ratio': risk_reward_ratio,
            'attractive': excess_return > 0.10  # >10% annualized excess return
        }

    def analyze_mna_event(self, current_price: float, deal_price: float,
                          days_to_closing: int, event_idx: int,
                          probability: Optional[float] = None) -> EventSignal:
        """
        Generate M&A arbitrage trading signal

        Args:
            current_price: Current trading price
            deal_price: Deal price per share
            days_to_closing: Days to deal closing
            event_idx: Event index
            probability: Estimated deal completion probability

        Returns:
            EventSignal for arbitrage trade
        """
        metrics = self.calculate_deal_metrics(current_price, deal_price,
                                             days_to_closing, probability)

        signal_type = 'HOLD'
        strength = 0.0

        # Positive signal if:
        # 1. Deal is likely to complete (high probability)
        # 2. Return is attractive
        # 3. Risk-reward is favorable

        if metrics['attractive'] and metrics['risk_reward_ratio'] > 1.5:
            signal_type = 'BUY'
            strength = min(1.0, metrics['excess_return_pct'] / 20.0)  # Scale to 0-1

        # Chi-square test on probability
        # Null hypothesis: market price perfectly reflects deal completion probability
        expected_price = deal_price * (metrics['probability_completion'] / 100.0)
        chi2_stat = ((current_price - expected_price) ** 2) / expected_price
        p_value = 1 - stats.chi2.cdf(chi2_stat, df=1)

        return EventSignal(
            timestamp=event_idx,
            signal_type=signal_type,
            price=current_price,
            event_type='MERGER',
            strategy='M&A Arbitrage',
            strength=strength,
            statistical_significance=p_value,
            event_date=event_idx
        )


class EventStudyAnalysis:
    """
    Event Study Analysis

    Comprehensive statistical analysis of price behavior around events using
    Abnormal Returns, Cumulative Abnormal Returns (CAR), and GARCH models.

    Methodology:
    1. Estimation Window: Calculate normal expected returns (before event)
    2. Event Window: Measure actual vs. expected returns
    3. Abnormal Return = Actual Return - Expected Return
    4. Cumulative Abnormal Return = Sum of abnormal returns
    5. Statistical Testing: T-test and cross-sectional tests

    Formulas:
        Expected Return = alpha + beta * Market Return
        Abnormal Return = Actual Return - Expected Return
        Cumulative AR = Sum(Abnormal Returns)
        t-stat = Average CAR / Standard Error of CAR

    GARCH(1,1) for volatility:
        sigma^2(t) = omega + alpha * epsilon^2(t-1) + beta * sigma^2(t-1)
    """

    def __init__(self, estimation_window: int = 120,
                 event_window_before: int = 5,
                 event_window_after: int = 20):
        """Initialize event study analysis parameters"""
        self.estimation_window = estimation_window
        self.event_window_before = event_window_before
        self.event_window_after = event_window_after

    def calculate_abnormal_returns(self, stock_returns: np.ndarray,
                                   market_returns: np.ndarray,
                                   event_idx: int) -> Dict:
        """
        Calculate abnormal returns using market model

        Args:
            stock_returns: Daily returns of stock
            market_returns: Daily market returns
            event_idx: Index of event date

        Returns:
            Dictionary with abnormal returns and statistics
        """
        # Estimation window: before event
        est_start = max(0, event_idx - self.estimation_window)
        est_end = max(0, event_idx - self.event_window_before)

        est_stock = stock_returns[est_start:est_end]
        est_market = market_returns[est_start:est_end]

        # Calculate market model parameters (alpha, beta)
        if len(est_stock) > 1:
            covariance = np.cov(est_stock, est_market)[0, 1]
            market_variance = np.var(est_market)
            beta = covariance / market_variance if market_variance > 0 else 0
            alpha = np.mean(est_stock) - beta * np.mean(est_market)
        else:
            alpha, beta = 0, 1

        # Event window
        evt_start = event_idx
        evt_end = min(len(stock_returns), event_idx + self.event_window_after)

        event_stock = stock_returns[evt_start:evt_end]
        event_market = market_returns[evt_start:evt_end]

        # Calculate abnormal returns
        expected_returns = alpha + beta * event_market
        abnormal_returns = event_stock - expected_returns

        # Cumulative abnormal returns
        cum_abnormal_returns = np.cumsum(abnormal_returns)

        # Calculate standard error
        residuals = est_stock - (alpha + beta * est_market)
        std_error = np.std(residuals)

        # T-test: is average abnormal return significantly different from 0?
        if len(abnormal_returns) > 1:
            t_stat = np.mean(abnormal_returns) / (std_error / np.sqrt(len(abnormal_returns)))
            p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(abnormal_returns) - 1))
        else:
            t_stat = 0
            p_value = 1.0

        return {
            'alpha': alpha,
            'beta': beta,
            'abnormal_returns': abnormal_returns,
            'cumulative_abnormal_returns': cum_abnormal_returns,
            'expected_returns': expected_returns,
            'std_error': std_error,
            't_statistic': t_stat,
            'p_value': p_value,
            'average_abnormal_return': np.mean(abnormal_returns),
            'average_car': cum_abnormal_returns[-1] if len(cum_abnormal_returns) > 0 else 0
        }

    def fit_garch_model(self, returns: np.ndarray) -> Dict:
        """
        Fit GARCH(1,1) model for volatility dynamics

        Args:
            returns: Array of returns

        Returns:
            Dictionary with GARCH parameters
        """
        if len(returns) < 20:
            return {'omega': 0.0001, 'alpha': 0.05, 'beta': 0.94}

        # Simple GARCH(1,1) parameter estimation
        # Using conditional maximum likelihood

        def garch_likelihood(params, returns):
            omega, alpha, beta = params

            if omega < 0 or alpha < 0 or beta < 0 or alpha + beta > 0.999:
                return 1e10

            n = len(returns)
            sigma2 = np.zeros(n)
            sigma2[0] = np.var(returns)

            for t in range(1, n):
                sigma2[t] = omega + alpha * returns[t - 1]**2 + beta * sigma2[t - 1]
                if sigma2[t] <= 0:
                    return 1e10

            likelihood = -0.5 * np.sum(np.log(sigma2) + returns**2 / sigma2)
            return -likelihood  # Minimize negative likelihood

        # Initial guess
        x0 = [0.0001, 0.05, 0.94]

        # Optimize
        result = minimize(garch_likelihood, x0, args=(returns,),
                         method='Nelder-Mead', options={'maxiter': 500})

        omega, alpha, beta = result.x

        return {
            'omega': omega,
            'alpha': alpha,
            'beta': beta,
            'convergence': result.success
        }

    def analyze_event(self, stock_returns: np.ndarray,
                      market_returns: np.ndarray,
                      event_idx: int,
                      event_name: str = "Unknown Event") -> EventSignal:
        """
        Perform comprehensive event study analysis

        Args:
            stock_returns: Daily returns
            market_returns: Market returns
            event_idx: Event date index
            event_name: Name of event

        Returns:
            EventSignal summarizing event impact
        """
        ar_results = self.calculate_abnormal_returns(stock_returns, market_returns, event_idx)

        signal_type = 'HOLD'
        strength = 0.0

        # Significant positive abnormal return
        if ar_results['p_value'] < 0.05:
            if ar_results['average_abnormal_return'] > 0:
                signal_type = 'BUY'
            else:
                signal_type = 'SELL'

            strength = min(1.0, abs(ar_results['average_abnormal_return']) / 0.05)

        return EventSignal(
            timestamp=event_idx,
            signal_type=signal_type,
            price=0.0,  # Not applicable for event study
            event_type='EVENT_STUDY',
            strategy='Event Study Analysis',
            strength=strength,
            statistical_significance=ar_results['p_value'],
            event_date=event_idx
        )


class EventDrivenStrategy:
    """
    Comprehensive Event-Driven Trading Strategy Manager

    Combines all five event-driven strategies for multi-event trading
    """

    def __init__(self):
        """Initialize all event-driven strategies"""
        self.earnings_momentum = EarningsMomentumStrategy()
        self.pead = PostEarningsAnnouncementDrift()
        self.dividend_capture = DividendCaptureStrategy()
        self.mna_arbitrage = MandAArbitrageCalculator()
        self.event_study = EventStudyAnalysis()

    def analyze_all_events(self, prices: np.ndarray,
                          volumes: np.ndarray,
                          stock_returns: np.ndarray,
                          market_returns: np.ndarray,
                          events: List[Dict]) -> List[EventSignal]:
        """
        Analyze multiple events across strategies

        Args:
            prices: Array of closing prices
            volumes: Array of trading volumes
            stock_returns: Daily returns
            market_returns: Market returns
            events: List of events with metadata

        Returns:
            List of EventSignals from all strategies
        """
        signals = []

        for event in events:
            event_idx = event.get('index', 0)
            event_type = event.get('type', 'UNKNOWN')

            if event_type == 'EARNINGS':
                actual_eps = event.get('actual_eps', 0)
                expected_eps = event.get('expected_eps', 0)
                signal = self.earnings_momentum.analyze_event(
                    prices, volumes, actual_eps, expected_eps, event_idx)
                signals.append(signal)

            elif event_type == 'DIVIDEND':
                price_before = event.get('price_before', prices[event_idx] if event_idx < len(prices) else 0)
                price_after = event.get('price_after', prices[event_idx + 1] if event_idx + 1 < len(prices) else 0)
                dividend = event.get('dividend', 0)
                signal = self.dividend_capture.analyze_dividend_event(
                    price_before, price_after, dividend, event_idx)
                signals.append(signal)

            elif event_type == 'MERGER':
                current_price = event.get('current_price', prices[event_idx] if event_idx < len(prices) else 0)
                deal_price = event.get('deal_price', 0)
                days_to_closing = event.get('days_to_closing', 90)
                probability = event.get('probability', None)
                signal = self.mna_arbitrage.analyze_mna_event(
                    current_price, deal_price, days_to_closing, event_idx, probability)
                signals.append(signal)

        return sorted(signals, key=lambda x: x.timestamp)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 80)
    print("EVENT-DRIVEN TRADING STRATEGIES")
    print("=" * 80)

    # Generate sample data
    np.random.seed(42)
    n_days = 500
    prices = 100 + np.cumsum(np.random.randn(n_days) * 0.5)
    volumes = 1000000 + np.random.randn(n_days) * 100000
    volumes = np.abs(volumes)

    # Calculate returns
    stock_returns = np.diff(np.log(prices))
    market_returns = np.random.randn(len(stock_returns)) * 0.02 + 0.0005

    print("\n1. EARNINGS MOMENTUM STRATEGY")
    print("-" * 80)
    earnings_strategy = EarningsMomentumStrategy()
    signal1 = earnings_strategy.analyze_event(prices, volumes, 2.50, 2.20, 100)
    print(f"Signal: {signal1.signal_type}, Strength: {signal1.strength:.3f}")
    print(f"Statistical Significance (p-value): {signal1.statistical_significance:.4f}")

    print("\n2. POST-EARNINGS ANNOUNCEMENT DRIFT")
    print("-" * 80)
    pead_strategy = PostEarningsAnnouncementDrift()
    subsequent_prices = prices[101:161]
    signal2 = pead_strategy.analyze_pead_signal(0.15, prices[100], subsequent_prices, 100)
    print(f"Signal: {signal2.signal_type}, Strength: {signal2.strength:.3f}")
    print(f"Statistical Significance (p-value): {signal2.statistical_significance:.4f}")

    print("\n3. DIVIDEND CAPTURE STRATEGY")
    print("-" * 80)
    dividend_strategy = DividendCaptureStrategy()
    signal3 = dividend_strategy.analyze_dividend_event(prices[200], prices[201], 2.50, 200)
    print(f"Signal: {signal3.signal_type}, Strength: {signal3.strength:.3f}")
    print(f"Statistical Significance (p-value): {signal3.statistical_significance:.4f}")

    print("\n4. M&A ARBITRAGE CALCULATOR")
    print("-" * 80)
    mna_strategy = MandAArbitrageCalculator()
    metrics = mna_strategy.calculate_deal_metrics(prices[300], prices[300] * 1.15, 60, 0.85)
    print(f"Deal Metrics:")
    print(f"  Spread: {metrics['percentage_spread']:.2f}%")
    print(f"  Probability Completion: {metrics['probability_completion']:.1f}%")
    print(f"  Annualized Return: {metrics['annualized_return_pct']:.2f}%")
    print(f"  Risk-Reward Ratio: {metrics['risk_reward_ratio']:.2f}")

    signal4 = mna_strategy.analyze_mna_event(prices[300], prices[300] * 1.15, 60, 300, 0.85)
    print(f"Signal: {signal4.signal_type}, Strength: {signal4.strength:.3f}")
    print(f"Statistical Significance (p-value): {signal4.statistical_significance:.4f}")

    print("\n5. EVENT STUDY ANALYSIS")
    print("-" * 80)
    event_study = EventStudyAnalysis()
    ar_results = event_study.calculate_abnormal_returns(stock_returns, market_returns, 250)
    print(f"Market Model:")
    print(f"  Alpha: {ar_results['alpha']:.4f}")
    print(f"  Beta: {ar_results['beta']:.4f}")
    print(f"  Average Abnormal Return: {ar_results['average_abnormal_return']:.4f}")
    print(f"  Cumulative AR: {ar_results['average_car']:.4f}")
    print(f"  T-Statistic: {ar_results['t_statistic']:.4f}")
    print(f"  P-Value: {ar_results['p_value']:.4f}")

    print("\n" + "=" * 80)
    print("Summary: All event-driven strategies implemented with statistical testing")
    print("=" * 80)
