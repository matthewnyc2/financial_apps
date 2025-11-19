"""
Stock Filtering Pipeline
========================

Complete implementation of 5-stage progressive filtering framework
From 1000+ stocks to top 10-20 candidates

Based on research in STOCK_FILTERING_RESEARCH.md

Author: Research Team
Date: 2025-11-19
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Scikit-learn imports
from sklearn.covariance import MinCovDet, LedoitWolf
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Scipy imports
from scipy.stats import chi2
from scipy.stats.mstats import winsorize
from scipy.optimize import minimize


class StockFilteringPipeline:
    """
    Five-stage progressive filtering pipeline for stock selection

    Pipeline stages:
    1. Exclusion filters (3000 → 1500)
    2. Outlier detection (1500 → 1000)
    3. Clustering & factor scoring (1000 → 200)
    4. PCA & advanced ranking (200 → 50)
    5. Portfolio optimization (50 → 10-20)
    """

    def __init__(self, config: Optional[Dict] = None, verbose: bool = True):
        """
        Initialize pipeline with configuration

        Parameters:
        -----------
        config : dict, optional
            Configuration parameters for each stage
        verbose : bool
            Print progress messages
        """
        self.config = config or self.default_config()
        self.verbose = verbose
        self.stage_results = {}

    @staticmethod
    def default_config() -> Dict:
        """Default configuration for all pipeline stages"""
        return {
            'stage1': {
                'min_market_cap': 500e6,
                'min_avg_volume': 1e6,
                'min_price': 5.0,
                'min_history_days': 252
            },
            'stage2': {
                'contamination': 0.33,
                'winsorize_limits': (0.05, 0.05),
                'chi2_percentile': 0.975
            },
            'stage3': {
                'n_clusters': 10,
                'top_pct_per_cluster': 0.20,
                'factor_weights': {
                    'value': 0.30,
                    'momentum': 0.30,
                    'quality': 0.20,
                    'low_vol': 0.20
                }
            },
            'stage4': {
                'n_pca_components': 10,
                'top_n': 50
            },
            'stage5': {
                'optimization_method': 'max_sharpe',
                'target_n': 10,
                'max_weight': 0.20,
                'kelly_fraction': 0.25,
                'risk_free_rate': 0.02
            }
        }

    def run_pipeline(self,
                    df: pd.DataFrame,
                    returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute complete filtering pipeline

        Parameters:
        -----------
        df : DataFrame
            Stock universe with features
        returns_df : DataFrame
            Historical returns (rows=dates, cols=tickers)

        Returns:
        --------
        final_selection : DataFrame
            Top stocks with weights and scores
        """
        if self.verbose:
            print(f"{'='*60}")
            print(f"Stock Filtering Pipeline")
            print(f"{'='*60}")
            print(f"Starting with {len(df)} stocks\n")

        # Stage 1: Exclusion filters
        df_s1 = self.stage1_exclusion(df)
        self.stage_results['stage1'] = df_s1
        if self.verbose:
            print(f"Stage 1 (Exclusion Filters): {len(df_s1)} stocks remaining")

        # Stage 2: Outlier detection
        df_s2 = self.stage2_outlier_detection(df_s1)
        self.stage_results['stage2'] = df_s2
        if self.verbose:
            print(f"Stage 2 (Outlier Detection): {len(df_s2)} stocks remaining")

        # Stage 3: Clustering and factor scoring
        df_s3 = self.stage3_clustering(df_s2)
        self.stage_results['stage3'] = df_s3
        if self.verbose:
            print(f"Stage 3 (Clustering & Scoring): {len(df_s3)} stocks remaining")

        # Stage 4: PCA and ranking
        df_s4 = self.stage4_pca_ranking(df_s3)
        self.stage_results['stage4'] = df_s4
        if self.verbose:
            print(f"Stage 4 (PCA & Ranking): {len(df_s4)} stocks remaining")

        # Stage 5: Portfolio optimization
        df_s5 = self.stage5_optimization(df_s4, returns_df)
        self.stage_results['stage5'] = df_s5
        if self.verbose:
            print(f"Stage 5 (Portfolio Optimization): {len(df_s5)} stocks selected")
            print(f"\n{'='*60}")
            print(f"Pipeline Complete!")
            print(f"{'='*60}\n")

        return df_s5

    # ========================
    # Stage 1: Exclusion Filters
    # ========================

    def stage1_exclusion(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage 1: Basic exclusion filters

        Filters applied:
        - Market cap threshold
        - Average volume threshold
        - Price threshold
        - Data quality requirements
        """
        cfg = self.config['stage1']

        mask = (
            (df['market_cap'] >= cfg['min_market_cap']) &
            (df['avg_daily_volume'] >= cfg['min_avg_volume']) &
            (df['price'] >= cfg['min_price']) &
            (df['history_days'] >= cfg['min_history_days'])
        )

        # Optional: add data completeness check
        if 'data_complete' in df.columns:
            mask &= df['data_complete']

        return df[mask].copy()

    # ========================
    # Stage 2: Outlier Detection
    # ========================

    def stage2_outlier_detection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage 2: Robust multivariate outlier detection

        Methods:
        - Winsorization at 5th/95th percentiles
        - Robust Mahalanobis distance (MCD)
        """
        cfg = self.config['stage2']

        # Define features for outlier detection
        numeric_features = [
            'return_12m', 'return_6m', 'volatility', 'beta',
            'market_cap', 'book_to_market', 'roe', 'roa',
            'debt_to_equity', 'earnings_yield'
        ]

        # Use only available features
        features = [f for f in numeric_features if f in df.columns]

        # Winsorize features
        df_clean = df.copy()
        for feature in features:
            df_clean[feature] = winsorize(
                df[feature].values,
                limits=cfg['winsorize_limits']
            )

        # Robust Mahalanobis distance outlier detection
        X = df_clean[features].values

        # Handle missing values
        if np.isnan(X).any():
            # Simple median imputation
            from sklearn.impute import SimpleImputer
            imputer = SimpleImputer(strategy='median')
            X = imputer.fit_transform(X)

        # Minimum Covariance Determinant
        mcd = MinCovDet(
            support_fraction=1 - cfg['contamination'],
            random_state=42
        )
        mcd.fit(X)

        # Calculate robust Mahalanobis distances
        mahal_dist = mcd.mahalanobis(X)

        # Chi-square threshold
        threshold = chi2.ppf(cfg['chi2_percentile'], df=len(features))

        # Keep non-outliers
        mask = mahal_dist < threshold

        if self.verbose:
            n_outliers = (~mask).sum()
            print(f"  → Removed {n_outliers} outliers ({n_outliers/len(df)*100:.1f}%)")

        return df_clean[mask].copy()

    # ========================
    # Stage 3: Clustering & Factor Scoring
    # ========================

    def stage3_clustering(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage 3: Factor scoring and clustering

        - Calculate Fama-French style factor scores
        - Cluster stocks by characteristics
        - Select top performers from each cluster
        """
        cfg = self.config['stage3']

        # Calculate factor scores
        df = self._calculate_factor_scores(df)

        # Composite score
        weights = cfg['factor_weights']
        df['composite_score'] = (
            weights['value'] * df['value_score'] +
            weights['momentum'] * df['momentum_score'] +
            weights['quality'] * df['quality_score'] +
            weights['low_vol'] * df['low_vol_score']
        )

        # Clustering features
        cluster_features = [
            'value_score', 'momentum_score', 'quality_score',
            'low_vol_score'
        ]

        # Add additional features if available
        if 'beta' in df.columns:
            cluster_features.append('beta')
        if 'market_cap' in df.columns:
            cluster_features.append('market_cap')

        X = df[cluster_features].values

        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # K-means clustering
        kmeans = KMeans(
            n_clusters=cfg['n_clusters'],
            random_state=42,
            n_init=10
        )
        df['cluster'] = kmeans.fit_predict(X_scaled)

        # Select top stocks from each cluster
        selected_stocks = []
        for cluster_id in range(cfg['n_clusters']):
            cluster_df = df[df['cluster'] == cluster_id]
            n_select = max(1, int(len(cluster_df) * cfg['top_pct_per_cluster']))
            top_stocks = cluster_df.nlargest(n_select, 'composite_score')
            selected_stocks.append(top_stocks)

        result = pd.concat(selected_stocks)

        if self.verbose:
            print(f"  → Formed {cfg['n_clusters']} clusters")
            print(f"  → Selected top {cfg['top_pct_per_cluster']*100:.0f}% from each cluster")

        return result

    def _calculate_factor_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Fama-French style factor scores"""

        # Value factor (higher is better)
        value_components = []
        if 'book_to_market' in df.columns:
            value_components.append(df['book_to_market'].rank(pct=True))
        if 'earnings_yield' in df.columns:
            value_components.append(df['earnings_yield'].rank(pct=True))
        if 'price_to_sales' in df.columns:
            value_components.append(1 - df['price_to_sales'].rank(pct=True))

        if value_components:
            df['value_score'] = np.mean(value_components, axis=0)
        else:
            df['value_score'] = 0.5

        # Momentum factor
        momentum_components = []
        if 'return_12m' in df.columns:
            momentum_components.append(df['return_12m'].rank(pct=True))
        if 'return_6m' in df.columns:
            momentum_components.append(df['return_6m'].rank(pct=True))

        if momentum_components:
            df['momentum_score'] = np.mean(momentum_components, axis=0)
        else:
            df['momentum_score'] = 0.5

        # Quality factor
        quality_components = []
        if 'roe' in df.columns:
            quality_components.append(df['roe'].rank(pct=True))
        if 'roa' in df.columns:
            quality_components.append(df['roa'].rank(pct=True))
        if 'debt_to_equity' in df.columns:
            quality_components.append(1 - df['debt_to_equity'].rank(pct=True))

        if quality_components:
            df['quality_score'] = np.mean(quality_components, axis=0)
        else:
            df['quality_score'] = 0.5

        # Low volatility factor (inverse)
        if 'volatility' in df.columns:
            df['low_vol_score'] = 1 - df['volatility'].rank(pct=True)
        else:
            df['low_vol_score'] = 0.5

        return df

    # ========================
    # Stage 4: PCA & Ranking
    # ========================

    def stage4_pca_ranking(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage 4: PCA dimension reduction and advanced ranking

        - Apply PCA for dimension reduction
        - Calculate percentile ranks
        - Create final composite ranking
        """
        cfg = self.config['stage4']

        # Select numeric features for PCA
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        exclude_cols = ['cluster', 'composite_score']
        features = [c for c in numeric_cols if c not in exclude_cols and not c.endswith('_score')]

        if len(features) > cfg['n_pca_components']:
            X = df[features].values

            # Handle missing values
            if np.isnan(X).any():
                from sklearn.impute import SimpleImputer
                imputer = SimpleImputer(strategy='median')
                X = imputer.fit_transform(X)

            # Standardize
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Apply PCA
            pca = PCA(n_components=cfg['n_pca_components'])
            components = pca.fit_transform(X_scaled)

            # Add principal components to dataframe
            for i in range(cfg['n_pca_components']):
                df[f'PC{i+1}'] = components[:, i]

            if self.verbose:
                var_explained = pca.explained_variance_ratio_.sum()
                print(f"  → PCA: {var_explained*100:.1f}% variance explained by {cfg['n_pca_components']} components")

        # Percentile ranking
        df['value_pctile'] = df['value_score'].rank(pct=True) * 100
        df['momentum_pctile'] = df['momentum_score'].rank(pct=True) * 100
        df['quality_pctile'] = df['quality_score'].rank(pct=True) * 100

        # Final composite rank (weighted percentiles)
        df['final_rank'] = (
            0.35 * df['value_pctile'] +
            0.35 * df['momentum_pctile'] +
            0.30 * df['quality_pctile']
        )

        # Cross-sectional z-score of final rank
        df['final_rank_zscore'] = (
            (df['final_rank'] - df['final_rank'].mean()) / df['final_rank'].std()
        )

        # Select top N stocks
        top_stocks = df.nlargest(cfg['top_n'], 'final_rank')

        return top_stocks

    # ========================
    # Stage 5: Portfolio Optimization
    # ========================

    def stage5_optimization(self,
                           df: pd.DataFrame,
                           returns_df: pd.DataFrame) -> pd.DataFrame:
        """
        Stage 5: Portfolio optimization

        - Ledoit-Wolf covariance estimation
        - Mean-variance optimization
        - Kelly criterion position sizing
        """
        cfg = self.config['stage5']

        # Get tickers
        tickers = df['ticker'].values

        # Filter returns to selected stocks
        available_tickers = [t for t in tickers if t in returns_df.columns]

        if len(available_tickers) == 0:
            raise ValueError("No matching tickers found in returns data")

        returns = returns_df[available_tickers].dropna()

        if len(returns) < 60:
            raise ValueError("Insufficient return history (need at least 60 days)")

        # Expected returns (annualized)
        expected_returns = returns.mean() * 252

        # Robust covariance estimation (Ledoit-Wolf)
        lw = LedoitWolf()
        cov_matrix = lw.fit(returns).covariance_

        if self.verbose:
            print(f"  → Using Ledoit-Wolf shrinkage (intensity: {lw.shrinkage_:.4f})")

        # Portfolio optimization
        if cfg['optimization_method'] == 'max_sharpe':
            weights = self._maximize_sharpe(
                expected_returns.values,
                cov_matrix,
                cfg['risk_free_rate'],
                cfg['max_weight']
            )
        elif cfg['optimization_method'] == 'min_variance':
            weights = self._minimize_variance(
                cov_matrix,
                cfg['max_weight']
            )
        else:
            # Equal weight fallback
            weights = np.ones(len(available_tickers)) / len(available_tickers)

        # Create result dataframe
        result_df = df[df['ticker'].isin(available_tickers)].copy()
        result_df['weight'] = weights

        # Apply Kelly criterion
        result_df = self._apply_kelly_criterion(
            result_df,
            returns,
            cfg['kelly_fraction']
        )

        # Filter to non-zero weights and sort
        result_df = result_df[result_df['adjusted_weight'] > 0.01]
        result_df = result_df.sort_values('adjusted_weight', ascending=False)

        # Limit to target number
        result_df = result_df.head(cfg['target_n'])

        # Renormalize weights
        result_df['final_weight'] = result_df['adjusted_weight'] / result_df['adjusted_weight'].sum()

        return result_df

    def _maximize_sharpe(self,
                        expected_returns: np.ndarray,
                        cov_matrix: np.ndarray,
                        risk_free_rate: float,
                        max_weight: float) -> np.ndarray:
        """Maximum Sharpe ratio portfolio"""
        n_assets = len(expected_returns)

        def neg_sharpe(weights):
            port_return = np.sum(expected_returns * weights)
            port_vol = np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))
            if port_vol == 0:
                return 0
            return -(port_return - risk_free_rate) / port_vol

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]

        bounds = tuple((0, max_weight) for _ in range(n_assets))

        initial_guess = np.ones(n_assets) / n_assets

        result = minimize(
            neg_sharpe,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints,
            options={'ftol': 1e-9, 'maxiter': 1000}
        )

        return result.x

    def _minimize_variance(self,
                          cov_matrix: np.ndarray,
                          max_weight: float) -> np.ndarray:
        """Minimum variance portfolio"""
        n_assets = cov_matrix.shape[0]

        def portfolio_variance(weights):
            return np.dot(weights, np.dot(cov_matrix, weights))

        constraints = [
            {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}
        ]

        bounds = tuple((0, max_weight) for _ in range(n_assets))

        initial_guess = np.ones(n_assets) / n_assets

        result = minimize(
            portfolio_variance,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )

        return result.x

    def _apply_kelly_criterion(self,
                               df: pd.DataFrame,
                               returns: pd.DataFrame,
                               fraction: float) -> pd.DataFrame:
        """
        Apply fractional Kelly criterion for position sizing

        Recommended: 0.25x Kelly for practitioners
        """
        kelly_fractions = []

        for ticker in df['ticker']:
            if ticker in returns.columns:
                stock_returns = returns[ticker]

                # Estimate win probability
                win_prob = (stock_returns > 0).mean()

                if win_prob > 0 and win_prob < 1:
                    avg_win = stock_returns[stock_returns > 0].mean()
                    avg_loss = abs(stock_returns[stock_returns < 0].mean())

                    if avg_loss > 0:
                        # Kelly formula: f* = (bp - q) / b
                        b = avg_win / avg_loss
                        kelly = (b * win_prob - (1 - win_prob)) / b
                        kelly_fractions.append(max(0, kelly * fraction))
                    else:
                        kelly_fractions.append(0)
                else:
                    kelly_fractions.append(0)
            else:
                kelly_fractions.append(0)

        df['kelly_fraction'] = kelly_fractions

        # Adjust weights by Kelly fraction
        df['adjusted_weight'] = df['weight'] * df['kelly_fraction']

        # Renormalize
        total_weight = df['adjusted_weight'].sum()
        if total_weight > 0:
            df['adjusted_weight'] = df['adjusted_weight'] / total_weight

        return df


# ========================
# Utility Functions
# ========================

def calculate_performance_metrics(returns: pd.Series,
                                 risk_free_rate: float = 0.02) -> Dict:
    """
    Calculate comprehensive performance metrics

    Parameters:
    -----------
    returns : Series
        Daily returns
    risk_free_rate : float
        Annual risk-free rate

    Returns:
    --------
    metrics : dict
        Performance metrics
    """
    # Annualized return
    cumulative_return = (1 + returns).prod()
    n_years = len(returns) / 252
    annual_return = cumulative_return ** (1/n_years) - 1

    # Volatility
    annual_vol = returns.std() * np.sqrt(252)

    # Sharpe ratio
    excess_returns = returns - risk_free_rate/252
    sharpe = np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    # Sortino ratio
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.sqrt((downside_returns**2).mean())
    sortino = np.sqrt(252) * excess_returns.mean() / downside_std if downside_std > 0 else np.inf

    # Maximum drawdown
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = abs(drawdown.min())

    # Calmar ratio
    calmar = annual_return / max_drawdown if max_drawdown > 0 else np.inf

    # Win rate
    win_rate = (returns > 0).mean()

    return {
        'Annual Return': annual_return,
        'Annual Volatility': annual_vol,
        'Sharpe Ratio': sharpe,
        'Sortino Ratio': sortino,
        'Calmar Ratio': calmar,
        'Max Drawdown': max_drawdown,
        'Win Rate': win_rate,
        'Cumulative Return': cumulative_return - 1
    }


# ========================
# Example Usage
# ========================

if __name__ == '__main__':
    """
    Example usage of the stock filtering pipeline
    """

    # Load sample data (replace with actual data loading)
    # df = pd.read_csv('stock_universe.csv')
    # returns_df = pd.read_csv('stock_returns.csv', index_col=0, parse_dates=True)

    # Create sample data for demonstration
    np.random.seed(42)
    n_stocks = 3000

    sample_df = pd.DataFrame({
        'ticker': [f'STOCK_{i:04d}' for i in range(n_stocks)],
        'market_cap': np.random.lognormal(20, 2, n_stocks),
        'avg_daily_volume': np.random.lognormal(14, 1.5, n_stocks),
        'price': np.random.lognormal(3, 1, n_stocks),
        'history_days': np.random.randint(100, 500, n_stocks),
        'return_12m': np.random.normal(0.10, 0.30, n_stocks),
        'return_6m': np.random.normal(0.05, 0.20, n_stocks),
        'volatility': np.random.gamma(2, 0.10, n_stocks),
        'beta': np.random.normal(1.0, 0.3, n_stocks),
        'book_to_market': np.random.lognormal(0, 0.5, n_stocks),
        'earnings_yield': np.random.normal(0.05, 0.03, n_stocks),
        'price_to_sales': np.random.lognormal(0.5, 0.8, n_stocks),
        'roe': np.random.normal(0.12, 0.08, n_stocks),
        'roa': np.random.normal(0.06, 0.05, n_stocks),
        'debt_to_equity': np.random.gamma(2, 0.5, n_stocks)
    })

    # Sample returns data
    n_days = 252
    sample_returns = pd.DataFrame(
        np.random.normal(0.0005, 0.02, (n_days, n_stocks)),
        columns=sample_df['ticker']
    )

    # Initialize pipeline
    pipeline = StockFilteringPipeline(verbose=True)

    # Run pipeline
    final_selection = pipeline.run_pipeline(sample_df, sample_returns)

    # Display results
    print("\nFinal Stock Selection:")
    print("=" * 80)
    display_cols = ['ticker', 'final_rank', 'final_weight', 'value_score',
                   'momentum_score', 'quality_score']
    display_cols = [c for c in display_cols if c in final_selection.columns]
    print(final_selection[display_cols].to_string(index=False))

    # Calculate portfolio performance
    selected_tickers = final_selection['ticker'].values
    selected_returns = sample_returns[selected_tickers]

    # Equal-weighted portfolio returns
    portfolio_returns = selected_returns.mean(axis=1)

    # Performance metrics
    metrics = calculate_performance_metrics(portfolio_returns)

    print("\nPortfolio Performance Metrics:")
    print("=" * 80)
    for metric, value in metrics.items():
        if 'Return' in metric or 'Drawdown' in metric:
            print(f"{metric:.<40} {value:>10.2%}")
        elif 'Rate' in metric:
            print(f"{metric:.<40} {value:>10.2%}")
        else:
            print(f"{metric:.<40} {value:>10.2f}")
