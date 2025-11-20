"""
Factor Models Implementation
Includes Fama-French 3/5 factor models, momentum, quality, and value factors.
Implements factor construction, exposure calculation, regression analysis, and alpha/beta estimation.
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class FactorModel:
    """Base class for factor model analysis."""

    def __init__(self, returns_df, factors_df, risk_free_rate=0.0):
        """
        Initialize factor model.

        Parameters
        ----------
        returns_df : pd.DataFrame
            Portfolio or security returns (T x N)
        factors_df : pd.DataFrame
            Factor returns (T x K)
        risk_free_rate : float or pd.Series
            Risk-free rate
        """
        self.returns = returns_df
        self.factors = factors_df
        self.risk_free_rate = risk_free_rate
        self.excess_returns = returns_df - risk_free_rate
        self.excess_factors = factors_df - risk_free_rate

    def factor_regression(self, asset_index=None):
        """
        Perform Fama-French factor regression.

        Parameters
        ----------
        asset_index : int or str, optional
            Index of specific asset

        Returns
        -------
        dict
            Regression results including alpha, betas, residuals
        """
        if asset_index is not None:
            y = self.excess_returns.iloc[:, asset_index].values
        else:
            y = self.excess_returns.values

        X = np.column_stack([np.ones(len(self.excess_factors)),
                            self.excess_factors.values])

        # OLS regression
        beta = np.linalg.lstsq(X, y, rcond=None)[0]

        if asset_index is not None:
            residuals = y - X @ beta
            fitted = X @ beta
        else:
            residuals = y - X @ beta
            fitted = X @ beta

        # Calculate statistics
        rss = np.sum(residuals**2, axis=0)
        tss = np.sum((y - np.mean(y, axis=0))**2, axis=0)
        r_squared = 1 - rss / tss

        n = X.shape[0]
        k = X.shape[1]
        dof = n - k

        # Standard errors
        mse = rss / dof
        if asset_index is not None:
            var_beta = mse * np.linalg.inv(X.T @ X)
            se_beta = np.sqrt(np.diag(var_beta))
            t_stats = beta / se_beta
            p_values = 2 * (1 - stats.t.cdf(np.abs(t_stats), dof))
        else:
            var_beta = np.zeros((k, k))
            se_beta = np.zeros(k)
            t_stats = np.zeros(k)
            p_values = np.zeros(k)

        return {
            'alpha': beta[0],
            'betas': beta[1:],
            'residuals': residuals,
            'fitted': fitted,
            'r_squared': r_squared,
            'adj_r_squared': 1 - (1 - r_squared) * (n - 1) / dof,
            'se_beta': se_beta,
            't_stats': t_stats,
            'p_values': p_values,
            'mse': mse
        }

    def calculate_exposure(self):
        """
        Calculate factor exposures (betas) for all assets.

        Returns
        -------
        pd.DataFrame
            Factor exposures (N x K)
        """
        X = np.column_stack([np.ones(len(self.excess_factors)),
                            self.excess_factors.values])
        y = self.excess_returns.values

        beta = np.linalg.lstsq(X, y, rcond=None)[0]

        betas_df = pd.DataFrame(
            beta[1:].T,
            columns=self.factors.columns,
            index=self.returns.columns
        )
        return betas_df

    def calculate_alpha(self):
        """
        Calculate alpha for all assets.

        Returns
        -------
        pd.Series
            Alphas (annualized) for each asset
        """
        X = np.column_stack([np.ones(len(self.excess_factors)),
                            self.excess_factors.values])
        y = self.excess_returns.values

        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        alphas = beta[0] * 252  # Annualize

        return pd.Series(alphas, index=self.returns.columns)

    def residual_analysis(self, asset_index=None):
        """
        Analyze regression residuals.

        Parameters
        ----------
        asset_index : int or str, optional
            Specific asset index

        Returns
        -------
        dict
            Residual statistics
        """
        result = self.factor_regression(asset_index)
        residuals = result['residuals']

        if asset_index is not None:
            residuals_mean = np.mean(residuals)
            residuals_std = np.std(residuals)
            skewness = stats.skew(residuals)
            kurtosis = stats.kurtosis(residuals)

            # Jarque-Bera test
            jb_stat = len(residuals) / 6 * (skewness**2 + (kurtosis**2 / 4))
            jb_pvalue = 1 - stats.chi2.cdf(jb_stat, 2)

            # Autocorrelation
            acf = np.corrcoef(residuals[:-1], residuals[1:])[0, 1]
        else:
            residuals_mean = np.mean(residuals, axis=0)
            residuals_std = np.std(residuals, axis=0)
            skewness = stats.skew(residuals, axis=0)
            kurtosis = stats.kurtosis(residuals, axis=0)
            jb_stat = np.nan
            jb_pvalue = np.nan
            acf = np.nan

        return {
            'mean': residuals_mean,
            'std': residuals_std,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'jb_stat': jb_stat,
            'jb_pvalue': jb_pvalue,
            'autocorrelation': acf
        }


class FactorConstruction:
    """Construct Fama-French and momentum factors from security data."""

    @staticmethod
    def construct_smb(market_cap, returns, lower_percentile=30, upper_percentile=70):
        """
        Construct SMB (Small Minus Big) size factor.

        Parameters
        ----------
        market_cap : pd.DataFrame
            Market capitalization by date and security
        returns : pd.DataFrame
            Returns by date and security
        lower_percentile : float
            Percentile for small cap cutoff
        upper_percentile : float
            Percentile for large cap cutoff

        Returns
        -------
        pd.Series
            SMB factor returns
        """
        smb_returns = []

        for date in market_cap.index:
            cap = market_cap.loc[date]
            ret = returns.loc[date]

            if cap.isna().all() or ret.isna().all():
                continue

            cutoff_small = np.nanpercentile(cap, lower_percentile)
            cutoff_big = np.nanpercentile(cap, upper_percentile)

            small = (cap <= cutoff_small) & (~ret.isna())
            big = (cap >= cutoff_big) & (~ret.isna())

            if small.sum() > 0 and big.sum() > 0:
                smb = ret[small].mean() - ret[big].mean()
                smb_returns.append(smb)
            else:
                smb_returns.append(np.nan)

        return pd.Series(smb_returns, index=market_cap.index)

    @staticmethod
    def construct_hml(book_to_market, returns, lower_percentile=30, upper_percentile=70):
        """
        Construct HML (High Minus Low) value factor.

        Parameters
        ----------
        book_to_market : pd.DataFrame
            Book-to-market ratios
        returns : pd.DataFrame
            Security returns
        lower_percentile : float
            Percentile for low value cutoff
        upper_percentile : float
            Percentile for high value cutoff

        Returns
        -------
        pd.Series
            HML factor returns
        """
        hml_returns = []

        for date in book_to_market.index:
            btm = book_to_market.loc[date]
            ret = returns.loc[date]

            if btm.isna().all() or ret.isna().all():
                continue

            cutoff_low = np.nanpercentile(btm, lower_percentile)
            cutoff_high = np.nanpercentile(btm, upper_percentile)

            high = (btm >= cutoff_high) & (~ret.isna())
            low = (btm <= cutoff_low) & (~ret.isna())

            if high.sum() > 0 and low.sum() > 0:
                hml = ret[high].mean() - ret[low].mean()
                hml_returns.append(hml)
            else:
                hml_returns.append(np.nan)

        return pd.Series(hml_returns, index=book_to_market.index)

    @staticmethod
    def construct_rmw(profitability, returns, lower_percentile=30, upper_percentile=70):
        """
        Construct RMW (Robust Minus Weak) quality/profitability factor.

        Parameters
        ----------
        profitability : pd.DataFrame
            Profitability metrics (e.g., ROE, operating profitability)
        returns : pd.DataFrame
            Security returns
        lower_percentile : float
            Percentile for weak profitability cutoff
        upper_percentile : float
            Percentile for robust profitability cutoff

        Returns
        -------
        pd.Series
            RMW factor returns
        """
        rmw_returns = []

        for date in profitability.index:
            prof = profitability.loc[date]
            ret = returns.loc[date]

            if prof.isna().all() or ret.isna().all():
                continue

            cutoff_weak = np.nanpercentile(prof, lower_percentile)
            cutoff_robust = np.nanpercentile(prof, upper_percentile)

            robust = (prof >= cutoff_robust) & (~ret.isna())
            weak = (prof <= cutoff_weak) & (~ret.isna())

            if robust.sum() > 0 and weak.sum() > 0:
                rmw = ret[robust].mean() - ret[weak].mean()
                rmw_returns.append(rmw)
            else:
                rmw_returns.append(np.nan)

        return pd.Series(rmw_returns, index=profitability.index)

    @staticmethod
    def construct_cma(investment, returns, lower_percentile=30, upper_percentile=70):
        """
        Construct CMA (Conservative Minus Aggressive) investment factor.

        Parameters
        ----------
        investment : pd.DataFrame
            Investment ratios (asset growth, capex/assets, etc.)
        returns : pd.DataFrame
            Security returns
        lower_percentile : float
            Percentile for aggressive investment cutoff
        upper_percentile : float
            Percentile for conservative investment cutoff

        Returns
        -------
        pd.Series
            CMA factor returns
        """
        cma_returns = []

        for date in investment.index:
            inv = investment.loc[date]
            ret = returns.loc[date]

            if inv.isna().all() or ret.isna().all():
                continue

            cutoff_aggressive = np.nanpercentile(inv, upper_percentile)
            cutoff_conservative = np.nanpercentile(inv, lower_percentile)

            conservative = (inv <= cutoff_conservative) & (~ret.isna())
            aggressive = (inv >= cutoff_aggressive) & (~ret.isna())

            if conservative.sum() > 0 and aggressive.sum() > 0:
                cma = ret[conservative].mean() - ret[aggressive].mean()
                cma_returns.append(cma)
            else:
                cma_returns.append(np.nan)

        return pd.Series(cma_returns, index=investment.index)

    @staticmethod
    def construct_momentum(returns, lookback=252, skip=21):
        """
        Construct MOM (Momentum) factor.

        Parameters
        ----------
        returns : pd.DataFrame
            Security returns
        lookback : int
            Lookback period for momentum calculation
        skip : int
            Period to skip (avoid microstructure effects)

        Returns
        -------
        pd.Series
            Momentum factor returns
        """
        mom_returns = []

        # Calculate momentum scores
        momentum_scores = returns.rolling(window=lookback).apply(
            lambda x: (1 + x).prod() - 1, raw=False
        ).shift(skip)

        for date in returns.index[lookback + skip:]:
            mom_score = momentum_scores.loc[date]
            ret = returns.loc[date]

            if mom_score.isna().all() or ret.isna().all():
                continue

            # Top 30% momentum vs bottom 30%
            top_mom = mom_score >= mom_score.quantile(0.70)
            bottom_mom = mom_score <= mom_score.quantile(0.30)

            if top_mom.sum() > 0 and bottom_mom.sum() > 0:
                mom = ret[top_mom].mean() - ret[bottom_mom].mean()
                mom_returns.append(mom)
            else:
                mom_returns.append(np.nan)

        return pd.Series(mom_returns, index=returns.index[lookback + skip:])


class FactorPortfolioConstruction:
    """Construct factor-mimicking portfolios."""

    @staticmethod
    def construct_long_short_portfolio(returns, factor_scores, long_pct=0.3, short_pct=0.3):
        """
        Construct long-short portfolio based on factor scores.

        Parameters
        ----------
        returns : pd.DataFrame
            Security returns
        factor_scores : pd.Series
            Factor exposure scores
        long_pct : float
            Percentage for long positions
        short_pct : float
            Percentage for short positions

        Returns
        -------
        pd.Series
            Portfolio returns
        """
        portfolio_returns = []

        for date in returns.index:
            scores = factor_scores.loc[date] if date in factor_scores.index else pd.Series()
            ret = returns.loc[date]

            if scores.empty or ret.isna().all():
                continue

            n_long = max(1, int(len(scores) * long_pct))
            n_short = max(1, int(len(scores) * short_pct))

            long_assets = scores.nlargest(n_long).index
            short_assets = scores.nsmallest(n_short).index

            long_ret = ret[long_assets].mean()
            short_ret = ret[short_assets].mean()

            portfolio_ret = long_ret - short_ret
            portfolio_returns.append(portfolio_ret)

        return pd.Series(portfolio_returns, index=returns.index[:len(portfolio_returns)])

    @staticmethod
    def construct_weighted_portfolio(returns, factor_exposures):
        """
        Construct portfolio with weights based on factor exposures.

        Parameters
        ----------
        returns : pd.DataFrame
            Security returns
        factor_exposures : pd.DataFrame
            Factor loadings/exposures

        Returns
        -------
        pd.Series
            Portfolio returns
        """
        # Normalize exposures to sum to 1
        weights = factor_exposures.div(factor_exposures.sum(axis=1), axis=0)

        # Calculate weighted returns
        portfolio_returns = (returns * weights).sum(axis=1)

        return portfolio_returns


class FactorAnalysis:
    """Statistical analysis of factor models and portfolios."""

    @staticmethod
    def calculate_performance_metrics(returns, excess=False):
        """
        Calculate comprehensive performance metrics.

        Parameters
        ----------
        returns : pd.Series
            Portfolio returns
        excess : bool
            Whether returns are excess returns

        Returns
        -------
        dict
            Performance metrics
        """
        ret_array = returns.dropna().values

        if len(ret_array) == 0:
            return {}

        total_return = (1 + ret_array).prod() - 1
        annual_return = (1 + total_return) ** (252 / len(ret_array)) - 1
        annual_vol = np.std(ret_array) * np.sqrt(252)
        sharpe = annual_return / annual_vol if annual_vol > 0 else 0

        cum_returns = (1 + ret_array).cumprod()
        running_max = np.maximum.accumulate(cum_returns)
        drawdown = cum_returns / running_max - 1
        max_drawdown = drawdown.min()

        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'skewness': stats.skew(ret_array),
            'kurtosis': stats.kurtosis(ret_array),
            'calmar_ratio': annual_return / abs(max_drawdown) if max_drawdown < 0 else 0
        }

    @staticmethod
    def factor_correlation_matrix(factors_df):
        """
        Calculate factor correlation matrix.

        Parameters
        ----------
        factors_df : pd.DataFrame
            Factor returns

        Returns
        -------
        pd.DataFrame
            Correlation matrix
        """
        return factors_df.corr()

    @staticmethod
    def factor_contribution_analysis(returns, factor_returns, betas):
        """
        Analyze contribution of each factor to returns.

        Parameters
        ----------
        returns : pd.Series
            Portfolio returns
        factor_returns : pd.DataFrame
            Factor returns
        betas : pd.Series
            Factor betas

        Returns
        -------
        pd.DataFrame
            Factor contribution analysis
        """
        factor_contributions = pd.DataFrame()

        for factor in betas.index:
            factor_contributions[factor] = betas[factor] * factor_returns[factor]

        return factor_contributions

    @staticmethod
    def style_factor_analysis(betas):
        """
        Analyze style factor exposures.

        Parameters
        ----------
        betas : pd.Series or pd.DataFrame
            Factor loadings

        Returns
        -------
        dict
            Style analysis results
        """
        if isinstance(betas, pd.Series):
            betas = betas.to_frame().T

        return {
            'mean_betas': betas.mean(),
            'std_betas': betas.std(),
            'min_betas': betas.min(),
            'max_betas': betas.max(),
            'exposure_concentration': (betas ** 2).sum(axis=1)
        }


# Example usage and demonstration
if __name__ == "__main__":
    print("Factor Models Implementation")
    print("=" * 60)

    # Create sample data
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    n_assets = 10

    # Generate sample returns
    returns = pd.DataFrame(
        np.random.randn(252, n_assets) * 0.02,
        index=dates,
        columns=[f'Asset_{i}' for i in range(n_assets)]
    )

    # Generate sample factors
    factors = pd.DataFrame({
        'MKT': np.random.randn(252) * 0.02,
        'SMB': np.random.randn(252) * 0.015,
        'HML': np.random.randn(252) * 0.015,
        'MOM': np.random.randn(252) * 0.01
    }, index=dates)

    # Create factor model
    fm = FactorModel(returns, factors)

    # Perform analysis
    print("\nFactor Regression Analysis")
    print("-" * 60)
    result = fm.factor_regression(asset_index=0)
    print(f"Alpha: {result['alpha']:.6f}")
    print(f"Betas: {result['betas']}")
    print(f"R-squared: {result['r_squared']:.4f}")

    # Factor exposures
    print("\nFactor Exposures (Betas)")
    print("-" * 60)
    exposures = fm.calculate_exposure()
    print(exposures.head())

    # Performance metrics
    print("\nPerformance Metrics")
    print("-" * 60)
    portfolio_returns = returns.mean(axis=1)
    metrics = FactorAnalysis.calculate_performance_metrics(portfolio_returns)
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}")

    # Factor correlation
    print("\nFactor Correlation Matrix")
    print("-" * 60)
    corr_matrix = FactorAnalysis.factor_correlation_matrix(factors)
    print(corr_matrix)

    print("\n" + "=" * 60)
    print("Implementation complete - ready for production use")
