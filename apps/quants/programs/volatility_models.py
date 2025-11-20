"""
Volatility Modeling Implementation
Includes GARCH, EGARCH, realized volatility, and VIX-based strategies
Using arch library for robust volatility estimation
"""

import numpy as np
import pandas as pd
from arch import arch_model
from arch.univariate import (
    GARCH, EGARCH, ARCH, ConstantMean, ZeroMean,
    Normal, StudentT, SkewStudent
)
import warnings
warnings.filterwarnings('ignore')


class VolatilityModels:
    """
    Comprehensive volatility modeling class supporting multiple GARCH variants
    """

    def __init__(self, returns_data):
        """
        Initialize with returns data

        Parameters:
        -----------
        returns_data : pd.Series or np.array
            Log returns or simple returns (in decimal form, e.g., 0.01 for 1%)
        """
        if isinstance(returns_data, pd.Series):
            self.returns = returns_data
        else:
            self.returns = pd.Series(returns_data)

        # Convert to percentage returns for arch library (convention: multiply by 100)
        self.returns_pct = self.returns * 100

    # ==================== GARCH(1,1) Models ====================

    def fit_garch11_normal(self, disp='off'):
        """
        Fit standard GARCH(1,1) model with normal distribution

        GARCH(1,1) variance equation:
        σ_t^2 = ω + α*ε_{t-1}^2 + β*σ_{t-1}^2

        where:
        - ω: constant term (long-run variance component)
        - α: ARCH effect (reaction to shocks)
        - β: GARCH effect (persistence)
        """
        model = arch_model(self.returns_pct, vol='Garch', p=1, q=1, mean='Zero')
        results = model.fit(disp=disp)
        return results

    def fit_garch11_studentt(self, disp='off'):
        """
        Fit GARCH(1,1) with Student's t distribution
        Better captures tail risk and kurtosis
        """
        model = arch_model(self.returns_pct, vol='Garch', p=1, q=1,
                          mean='Zero', rescale=False)
        model.distribution = StudentT()
        results = model.fit(disp=disp)
        return results

    def fit_garch21(self, disp='off'):
        """
        Fit GARCH(2,1) model for more complex volatility dynamics
        """
        model = arch_model(self.returns_pct, vol='Garch', p=2, q=1, mean='Zero')
        results = model.fit(disp=disp)
        return results

    # ==================== EGARCH Models ====================

    def fit_egarch(self, disp='off'):
        """
        Fit Exponential GARCH (EGARCH) model

        Log-variance equation:
        log(σ_t^2) = ω + β*log(σ_{t-1}^2) + γ*[|Z_t| - E(|Z_t|)] + λ*Z_t

        Advantages:
        - Captures leverage effects (negative shocks have larger impact than positive)
        - No positivity constraints needed
        - More flexible for asymmetric volatility
        """
        model = arch_model(self.returns_pct, vol='EGARCH', p=1, q=1, mean='Zero')
        results = model.fit(disp=disp)
        return results

    def fit_gjr_garch(self, disp='off'):
        """
        Fit GJR-GARCH(1,1,1) model - Asymmetric GARCH

        Variance equation:
        σ_t^2 = ω + (α + γ*I_{t-1})*ε_{t-1}^2 + β*σ_{t-1}^2

        where I_{t-1} = 1 if ε_{t-1} < 0 (bad news), 0 otherwise
        γ: asymmetry parameter (leverage effect)
        """
        model = arch_model(self.returns_pct, vol='GARCH', p=1, q=1,
                          mean='Zero', rescale=False)
        model.volatility = GARCH(p=1, q=1, o=1)
        results = model.fit(disp=disp)
        return results

    # ==================== Realized Volatility ====================

    def realized_volatility_simple(self, window=20):
        """
        Calculate simple realized volatility as rolling standard deviation

        RV_t = sqrt(sum of squared returns over window)

        Parameters:
        -----------
        window : int
            Rolling window size (default: 20 trading days ≈ 1 month)
        """
        rv = self.returns.rolling(window=window).std() * np.sqrt(252)
        return rv

    def realized_volatility_parkinson(self, high_low_data, window=20):
        """
        Parkinson (1980) volatility estimator using intraday high-low prices
        More efficient than close-to-close volatility

        RV_Parkinson = sqrt(1/(4*ln(2)) * ln(H/L)^2)

        Parameters:
        -----------
        high_low_data : pd.DataFrame
            DataFrame with 'High' and 'Low' columns
        window : int
            Averaging window
        """
        high_low_ratio = np.log(high_low_data['High'] / high_low_data['Low'])
        rv_parkinson = np.sqrt(high_low_ratio**2 / (4 * np.log(2)))
        return rv_parkinson.rolling(window=window).mean() * np.sqrt(252)

    def realized_volatility_garman_klass(self, ohlc_data, window=20):
        """
        Garman-Klass (1980) volatility estimator
        Uses open, high, low, close prices
        More efficient than Parkinson alone

        RV_GK = sqrt(0.5*ln(H/L)^2 - (2*ln(2)-1)*ln(C/O)^2)

        Parameters:
        -----------
        ohlc_data : pd.DataFrame
            DataFrame with 'Open', 'High', 'Low', 'Close' columns
        window : int
            Averaging window
        """
        hl = np.log(ohlc_data['High'] / ohlc_data['Low'])
        co = np.log(ohlc_data['Close'] / ohlc_data['Open'])

        rv_gk = np.sqrt(0.5 * hl**2 - (2*np.log(2) - 1) * co**2)
        return rv_gk.rolling(window=window).mean() * np.sqrt(252)

    def realized_volatility_rogers_satchell(self, ohlc_data, window=20):
        """
        Rogers-Satchell (1991) volatility estimator
        Unaffected by opening jumps and gaps

        Parameters:
        -----------
        ohlc_data : pd.DataFrame
            DataFrame with 'Open', 'High', 'Low', 'Close' columns
        window : int
            Averaging window
        """
        ho = np.log(ohlc_data['High'] / ohlc_data['Open'])
        lc = np.log(ohlc_data['Low'] / ohlc_data['Close'])

        rv_rs = np.sqrt(ho * lc + ho**2 + lc**2)
        return rv_rs.rolling(window=window).mean() * np.sqrt(252)

    def realized_volatility_range_based(self, high, low, close, window=20):
        """
        Simple range-based volatility: high-low range as volatility proxy
        """
        range_vol = (np.log(high) - np.log(low)) / (2 * np.sqrt(np.log(4)))
        return range_vol.rolling(window=window).mean() * np.sqrt(252)

    # ==================== Volatility Forecasting ====================

    def forecast_volatility(self, garch_results, horizon=1):
        """
        Forecast volatility using fitted GARCH model

        Parameters:
        -----------
        garch_results : arch results object
            Fitted GARCH model
        horizon : int
            Forecast horizon (1-step, multi-step)
        """
        forecast = garch_results.get_forecast(horizon=horizon)
        return forecast.variance.values / 10000  # Convert back to decimal

    def forecast_volatility_parametric(self, garch_results, horizon=5):
        """
        Multi-step ahead parametric volatility forecast
        """
        forecast = garch_results.get_forecast(horizon=horizon)
        variance_forecast = forecast.variance
        volatility_forecast = np.sqrt(variance_forecast) / 100  # Convert to decimal
        return volatility_forecast

    def conditional_volatility(self, garch_results):
        """
        Extract conditional volatility (σ_t) from fitted model
        Time series of model-implied volatilities
        """
        return garch_results.conditional_volatility / 100  # Convert to decimal

    # ==================== VIX-Based Strategies ====================

    def calculate_vol_term_structure(self, realized_vol_series, forward_returns):
        """
        Calculate implied volatility term structure
        Relationship between near-term and forward volatility

        Parameters:
        -----------
        realized_vol_series : pd.Series
            Time series of realized volatilities
        forward_returns : pd.Series
            Forward returns for different maturities
        """
        # Annualized volatility across different horizons
        term_structure = {
            '1M': np.std(forward_returns.iloc[:21]) * np.sqrt(252),
            '3M': np.std(forward_returns.iloc[:63]) * np.sqrt(252),
            '6M': np.std(forward_returns.iloc[:126]) * np.sqrt(252),
            '1Y': np.std(forward_returns.iloc[:252]) * np.sqrt(252),
        }
        return term_structure

    def vix_simulation(self, garch_results, num_simulations=10000, horizon=1):
        """
        Simulate VIX-like metric using GARCH model
        Monte Carlo simulation of future volatility

        Parameters:
        -----------
        garch_results : arch results object
            Fitted GARCH model
        num_simulations : int
            Number of Monte Carlo paths
        horizon : int
            Forecast horizon
        """
        # Get current conditional volatility
        current_vol = garch_results.conditional_volatility.iloc[-1] / 100

        # Bootstrap samples from residuals for Monte Carlo
        residuals = garch_results.resid / 100

        # Simple simulation: assume conditional volatility evolves as mean-reverting
        vix_sim = np.zeros((num_simulations, horizon))
        vix_sim[:, 0] = current_vol

        # Mean reversion to long-run volatility
        long_run_vol = garch_results.conditional_volatility.mean() / 100
        mean_reversion_speed = 0.1

        for t in range(1, horizon):
            shocks = np.random.standard_normal(num_simulations)
            vix_sim[:, t] = (vix_sim[:, t-1] +
                           mean_reversion_speed * (long_run_vol - vix_sim[:, t-1]) +
                           0.05 * vix_sim[:, t-1] * shocks)

        return vix_sim

    def vol_mean_reversion_strategy(self, realized_vol, implied_vol,
                                     long_threshold=0.25, short_threshold=0.75):
        """
        Mean reversion strategy based on realized vs implied volatility

        Strategy:
        - If RV < percentile(ImpVol, 25%): Market is expensive, sell volatility
        - If RV > percentile(ImpVol, 75%): Market is cheap, buy volatility

        Parameters:
        -----------
        realized_vol : pd.Series
            Realized volatility time series
        implied_vol : pd.Series
            Implied volatility time series (e.g., VIX)
        long_threshold : float
            Percentile threshold for long positions
        short_threshold : float
            Percentile threshold for short positions
        """
        # Normalize volumes
        rv_norm = realized_vol / realized_vol.rolling(60).mean()
        iv_norm = implied_vol / implied_vol.rolling(60).mean()

        # Calculate strategy signals
        signals = pd.DataFrame(index=realized_vol.index)
        signals['RV'] = rv_norm
        signals['IV'] = iv_norm
        signals['Vol_Ratio'] = rv_norm / (iv_norm + 1e-6)

        # Generate signals
        signals['Signal'] = 0  # Neutral
        signals.loc[signals['Vol_Ratio'] < long_threshold, 'Signal'] = 1   # Long vol
        signals.loc[signals['Vol_Ratio'] > short_threshold, 'Signal'] = -1  # Short vol

        return signals

    def vol_clustering_strategy(self, garch_results, threshold_percentile=75):
        """
        Strategy exploiting volatility clustering
        High volatility today predicts high volatility tomorrow

        Buy volatility when conditional volatility exceeds threshold
        """
        cond_vol = garch_results.conditional_volatility / 100
        threshold = cond_vol.quantile(threshold_percentile / 100)

        signals = pd.DataFrame(index=cond_vol.index)
        signals['Cond_Vol'] = cond_vol
        signals['Threshold'] = threshold
        signals['Signal'] = np.where(cond_vol > threshold, 1, 0)

        return signals

    def vol_surface_arbitrage(self, volatilities_dict):
        """
        Identify arbitrage opportunities in volatility surface

        Parameters:
        -----------
        volatilities_dict : dict
            Dictionary with keys like '1M', '3M', '6M', '1Y'
            representing different maturities
        """
        sorted_vols = sorted(volatilities_dict.items(),
                            key=lambda x: int(x[0].replace('M', '').replace('Y', '')))

        vol_moves = []
        for i in range(len(sorted_vols) - 1):
            move = sorted_vols[i+1][1] - sorted_vols[i][1]
            vol_moves.append(move)

        return vol_moves

    # ==================== Model Diagnostics ====================

    def model_diagnostics(self, garch_results):
        """
        Print comprehensive model diagnostics
        """
        print("\n" + "="*80)
        print("GARCH MODEL DIAGNOSTICS")
        print("="*80)
        print(garch_results.summary())

        # Check persistence
        params = garch_results.params
        if 'beta[1]' in params.index and 'alpha[1]' in params.index:
            persistence = params['alpha[1]'] + params['beta[1]']
            print(f"\nVolatility Persistence (α + β): {persistence:.4f}")
            if persistence < 1:
                print("✓ Model is mean-reverting (stable)")
            else:
                print("✗ Model is explosive or unit root")

    def residuals_analysis(self, garch_results):
        """
        Analyze standardized residuals for model fit
        """
        std_resid = garch_results.std_resid

        diagnostics = {
            'Mean': std_resid.mean(),
            'Std Dev': std_resid.std(),
            'Skewness': std_resid.skew(),
            'Kurtosis': std_resid.kurtosis(),
            'Jarque-Bera': self._jarque_bera(std_resid),
        }

        return diagnostics

    @staticmethod
    def _jarque_bera(residuals):
        """Calculate Jarque-Bera test statistic"""
        n = len(residuals)
        skew = residuals.skew()
        kurt = residuals.kurtosis()
        jb = n/6 * (skew**2 + (kurt**2)/4)
        return jb


