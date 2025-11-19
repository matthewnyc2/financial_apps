"""
Calendar Effects Analysis Implementation

This module implements comprehensive calendar effect detection and analysis:
1. Day-of-week effect analysis
2. January effect detector
3. Turn-of-month strategy
4. Holiday effect analysis
5. Seasonality decomposition

Includes statistical significance testing for all effects.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy import stats
import warnings

warnings.filterwarnings('ignore')


@dataclass
class CalendarSignal:
    """Calendar effect signal dataclass"""
    timestamp: str
    signal_type: str  # 'BUY', 'SELL', 'HOLD'
    effect_name: str
    confidence: float  # 0-1
    p_value: float
    return_mean: float


class DayOfWeekEffect:
    """
    Day-of-Week Effect Analysis

    Studies the Monday Effect and other weekday anomalies.
    Theory: Average returns may vary systematically by day of week.

    Formula:
        Returns = β0 + Σ(βi × Dayᵢ) + ε
        where Dayᵢ are dummy variables for each weekday
    """

    def __init__(self, significance_level: float = 0.05):
        """Initialize with significance level for statistical tests"""
        self.significance_level = significance_level
        self.day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        self.results = {}

    def analyze(self, prices: pd.Series, dates: pd.DatetimeIndex) -> Dict:
        """
        Analyze day-of-week effects

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates

        Returns:
            Dictionary with day-of-week statistics
        """
        if len(prices) < 5:
            raise ValueError("Minimum 5 days of data required")

        # Calculate daily returns
        returns = prices.pct_change() * 100  # In percentage

        # Assign day of week
        df = pd.DataFrame({
            'date': dates,
            'return': returns.values,
            'day_of_week': dates.dayofweek,
            'day_name': dates.day_name()
        })

        # Group by day of week
        day_stats = {}
        f_statistic = None
        p_value_f = None

        for day in range(5):
            day_returns = df[df['day_of_week'] == day]['return'].dropna()
            if len(day_returns) > 0:
                day_stats[self.day_names[day]] = {
                    'mean': day_returns.mean(),
                    'std': day_returns.std(),
                    'count': len(day_returns),
                    'median': day_returns.median()
                }

        # ANOVA test
        groups = [df[df['day_of_week'] == i]['return'].dropna().values
                  for i in range(5) if len(df[df['day_of_week'] == i]) > 0]

        if len(groups) > 1:
            f_statistic, p_value_f = stats.f_oneway(*groups)

        # T-tests: Monday vs other days
        monday_returns = df[df['day_of_week'] == 0]['return'].dropna()
        other_returns = df[df['day_of_week'] != 0]['return'].dropna()

        t_stat, p_value_t = stats.ttest_ind(monday_returns, other_returns)

        self.results = {
            'day_stats': day_stats,
            'anova_f_statistic': f_statistic,
            'anova_p_value': p_value_f,
            'monday_effect': {
                't_statistic': t_stat,
                'p_value': p_value_t,
                'significant': p_value_t < self.significance_level,
                'monday_mean': monday_returns.mean(),
                'other_mean': other_returns.mean()
            }
        }

        return self.results

    def get_signal(self) -> Optional[CalendarSignal]:
        """Generate trading signal based on day-of-week effect"""
        if not self.results or 'monday_effect' not in self.results:
            return None

        monday_effect = self.results['monday_effect']
        if monday_effect['significant'] and monday_effect['monday_mean'] < 0:
            return CalendarSignal(
                timestamp=datetime.now().isoformat(),
                signal_type='SELL',
                effect_name='Monday Effect',
                confidence=min(0.9, 1.0 - monday_effect['p_value']),
                p_value=monday_effect['p_value'],
                return_mean=monday_effect['monday_mean']
            )
        return None


class JanuaryEffect:
    """
    January Effect Detector

    Studies the tendency for stocks to perform better in January.
    Theory: Tax loss harvesting reversals, year-end bonuses, new year optimism.

    Formula:
        January_Return = Mean(Return_January)
        Other_Return = Mean(Return_NonJanuary)
        Effect = January_Return - Other_Return
    """

    def __init__(self, significance_level: float = 0.05):
        """Initialize with significance level"""
        self.significance_level = significance_level
        self.results = {}

    def analyze(self, prices: pd.Series, dates: pd.DatetimeIndex) -> Dict:
        """
        Analyze January effect

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates

        Returns:
            Dictionary with January effect statistics
        """
        # Calculate monthly returns
        df = pd.DataFrame({
            'date': dates,
            'price': prices.values,
            'month': dates.month,
            'year': dates.year
        })

        # Group by year and month
        monthly_returns = df.groupby(['year', 'month'])['price'].agg(['first', 'last'])
        monthly_returns['return'] = ((monthly_returns['last'] - monthly_returns['first'])
                                     / monthly_returns['first'] * 100)

        january_returns = monthly_returns[monthly_returns.index.get_level_values(1) == 1]['return'].values
        other_returns = monthly_returns[monthly_returns.index.get_level_values(1) != 1]['return'].values

        # Statistical tests
        if len(january_returns) > 0 and len(other_returns) > 0:
            t_stat, p_value = stats.ttest_ind(january_returns, other_returns)
            mann_whitney_stat, mann_whitney_p = stats.mannwhitneyu(january_returns, other_returns)
        else:
            t_stat = p_value = mann_whitney_stat = mann_whitney_p = np.nan

        self.results = {
            'january_mean': np.mean(january_returns) if len(january_returns) > 0 else np.nan,
            'january_std': np.std(january_returns) if len(january_returns) > 0 else np.nan,
            'january_count': len(january_returns),
            'other_mean': np.mean(other_returns) if len(other_returns) > 0 else np.nan,
            'other_std': np.std(other_returns) if len(other_returns) > 0 else np.nan,
            'other_count': len(other_returns),
            'effect_size': (np.mean(january_returns) if len(january_returns) > 0 else 0) -
                          (np.mean(other_returns) if len(other_returns) > 0 else 0),
            't_statistic': t_stat,
            'p_value': p_value,
            'mann_whitney_u': mann_whitney_stat,
            'mann_whitney_p': mann_whitney_p,
            'significant': p_value < self.significance_level if not np.isnan(p_value) else False,
            'effect_direction': 'positive' if (np.mean(january_returns) if len(january_returns) > 0 else 0) > 0 else 'negative'
        }

        return self.results

    def get_signal(self) -> Optional[CalendarSignal]:
        """Generate trading signal based on January effect"""
        if not self.results:
            return None

        if self.results['significant'] and self.results['effect_direction'] == 'positive':
            return CalendarSignal(
                timestamp=datetime.now().isoformat(),
                signal_type='BUY',
                effect_name='January Effect',
                confidence=min(0.85, 1.0 - self.results['p_value']),
                p_value=self.results['p_value'],
                return_mean=self.results['january_mean']
            )
        return None


class TurnOfMonthStrategy:
    """
    Turn-of-Month Strategy

    Exploits the tendency for returns to be higher at month boundaries.
    Typically: Last 3 days of month + first 3 days of next month

    Formula:
        TOM_Return = Mean(Return_TOM_Period)
        Mid_Return = Mean(Return_Mid_Month)
        Strategy_Excess = TOM_Return - Mid_Return
    """

    def __init__(self, days_before: int = 3, days_after: int = 3,
                 significance_level: float = 0.05):
        """Initialize with TOM period parameters"""
        self.days_before = days_before
        self.days_after = days_after
        self.significance_level = significance_level
        self.results = {}

    def is_tom_period(self, date: pd.Timestamp) -> bool:
        """Check if date is in turn-of-month period"""
        days_in_month = pd.Timestamp(
            year=date.year,
            month=date.month if date.month < 12 else 1,
            day=1
        ) - pd.Timedelta(days=1)
        days_in_month = days_in_month.day

        # Last N days of month
        if date.day > (days_in_month - self.days_before):
            return True

        # First N days of month
        if date.day <= self.days_after:
            return True

        return False

    def analyze(self, prices: pd.Series, dates: pd.DatetimeIndex) -> Dict:
        """
        Analyze turn-of-month effect

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates

        Returns:
            Dictionary with TOM statistics
        """
        returns = prices.pct_change() * 100

        df = pd.DataFrame({
            'date': dates,
            'return': returns.values,
            'is_tom': [self.is_tom_period(d) for d in dates]
        })

        tom_returns = df[df['is_tom']]['return'].dropna()
        mid_returns = df[~df['is_tom']]['return'].dropna()

        if len(tom_returns) > 0 and len(mid_returns) > 0:
            t_stat, p_value = stats.ttest_ind(tom_returns, mid_returns)
        else:
            t_stat = p_value = np.nan

        self.results = {
            'tom_mean': tom_returns.mean(),
            'tom_std': tom_returns.std(),
            'tom_count': len(tom_returns),
            'mid_month_mean': mid_returns.mean(),
            'mid_month_std': mid_returns.std(),
            'mid_month_count': len(mid_returns),
            'excess_return': tom_returns.mean() - mid_returns.mean(),
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.significance_level if not np.isnan(p_value) else False,
            'sharpe_tom': tom_returns.mean() / tom_returns.std() if tom_returns.std() > 0 else 0,
            'sharpe_mid': mid_returns.mean() / mid_returns.std() if mid_returns.std() > 0 else 0
        }

        return self.results

    def get_signals(self, dates: pd.DatetimeIndex) -> List[CalendarSignal]:
        """Generate trading signals for TOM periods"""
        if not self.results or not self.results['significant']:
            return []

        signals = []
        for date in dates:
            if self.is_tom_period(date) and self.results['excess_return'] > 0:
                signals.append(CalendarSignal(
                    timestamp=date.isoformat(),
                    signal_type='BUY',
                    effect_name='Turn-of-Month',
                    confidence=min(0.8, 1.0 - self.results['p_value']),
                    p_value=self.results['p_value'],
                    return_mean=self.results['tom_mean']
                ))
        return signals


class HolidayEffect:
    """
    Holiday Effect Analysis

    Studies returns around market holidays and calendar events.
    Theory: Pre-holiday drift, holiday seasonality effects.

    Formula:
        Holiday_Return = Mean(Return_PreHoliday + Return_PostHoliday)
        Normal_Return = Mean(Return_NonHoliday)
    """

    def __init__(self, significance_level: float = 0.05):
        """Initialize with significance level"""
        self.significance_level = significance_level
        self.us_holidays = self._get_us_holidays()
        self.results = {}

    @staticmethod
    def _get_us_holidays() -> Dict[int, List[Tuple[int, int]]]:
        """Get US market holidays (month, day) - simplified list"""
        return {
            1: [(1, 1)],  # New Year's Day
            7: [(4, 7)],  # Independence Day
            11: [(23, 11)],  # Thanksgiving (4th Thursday)
            12: [(25, 12)]  # Christmas
        }

    def is_near_holiday(self, date: pd.Timestamp, days_window: int = 1) -> Tuple[bool, str]:
        """Check if date is near a holiday"""
        month = date.month
        day = date.day

        holiday_name = None
        if month in self.us_holidays:
            for holiday_day, holiday_month in self.us_holidays[month]:
                if abs(day - holiday_day) <= days_window:
                    holiday_name = {
                        (1, 1): 'New Year',
                        (7, 4): 'Independence Day',
                        (11, 23): 'Thanksgiving',
                        (12, 25): 'Christmas'
                    }.get((holiday_month, holiday_day), 'Holiday')
                    return True, holiday_name

        return False, holiday_name

    def analyze(self, prices: pd.Series, dates: pd.DatetimeIndex,
                days_window: int = 1) -> Dict:
        """
        Analyze holiday effects

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates
            days_window: Days before/after holiday to consider

        Returns:
            Dictionary with holiday effect statistics
        """
        returns = prices.pct_change() * 100

        df = pd.DataFrame({
            'date': dates,
            'return': returns.values
        })

        df['near_holiday'], df['holiday_name'] = zip(*[
            self.is_near_holiday(d, days_window) for d in dates
        ])

        holiday_returns = df[df['near_holiday']]['return'].dropna()
        normal_returns = df[~df['near_holiday']]['return'].dropna()

        if len(holiday_returns) > 0 and len(normal_returns) > 0:
            t_stat, p_value = stats.ttest_ind(holiday_returns, normal_returns)
        else:
            t_stat = p_value = np.nan

        self.results = {
            'holiday_mean': holiday_returns.mean(),
            'holiday_std': holiday_returns.std(),
            'holiday_count': len(holiday_returns),
            'normal_mean': normal_returns.mean(),
            'normal_std': normal_returns.std(),
            'normal_count': len(normal_returns),
            'effect_size': holiday_returns.mean() - normal_returns.mean(),
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.significance_level if not np.isnan(p_value) else False,
            'holiday_names': df[df['near_holiday']]['holiday_name'].unique().tolist()
        }

        return self.results

    def get_signal(self) -> Optional[CalendarSignal]:
        """Generate trading signal based on holiday effect"""
        if not self.results:
            return None

        if self.results['significant'] and self.results['effect_size'] > 0:
            return CalendarSignal(
                timestamp=datetime.now().isoformat(),
                signal_type='BUY',
                effect_name='Holiday Effect',
                confidence=min(0.75, 1.0 - self.results['p_value']),
                p_value=self.results['p_value'],
                return_mean=self.results['holiday_mean']
            )
        return None


class SeasonalityDecomposition:
    """
    Seasonality Decomposition

    Decomposes price series into trend, seasonal, and residual components.
    Uses additive model: Y = Trend + Seasonal + Residual

    Formula:
        Seasonal(t) = Y(t) - Trend(t)  [after residual removal]
        Seasonal_Index = Seasonal / Mean(|Seasonal|)
    """

    def __init__(self, period: int = 252):  # Default: trading days per year
        """Initialize with seasonal period"""
        self.period = period
        self.results = {}

    def decompose(self, prices: pd.Series, dates: pd.DatetimeIndex) -> Dict:
        """
        Decompose price series into trend, seasonal, residual

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates

        Returns:
            Dictionary with decomposition components
        """
        # Convert to log returns for multiplicative nature
        log_prices = np.log(prices)
        returns = log_prices.diff() * 100

        # Calculate trend using centered moving average
        trend = returns.rolling(window=self.period, center=True).mean()

        # Calculate seasonal component
        detrended = returns - trend
        seasonal = detrended.groupby(detrended.index.dayofyear).transform('mean')

        # Calculate residual
        residual = returns - trend - seasonal

        # Monthly seasonality
        df = pd.DataFrame({
            'return': returns.values,
            'month': dates.month,
            'day_of_year': dates.dayofyear
        })

        monthly_seasonal = df.groupby('month')['return'].agg(['mean', 'std', 'count'])

        # Test for seasonality significance (Kruskal-Wallis)
        groups = [df[df['month'] == m]['return'].dropna().values for m in range(1, 13)]
        groups = [g for g in groups if len(g) > 0]

        if len(groups) > 1:
            h_stat, p_value = stats.kruskal(*groups)
        else:
            h_stat = p_value = np.nan

        self.results = {
            'trend': trend.values,
            'seasonal': seasonal.values,
            'residual': residual.values,
            'monthly_seasonal': monthly_seasonal.to_dict('index'),
            'kruskal_wallis_h': h_stat,
            'kruskal_wallis_p': p_value,
            'seasonality_significant': p_value < 0.05 if not np.isnan(p_value) else False,
            'trend_direction': 'up' if trend.dropna().iloc[-1] > trend.dropna().iloc[0] else 'down',
            'seasonal_amplitude': seasonal.std()
        }

        return self.results

    def get_monthly_seasonality(self) -> Dict:
        """Get seasonal indices by month"""
        if 'monthly_seasonal' not in self.results:
            return {}

        monthly_data = self.results['monthly_seasonal']
        seasonal_indices = {}

        for month in range(1, 13):
            month_name = pd.Timestamp(2024, month, 1).strftime('%B')
            if month in monthly_data:
                seasonal_indices[month_name] = {
                    'mean_return': monthly_data[month]['mean'],
                    'std_return': monthly_data[month]['std'],
                    'count': int(monthly_data[month]['count'])
                }

        return seasonal_indices


class CalendarEffectsAnalyzer:
    """
    Comprehensive Calendar Effects Analyzer

    Combines all calendar effects for integrated analysis.
    """

    def __init__(self):
        """Initialize all calendar effect analyzers"""
        self.dow_effect = DayOfWeekEffect()
        self.january_effect = JanuaryEffect()
        self.tom_strategy = TurnOfMonthStrategy()
        self.holiday_effect = HolidayEffect()
        self.seasonality = SeasonalityDecomposition()
        self.signals = []

    def analyze_all(self, prices: pd.Series, dates: pd.DatetimeIndex) -> Dict:
        """
        Run comprehensive calendar effects analysis

        Args:
            prices: Series of closing prices
            dates: DatetimeIndex of dates

        Returns:
            Dictionary with all analysis results
        """
        results = {
            'day_of_week': self.dow_effect.analyze(prices, dates),
            'january_effect': self.january_effect.analyze(prices, dates),
            'turn_of_month': self.tom_strategy.analyze(prices, dates),
            'holiday_effect': self.holiday_effect.analyze(prices, dates),
            'seasonality': self.seasonality.decompose(prices, dates)
        }

        # Generate signals
        dow_signal = self.dow_effect.get_signal()
        if dow_signal:
            self.signals.append(dow_signal)

        jan_signal = self.january_effect.get_signal()
        if jan_signal:
            self.signals.append(jan_signal)

        tom_signals = self.tom_strategy.get_signals(dates)
        self.signals.extend(tom_signals)

        holiday_signal = self.holiday_effect.get_signal()
        if holiday_signal:
            self.signals.append(holiday_signal)

        results['signals'] = self.signals
        return results

    def get_summary(self) -> Dict:
        """Get summary of all calendar effects"""
        summary = {
            'total_signals': len(self.signals),
            'buy_signals': len([s for s in self.signals if s.signal_type == 'BUY']),
            'sell_signals': len([s for s in self.signals if s.signal_type == 'SELL']),
            'average_confidence': np.mean([s.confidence for s in self.signals])
                                 if self.signals else 0,
            'effects_detected': []
        }

        for signal in self.signals:
            if signal.effect_name not in summary['effects_detected']:
                summary['effects_detected'].append(signal.effect_name)

        return summary
