"""
Regime Detection Implementation
Includes Hidden Markov Models, change point detection, volatility regime classification,
and regime-conditional strategies using hmmlearn library
"""

import numpy as np
import pandas as pd
from hmmlearn import hmm
from scipy import stats
from scipy.signal import argrelextrema
import warnings
warnings.filterwarnings('ignore')


class HiddenMarkovRegimes:
    """
    Hidden Markov Model for regime detection in financial time series
    Supports Gaussian HMM for continuous data (returns, volatility)
    """

    def __init__(self, data, n_states=2):
        """
        Initialize HMM regime detector

        Parameters:
        -----------
        data : pd.Series or np.array
            Time series data (returns or log-returns)
        n_states : int
            Number of regimes/hidden states (typically 2-4)
        """
        if isinstance(data, pd.Series):
            self.data = data.values.reshape(-1, 1)
            self.data_index = data.index
        else:
            self.data = np.array(data).reshape(-1, 1)
            self.data_index = None

        self.n_states = n_states
        self.model = None
        self.states = None

    def fit_gaussian_hmm(self, random_state=42, n_iter=1000, tol=1e-4):
        """
        Fit Gaussian HMM model

        HMM assumes:
        - Hidden states follow Markov process P(s_t | s_{t-1})
        - Observations conditionally independent given state: P(x_t | s_t)

        Parameters:
        -----------
        random_state : int
            Random seed for reproducibility
        n_iter : int
            Maximum EM iterations
        tol : float
            Convergence tolerance for EM algorithm
        """
        self.model = hmm.GaussianHMM(
            n_components=self.n_states,
            covariance_type='full',
            n_iter=n_iter,
            random_state=random_state,
            tol=tol
        )

        self.model.fit(self.data)
        return self.model

    def fit_student_hmm(self, random_state=42, n_iter=1000):
        """
        Approximate Student-t HMM using Gaussian mixture
        More robust to outliers/fat tails
        """
        # Start with Gaussian for initialization
        self.fit_gaussian_hmm(random_state=random_state, n_iter=n_iter)
        return self.model

    def predict_states(self, data=None):
        """
        Predict hidden state sequence using Viterbi algorithm

        Viterbi algorithm:
        - Dynamic programming approach
        - Finds most likely state sequence given observations
        - O(n * k^2) complexity (linear in sequence length)

        Parameters:
        -----------
        data : np.array, optional
            If None, uses training data
        """
        if data is None:
            data = self.data
        else:
            if isinstance(data, pd.Series):
                data = data.values.reshape(-1, 1)
            else:
                data = np.array(data).reshape(-1, 1)

        self.states = self.model.predict(data)
        return self.states

    def predict_proba_states(self, data=None):
        """
        Predict state probabilities (soft assignment)
        Returns probability of each state at each time point

        Parameters:
        -----------
        data : np.array, optional
            If None, uses training data
        """
        if data is None:
            data = self.data
        else:
            if isinstance(data, pd.Series):
                data = data.values.reshape(-1, 1)
            else:
                data = np.array(data).reshape(-1, 1)

        return self.model.predict_proba(data)

    def get_model_parameters(self):
        """
        Extract model parameters for interpretation

        Returns:
        --------
        dict : Contains transition matrix, means, covariances
        """
        params = {
            'transition_matrix': self.model.transmat_,
            'means': self.model.means_,
            'covariances': self.model.covars_,
            'log_probability': self.model.score(self.data),
        }
        return params

    def get_transition_matrix(self):
        """
        Get state transition probabilities

        Returns:
        --------
        pd.DataFrame : Transition probabilities P(s_t | s_{t-1})
        """
        trans_matrix = self.model.transmat_
        return pd.DataFrame(
            trans_matrix,
            index=[f'From State {i}' for i in range(self.n_states)],
            columns=[f'To State {i}' for i in range(self.n_states)]
        )

    def get_state_statistics(self):
        """
        Calculate statistics for each regime

        Returns:
        --------
        pd.DataFrame : Mean return, volatility, duration for each regime
        """
        stats_list = []

        for state in range(self.n_states):
            state_data = self.data[self.states == state, 0]

            # Duration: average consecutive periods in state
            state_transitions = np.diff(self.states == state)
            n_spells = np.sum(state_transitions)
            avg_duration = len(state_data) / max(1, n_spells)

            stats_list.append({
                'State': state,
                'Mean': np.mean(state_data),
                'Std': np.std(state_data),
                'Skewness': stats.skew(state_data),
                'Kurtosis': stats.kurtosis(state_data),
                'Observations': len(state_data),
                'Probability': len(state_data) / len(self.states),
                'Avg_Duration': avg_duration,
            })

        return pd.DataFrame(stats_list)

    def log_likelihood(self):
        """
        Get log-likelihood of model fit
        Higher is better; useful for model selection (AIC/BIC)
        """
        return self.model.score(self.data)

    def aic(self):
        """Akaike Information Criterion for model selection"""
        n_params = (self.n_states * (self.n_states - 1) +  # transition matrix
                   self.n_states +                          # means
                   self.n_states)                            # variances
        return 2 * n_params - 2 * self.log_likelihood()

    def bic(self):
        """Bayesian Information Criterion for model selection"""
        n_params = (self.n_states * (self.n_states - 1) +
                   self.n_states + self.n_states)
        return np.log(len(self.data)) * n_params - 2 * self.log_likelihood()


