import pytest
import pandas as pd
import numpy as np
import time
from apps.opening_hour_predictor.analysis.quantitative import QuantitativeAnalyzer

class TestPerformance:

    @pytest.fixture
    def large_dataset(self):
        # Generate 1 year of 5-min data (~25k rows)
        dates = pd.date_range('2024-01-01', periods=25000, freq='5min')
        df = pd.DataFrame({
            'open': np.random.randn(25000).cumsum() + 100,
            'high': np.random.randn(25000).cumsum() + 105,
            'low': np.random.randn(25000).cumsum() + 95,
            'close': np.random.randn(25000).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 25000)
        }, index=dates)
        return df

    def test_indicator_calculation_benchmark(self, large_dataset):
        """
        Benchmark for indicator calculation.
        Note: We avoid asserting on wall-clock time to keep tests deterministic in CI.
        """
        config = {'analysis': {'max_compute_workers': 1}}
        analyzer = QuantitativeAnalyzer(config)

        start_time = time.time()
        result = analyzer.calculate_all_indicators(large_dataset)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Analysis of 25k rows took {duration:.4f} seconds")

        # Verify the operation completed successfully and produced expected output size
        assert len(result) == 25000
        assert 'rsi_14' in result.columns

    def test_batch_processing_benchmark(self, large_dataset):
        """
        Benchmark for batch processing overhead.
        """
        config = {'analysis': {'max_compute_workers': 2}}
        analyzer = QuantitativeAnalyzer(config)

        # Create 4 stocks
        stock_data = {f'STOCK_{i}': large_dataset.copy() for i in range(4)}

        start_time = time.time()
        results = analyzer.analyze_multiple_stocks(stock_data)
        end_time = time.time()

        duration = end_time - start_time
        print(f"Batch analysis of 4 stocks (100k rows total) took {duration:.4f} seconds")

        assert len(results) == 4
