import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from stock_filtering_pipeline import StockFilteringPipeline

class TestStockFilteringPipeline:

    @pytest.fixture
    def pipeline(self):
        return StockFilteringPipeline(verbose=False)

    @pytest.fixture
    def sample_stock_data(self):
        np.random.seed(42)
        n_stocks = 50

        df = pd.DataFrame({
            'ticker': [f'STOCK_{i:04d}' for i in range(n_stocks)],
            'market_cap': np.random.uniform(1e8, 1e10, n_stocks),
            'avg_daily_volume': np.random.uniform(1e5, 1e7, n_stocks),
            'price': np.random.uniform(10, 100, n_stocks),
            'history_days': np.random.randint(200, 300, n_stocks),
            'return_12m': np.random.normal(0.1, 0.2, n_stocks),
            'return_6m': np.random.normal(0.05, 0.1, n_stocks),
            'volatility': np.random.uniform(0.1, 0.5, n_stocks),
            'beta': np.random.normal(1.0, 0.2, n_stocks),
            'book_to_market': np.random.uniform(0.1, 2.0, n_stocks),
            'earnings_yield': np.random.normal(0.05, 0.02, n_stocks),
            'price_to_sales': np.random.uniform(0.5, 5.0, n_stocks),
            'roe': np.random.normal(0.15, 0.05, n_stocks),
            'roa': np.random.normal(0.05, 0.02, n_stocks),
            'debt_to_equity': np.random.uniform(0.1, 2.0, n_stocks)
        })
        return df

    @pytest.fixture
    def sample_returns_data(self, sample_stock_data):
        n_days = 100
        tickers = sample_stock_data['ticker'].values
        returns = np.random.normal(0.001, 0.02, (n_days, len(tickers)))
        return pd.DataFrame(returns, columns=tickers)

    def test_initialization(self):
        pipeline = StockFilteringPipeline()
        assert pipeline.config is not None
        assert 'stage1' in pipeline.config

    def test_stage1_exclusion(self, pipeline, sample_stock_data):
        # Modify one stock to be excluded
        sample_stock_data.loc[0, 'market_cap'] = 100  # Very small cap

        result = pipeline.stage1_exclusion(sample_stock_data)

        assert len(result) < len(sample_stock_data)
        assert 'STOCK_0000' not in result['ticker'].values

    @patch('sklearn.covariance.MinCovDet')
    def test_stage2_outlier_detection(self, mock_mcd, pipeline, sample_stock_data):
        # Setup mock MCD
        mock_mcd_instance = MagicMock()
        mock_mcd_instance.mahalanobis.return_value = np.zeros(len(sample_stock_data)) # No outliers by default
        mock_mcd.return_value = mock_mcd_instance

        result = pipeline.stage2_outlier_detection(sample_stock_data)

        assert len(result) == len(sample_stock_data)

        # Test with outliers
        # Mock mahalanobis to return high values for first stock
        dists = np.zeros(len(sample_stock_data))
        dists[0] = 1000.0 # High distance
        mock_mcd_instance.mahalanobis.return_value = dists

        result_with_outliers = pipeline.stage2_outlier_detection(sample_stock_data)
        assert len(result_with_outliers) < len(sample_stock_data)

    def test_stage3_clustering(self, pipeline, sample_stock_data):
        # Ensure we have enough data for clustering
        pipeline.config['stage3']['n_clusters'] = 2
        pipeline.config['stage3']['top_pct_per_cluster'] = 0.5

        # Need to calculate scores first or ensure cols exist?
        # The method _calculate_factor_scores handles score creation.

        result = pipeline.stage3_clustering(sample_stock_data)

        assert 'cluster' in result.columns
        assert 'composite_score' in result.columns
        assert len(result) > 0

    def test_stage4_pca_ranking(self, pipeline, sample_stock_data):
        # Add necessary columns from previous stages (mocking them)
        df = sample_stock_data.copy()
        df['cluster'] = 0
        df['composite_score'] = 0.5
        df['value_score'] = 0.5
        df['momentum_score'] = 0.5
        df['quality_score'] = 0.5

        pipeline.config['stage4']['n_pca_components'] = 2
        pipeline.config['stage4']['top_n'] = 10

        result = pipeline.stage4_pca_ranking(df)

        assert 'PC1' in result.columns
        assert 'final_rank' in result.columns
        assert len(result) <= 10

    def test_stage5_optimization(self, pipeline, sample_stock_data, sample_returns_data):
        # Prepare input dataframe
        df = sample_stock_data.head(10).copy()

        # Mock minimize to return equal weights
        with patch('scipy.optimize.minimize') as mock_minimize:
            mock_result = MagicMock()
            mock_result.x = np.ones(len(df)) / len(df)
            mock_minimize.return_value = mock_result

            result = pipeline.stage5_optimization(df, sample_returns_data)

            assert 'weight' in result.columns
            assert 'final_weight' in result.columns
            assert len(result) > 0

    def test_full_pipeline_run(self, pipeline, sample_stock_data, sample_returns_data):
        # We need to mock the heavy lifting parts to ensure this unit test runs fast
        # and doesn't depend on specific statistical outcomes

        # Relax constraints for the small sample size
        pipeline.config['stage1']['min_market_cap'] = 0
        pipeline.config['stage1']['min_avg_volume'] = 0
        pipeline.config['stage3']['n_clusters'] = 2
        pipeline.config['stage5']['target_n'] = 5

        # Mock MCD to avoid dropping too many
        with patch('sklearn.covariance.MinCovDet') as mock_mcd:
             mock_mcd_instance = MagicMock()
             mock_mcd_instance.mahalanobis.return_value = np.zeros(len(sample_stock_data))
             mock_mcd.return_value = mock_mcd_instance

             result = pipeline.run_pipeline(sample_stock_data, sample_returns_data)

             assert not result.empty
             assert 'final_weight' in result.columns