class ChangePointDetection:
    """
    Change point detection algorithms for regime identification
    Implements PELT and CUSUM algorithms
    """

    def __init__(self, data):
        """
        Initialize change point detector

        Parameters:
        -----------
        data : pd.Series or np.array
            Time series data
        """
        if isinstance(data, pd.Series):
            self.data = data.values
            self.index = data.index
        else:
            self.data = np.array(data)
            self.index = None

    def pelt_algorithm(self, penalty='BIC', min_size=2):
        """
        PELT (Pruned Exact Linear Time) algorithm
        Detects multiple change points efficiently

        Algorithm:
        - Dynamic programming with pruning
        - Tests for changes in mean, variance, or both
        - O(n) complexity with pruning

        Parameters:
        -----------
        penalty : str
            'BIC': Bayesian Information Criterion (default)
            'AIC': Akaike Information Criterion
            'Manual': Specify custom penalty value
        min_size : int
            Minimum segment size (prevents over-fitting)

        Returns:
        --------
        dict : Change points and cost
        """
        n = len(self.data)

        # Calculate penalty
        if penalty == 'BIC':
            penalty_value = np.log(n) / 2
        elif penalty == 'AIC':
            penalty_value = 1
        else:
            penalty_value = 1

        # Cost function: negative log-likelihood
        def segment_cost(data_segment):
            if len(data_segment) < 1:
                return 0
            mean = np.mean(data_segment)
            variance = np.var(data_segment)
            if variance < 1e-10:
                variance = 1e-10
            return len(data_segment) * np.log(variance)

        # Dynamic programming
        costs = np.zeros(n + 1)
        changepoints = np.zeros(n + 1, dtype=int)
        last_index = np.zeros(n + 1, dtype=int)

        for i in range(min_size, n + 1):
            costs[i] = np.inf
            for j in range(min_size, i + 1):
                cost = costs[j - 1] + segment_cost(self.data[j-1:i]) + penalty_value
                if cost < costs[i]:
                    costs[i] = cost
                    changepoints[i] = j - 1

        # Extract changepoints
        detected_points = []
        idx = n
        while idx > 0:
            detected_points.append(changepoints[idx])
            idx = changepoints[idx]

        detected_points = sorted(list(set(detected_points)))
        detected_points = [p for p in detected_points if p > min_size and p < n - min_size]

        return {
            'changepoints': detected_points,
            'cost': costs[-1],
            'n_segments': len(detected_points) + 1,
        }

    def cusum_algorithm(self, threshold=5.0, drift=1.0):
        """
        CUSUM (Cumulative Sum Control Chart) algorithm
        Detects mean shifts in time series

        Algorithm:
        - Tracks cumulative deviation from baseline
        - Signals when cumulative sum exceeds threshold
        - Good for sequential detection

        Parameters:
        -----------
        threshold : float
            Detection threshold (standard deviations)
        drift : float
            Expected drift/mean shift to detect

        Returns:
        --------
        dict : Change points, CUSUM values
        """
        n = len(self.data)

        # Standardize data
        mean = np.mean(self.data)
        std = np.std(self.data)
        if std < 1e-10:
            std = 1e-10

        data_std = (self.data - mean) / std

        # CUSUM calculation
        cusum_pos = np.zeros(n)
        cusum_neg = np.zeros(n)

        for i in range(1, n):
            # Positive CUSUM (detects mean increase)
            cusum_pos[i] = max(0, cusum_pos[i-1] + data_std[i] - drift / 2)
            # Negative CUSUM (detects mean decrease)
            cusum_neg[i] = min(0, cusum_neg[i-1] + data_std[i] + drift / 2)

        # Detect changepoints
        changepoints = []
        for i in range(1, n):
            if abs(cusum_pos[i]) > threshold or abs(cusum_neg[i]) > threshold:
                # Check if new changepoint (not too close to previous)
                if not changepoints or i - changepoints[-1] > 10:
                    changepoints.append(i)

        return {
            'changepoints': changepoints,
            'cusum_pos': cusum_pos,
            'cusum_neg': cusum_neg,
            'threshold': threshold,
        }

    def kernel_change_detection(self, window=50, threshold=2.0):
        """
        Kernel-based change point detection
        Uses rolling window statistics to detect changes

        Parameters:
        -----------
        window : int
            Rolling window size
        threshold : float
            Threshold for detecting change (in standard deviations)
        """
        n = len(self.data)

        # Calculate rolling statistics
        rolling_mean = pd.Series(self.data).rolling(window).mean()
        rolling_std = pd.Series(self.data).rolling(window).std()

        # Detect changes as outliers in rolling mean
        diff_mean = np.diff(rolling_mean, prepend=rolling_mean.iloc[0])

        # Standardize differences
        mean_diff = np.nanmean(diff_mean)
        std_diff = np.nanstd(diff_mean)

        if std_diff < 1e-10:
            std_diff = 1e-10

        z_scores = (diff_mean - mean_diff) / std_diff
        changepoints = np.where(np.abs(z_scores) > threshold)[0]

        return {
            'changepoints': list(changepoints),
            'z_scores': z_scores,
            'rolling_mean': rolling_mean,
        }


