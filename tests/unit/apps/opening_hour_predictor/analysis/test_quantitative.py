import pytest
import pandas as pd
import numpy as np
from apps.opening_hour_predictor.analysis.quantitative import QuantitativeAnalyzer

class TestQuantitativeAnalyzer:

    @pytest.fixture
    def analyzer(self):
        config = {'analysis': {'max_compute_workers': 1}}
        return QuantitativeAnalyzer(config)

    @pytest.fixture
    def market_data(self):
        dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
        np.random.seed(42)

        # Create a trending data pattern
        close = np.linspace(100, 110, 100) + np.random.normal(0, 0.5, 100)

        df = pd.DataFrame({
            'open': close - 0.1,
            'high': close + 0.2,
            'low': close - 0.2,
            'close': close,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)

        return df

    def test_calculate_rsi(self, analyzer, market_data):
        rsi = analyzer.calculate_rsi(market_data['close'], period=14)
        assert isinstance(rsi, pd.Series)
        assert len(rsi) == len(market_data)
        # RSI should be between 0 and 100
        # Skip first 14 (NaNs)
        assert rsi.iloc[15:].between(0, 100).all()

    def test_calculate_macd(self, analyzer, market_data):
        macd = analyzer.calculate_macd(market_data['close'])
        assert isinstance(macd, pd.DataFrame)
        assert all(col in macd.columns for col in ['macd', 'signal', 'histogram'])

    def test_calculate_stochastic(self, analyzer, market_data):
        stoch = analyzer.calculate_stochastic(
            market_data['high'], market_data['low'], market_data['close']
        )
        assert isinstance(stoch, pd.DataFrame)
        assert 'stoch_k' in stoch.columns
        assert 'stoch_d' in stoch.columns
        assert stoch['stoch_k'].iloc[20:].between(0, 100).all()

    def test_calculate_vwap(self, analyzer, market_data):
        vwap = analyzer.calculate_vwap(
            market_data['high'], market_data['low'],
            market_data['close'], market_data['volume']
        )
        assert isinstance(vwap, pd.Series)
        # VWAP should track price roughly
        assert abs(vwap.iloc[-1] - market_data['close'].iloc[-1]) < 10.0

    def test_detect_volume_spike(self, analyzer, market_data):
        # Create a massive spike
        market_data.iloc[-1, market_data.columns.get_loc('volume')] = 1_000_000

        spikes = analyzer.detect_volume_spike(market_data['volume'], std_threshold=2.0)
        assert spikes.iloc[-1] == True
        assert spikes.iloc[0] == False # Early data might be false or NaN logic dependent

    def test_calculate_atr(self, analyzer, market_data):
        atr = analyzer.calculate_atr(
            market_data['high'], market_data['low'], market_data['close']
        )
        assert isinstance(atr, pd.Series)
        assert atr.iloc[-1] > 0

    def test_calculate_bollinger_bands(self, analyzer, market_data):
        bb = analyzer.calculate_bollinger_bands(market_data['close'])
        assert all(col in bb.columns for col in ['bb_upper', 'bb_lower', 'bb_middle'])
        assert (bb['bb_upper'] >= bb['bb_middle']).all()
        assert (bb['bb_lower'] <= bb['bb_middle']).all()

    def test_calculate_gap(self, analyzer):
        # Large gap up
        res = analyzer.calculate_gap(102.0, 100.0)
        assert res['gap_percent'] == 2.0
        assert res['gap_type'] == 'large'
        assert res['direction'] == 'up'

        # Small gap down
        res = analyzer.calculate_gap(99.5, 100.0)
        assert res['gap_percent'] == -0.5
        assert res['gap_type'] == 'small'
        assert res['direction'] == 'down'

    def test_calculate_opening_range(self, analyzer, market_data):
        or_data = analyzer.calculate_opening_range(market_data, minutes=5)
        assert 'or_high' in or_data
        assert 'range_size' in or_data
        assert or_data['range_size'] >= 0

    def test_calculate_all_indicators(self, analyzer, market_data):
        result = analyzer.calculate_all_indicators(market_data)

        expected_cols = [
            'rsi_14', 'macd', 'vwap', 'atr', 'bb_upper',
            'sma_20', 'above_sma_20', 'volume_spike'
        ]
        for col in expected_cols:
            assert col in result.columns

    def test_get_latest_metrics(self, analyzer, market_data):
        result = analyzer.calculate_all_indicators(market_data)
        metrics = analyzer.get_latest_metrics(result)

        assert 'latest_price' in metrics
        assert 'rsi_14' in metrics
        assert metrics['latest_price'] == market_data['close'].iloc[-1]