# ==================== Utility Functions ====================

def compare_garch_variants(returns_pct):
    """
    Compare multiple GARCH variants on same data
    """
    results = {}

    # GARCH(1,1) Normal
    garch_normal = arch_model(returns_pct, vol='Garch', p=1, q=1, mean='Zero')
    results['GARCH(1,1) Normal'] = garch_normal.fit(disp='off')

    # GARCH(1,1) Student's t
    garch_t = arch_model(returns_pct, vol='Garch', p=1, q=1, mean='Zero')
    garch_t.distribution = StudentT()
    results['GARCH(1,1) StudentT'] = garch_t.fit(disp='off')

    # EGARCH
    egarch = arch_model(returns_pct, vol='EGARCH', p=1, q=1, mean='Zero')
    results['EGARCH(1,1)'] = egarch.fit(disp='off')

    # GJR-GARCH
    gjr = arch_model(returns_pct, vol='GARCH', p=1, q=1, mean='Zero')
    gjr.volatility = GARCH(p=1, q=1, o=1)
    results['GJR-GARCH(1,1,1)'] = gjr.fit(disp='off')

    # Compare using information criteria
    comparison = pd.DataFrame({
        'Model': results.keys(),
        'AIC': [r.aic for r in results.values()],
        'BIC': [r.bic for r in results.values()],
    })

    return results, comparison


if __name__ == '__main__':
    # Example usage
    print("Volatility Models Module - Import and use with your data")
    print("Example: vol_model = VolatilityModels(returns_data)")
    print("         garch_fit = vol_model.fit_garch11_normal()")
    print("         forecast = vol_model.forecast_volatility(garch_fit, horizon=5)")