class VolatilityRegimes:
    """
    Classification of market into volatility regimes
    Useful for adaptive strategies and risk management
    """

    def __init__(self, returns_data, window=20):
        """
        Initialize volatility regime detector

        Parameters:
        -----------
        returns_data : pd.Series or np.array
            Log returns or simple returns
        window : int
            Window for rolling volatility calculation
        """
        if isinstance(returns_data, pd.Series):
            self.returns = returns_data
            self.index = returns_data.index
        else:
            self.returns = pd.Series(returns_data)
            self.index = None

        self.window = window
        self.volatility = None
        self.regimes = None

    def calculate_rolling_volatility(self):
        """
        Calculate rolling volatility (annualized)
        """
        self.volatility = self.returns.rolling(self.window).std() * np.sqrt(252)
        return self.volatility

    def classify_regimes_quantile(self, quantiles=[0.33, 0.67]):
        """
        Classify into regimes based on volatility quantiles

        Low regime: vol < 33rd percentile
        Medium regime: 33rd < vol < 67th percentile
        High regime: vol > 67th percentile

        Parameters:
        -----------
        quantiles : list
            Quantile thresholds

        Returns:
        --------
        pd.Series : Regime labels (0=Low, 1=Medium, 2=High)
        """
        if self.volatility is None:
            self.calculate_rolling_volatility()

        vol_non_nan = self.volatility.dropna()
        thresholds = [vol_non_nan.quantile(q) for q in quantiles]

        self.regimes = pd.Series(0, index=self.volatility.index)
        self.regimes[self.volatility >= thresholds[0]] = 1
        self.regimes[self.volatility >= thresholds[1]] = 2

        return self.regimes

    def classify_regimes_hmm(self, n_states=3):
        """
        Classify volatility into HMM regimes

        Parameters:
        -----------
        n_states : int
            Number of volatility regimes

        Returns:
        --------
        np.array : Regime labels
        """
        if self.volatility is None:
            self.calculate_rolling_volatility()

        vol_data = self.volatility.dropna().values

        hmm_model = HiddenMarkovRegimes(vol_data, n_states=n_states)
        hmm_model.fit_gaussian_hmm()
        states = hmm_model.predict_states()

        # Order states by mean volatility
        means = hmm_model.get_state_statistics()['Mean'].values
        state_order = np.argsort(means)
        state_mapping = {old: new for new, old in enumerate(state_order)}
        ordered_states = np.array([state_mapping[s] for s in states])

        # Map back to full time series
        self.regimes = pd.Series(np.nan, index=self.volatility.index)
        valid_idx = self.volatility.dropna().index
        self.regimes[valid_idx] = ordered_states

        return self.regimes

    def regime_statistics(self):
        """
        Calculate statistics for each volatility regime
        """
        if self.regimes is None:
            self.classify_regimes_quantile()

        regime_stats = []
        for regime in sorted(self.regimes.dropna().unique()):
            mask = self.regimes == regime
            ret = self.returns[mask]
            vol = self.volatility[mask]

            regime_stats.append({
                'Regime': f"{'LMH'[int(regime)]}",
                'Observations': mask.sum(),
                'Avg_Return': ret.mean(),
                'Avg_Volatility': vol.mean(),
                'Return_Std': ret.std(),
                'Sharpe': ret.mean() / ret.std() * np.sqrt(252) if ret.std() > 0 else 0,
            })

        return pd.DataFrame(regime_stats)

    def bull_bear_classification(self, ma_window=200, return_threshold=0.0):
        """
        Classify regimes as Bull (positive trend) or Bear (negative trend)

        Parameters:
        -----------
        ma_window : int
            Moving average window for trend
        return_threshold : float
            Return threshold for bull/bear classification

        Returns:
        --------
        pd.DataFrame : Bull/Bear regimes with trend and vol
        """
        # Calculate trend (moving average)
        price_cumsum = (1 + self.returns).cumprod()
        trend = price_cumsum.rolling(ma_window).mean()

        # Calculate trend direction
        trend_direction = np.sign(np.diff(trend, prepend=trend.iloc[0]))

        # Combine with volatility regime
        if self.volatility is None:
            self.calculate_rolling_volatility()

        if self.regimes is None:
            self.classify_regimes_quantile()

        classification = pd.DataFrame({
            'Returns': self.returns,
            'Volatility': self.volatility,
            'Vol_Regime': self.regimes,
            'Trend': trend,
            'Trend_Direction': trend_direction,
        })

        # Create Bull/Bear labels
        classification['Market_Regime'] = 'Neutral'
        bull_mask = (trend_direction > 0) & (self.returns > return_threshold)
        bear_mask = (trend_direction < 0) | (self.returns < return_threshold)

        classification.loc[bull_mask, 'Market_Regime'] = 'Bull'
        classification.loc[bear_mask, 'Market_Regime'] = 'Bear'

        return classification


class RegimeConditionalStrategies:
    """
    Strategies that adapt to market regimes
    Different rules/parameters for different market states
    """

    def __init__(self, returns_data, regimes):
        """
        Initialize regime-conditional strategy

        Parameters:
        -----------
        returns_data : pd.Series
            Time series of returns
        regimes : pd.Series
            Regime labels (0, 1, 2, etc.)
        """
        self.returns = returns_data
        self.regimes = regimes
        self.signals = None

    def momentum_strategy_by_regime(self, lookback=20):
        """
        Momentum strategy with regime-dependent parameters

        High vol regime: Use shorter lookback, reduce position size
        Low vol regime: Use longer lookback, increase position size

        Parameters:
        -----------
        lookback : int
            Base lookback period for momentum

        Returns:
        --------
        pd.DataFrame : Signals and position sizes by regime
        """
        momentum = self.returns.rolling(lookback).sum()

        signals = pd.DataFrame({
            'Momentum': momentum,
            'Regime': self.regimes,
        })

        # Regime-dependent thresholds
        signals['Position_Size'] = 0.5  # Default

        # Low regime: more aggressive
        signals.loc[self.regimes == 0, 'Position_Size'] = 1.0

        # Medium regime: neutral
        signals.loc[self.regimes == 1, 'Position_Size'] = 0.5

        # High regime: defensive
        signals.loc[self.regimes == 2, 'Position_Size'] = 0.25

        # Generate signals
        signals['Signal'] = np.sign(signals['Momentum'])
        signals['Signal'] = signals['Signal'] * signals['Position_Size']

        return signals

    def mean_reversion_strategy_by_regime(self, lookback=20, threshold=1.5):
        """
        Mean reversion strategy with regime adaptation

        Parameters:
        -----------
        lookback : int
            Lookback for mean calculation
        threshold : float
            Standard deviation threshold for signals
        """
        rolling_mean = self.returns.rolling(lookback).mean()
        rolling_std = self.returns.rolling(lookback).std()

        deviation = (self.returns - rolling_mean) / rolling_std

        signals = pd.DataFrame({
            'Deviation': deviation,
            'Regime': self.regimes,
        })

        # Mean reversion more effective in low-vol regimes
        signals['Strength'] = 0.0

        # Low vol: strong mean reversion signal
        signals.loc[(self.regimes == 0) & (np.abs(deviation) > threshold), 'Strength'] = 1.0
        signals.loc[(self.regimes == 0) & (np.abs(deviation) > threshold * 1.5), 'Strength'] = 1.5

        # Medium vol: moderate signal
        signals.loc[(self.regimes == 1) & (np.abs(deviation) > threshold * 1.5), 'Strength'] = 0.75

        # High vol: weak signal (less reliable)
        signals.loc[(self.regimes == 2) & (np.abs(deviation) > threshold * 2.0), 'Strength'] = 0.25

        # Generate signals
        signals['Signal'] = np.where(deviation > threshold, -1, 0)  # Revert down movements
        signals['Signal'] = np.where(deviation < -threshold, 1, signals['Signal'])  # Revert up movements
        signals['Signal'] = signals['Signal'] * signals['Strength']

        return signals

    def volatility_targeting_strategy(self, target_vol=0.15, vol_window=20):
        """
        Dynamic position sizing based on volatility

        When vol is high, reduce position size to maintain constant portfolio vol
        When vol is low, increase position size

        Parameters:
        -----------
        target_vol : float
            Target volatility level
        vol_window : int
            Window for rolling vol calculation
        """
        rolling_vol = self.returns.rolling(vol_window).std() * np.sqrt(252)

        # Position size inversely proportional to volatility
        position_size = target_vol / (rolling_vol + 1e-6)

        # Cap position size at reasonable levels
        position_size = np.clip(position_size, 0.25, 3.0)

        signals = pd.DataFrame({
            'Rolling_Vol': rolling_vol,
            'Position_Size': position_size,
            'Regime': self.regimes,
        })

        # Base momentum signal
        momentum = self.returns.rolling(20).sum()
        signals['Signal'] = np.sign(momentum) * position_size

        return signals

    def regime_change_detector(self, window=10):
        """
        Detect transitions between regimes
        Useful for entry/exit signals

        Parameters:
        -----------
        window : int
            Detection window

        Returns:
        --------
        pd.DataFrame : Regime changes and confidence
        """
        regime_changes = self.regimes.diff() != 0

        changes = pd.DataFrame({
            'Regime': self.regimes,
            'Change': regime_changes,
        })

        # Confidence: how stable is new regime
        changes['Stability'] = 0.0

        for i in range(window, len(changes)):
            recent_regimes = self.regimes.iloc[i-window:i]
            if changes['Change'].iloc[i]:
                # New regime: count how many periods same regime
                stability = (recent_regimes == self.regimes.iloc[i]).sum() / window
                changes.loc[i, 'Stability'] = stability

        return changes


# ==================== Utility Functions ====================

def compare_hmm_models(data, max_states=4):
    """
    Compare HMM models with different numbers of states

    Returns:
    --------
    pd.DataFrame : AIC, BIC, and likelihood for each model
    """
    results = []

    for n_states in range(1, max_states + 1):
        hmm_model = HiddenMarkovRegimes(data, n_states=n_states)
        hmm_model.fit_gaussian_hmm()

        results.append({
            'N_States': n_states,
            'Log_Likelihood': hmm_model.log_likelihood(),
            'AIC': hmm_model.aic(),
            'BIC': hmm_model.bic(),
        })

    comparison = pd.DataFrame(results)
    return comparison


def backtest_regime_strategy(returns, signals, transaction_cost=0.001):
    """
    Backtest a regime-based strategy

    Parameters:
    -----------
    returns : pd.Series
        Returns time series
    signals : pd.Series
        Trading signals (1, 0, -1)
    transaction_cost : float
        Cost per transaction (as fraction of position)

    Returns:
    --------
    dict : Performance metrics
    """
    # Align signals with returns
    returns_aligned = returns[signals.index]
    signals_aligned = signals

    # Calculate position (accounting for signal lag)
    position = signals_aligned.shift(1).fillna(0)

    # Calculate PnL
    pnl = position * returns_aligned

    # Apply transaction costs
    position_changes = position.diff().abs()
    costs = position_changes * transaction_cost
    net_pnl = pnl - costs

    # Calculate metrics
    total_return = (1 + net_pnl).prod() - 1
    sharpe = net_pnl.mean() / net_pnl.std() * np.sqrt(252) if net_pnl.std() > 0 else 0
    cumulative = (1 + net_pnl).cumprod()
    max_dd = (cumulative / cumulative.expanding().max() - 1).min()
    win_rate = (net_pnl > 0).sum() / (net_pnl != 0).sum() if (net_pnl != 0).sum() > 0 else 0

    return {
        'Total_Return': total_return,
        'Sharpe_Ratio': sharpe,
        'Max_Drawdown': max_dd,
        'Win_Rate': win_rate,
        'Avg_Trade': net_pnl[net_pnl != 0].mean(),
        'num_trades': (position_changes > 0).sum(),
    }


if __name__ == '__main__':
    # Example usage
    print("Regime Detection Module - Import and use with your data")
    print("\nExample 1: HMM Regime Detection")
    print("  hmm = HiddenMarkovRegimes(returns, n_states=2)")
    print("  hmm.fit_gaussian_hmm()")
    print("  states = hmm.predict_states()")
    print("\nExample 2: Change Point Detection")
    print("  cpd = ChangePointDetection(data)")
    print("  pelt = cpd.pelt_algorithm(penalty='BIC')")
    print("  cusum = cpd.cusum_algorithm(threshold=5.0)")
    print("\nExample 3: Volatility Regimes")
    print("  vol_reg = VolatilityRegimes(returns)")
    print("  vol_reg.classify_regimes_hmm(n_states=3)")
    print("\nExample 4: Regime-Conditional Strategy")
    print("  strategy = RegimeConditionalStrategies(returns, regimes)")
    print("  signals = strategy.momentum_strategy_by_regime()")
