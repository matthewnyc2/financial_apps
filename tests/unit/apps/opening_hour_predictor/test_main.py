import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from apps.opening_hour_predictor.main import OpeningHourPredictor

class TestOpeningHourPredictor:

    @pytest.fixture
    def predictor(self):
        with patch('apps.opening_hour_predictor.main.MultiSourceDataAcquirer'), \
             patch('apps.opening_hour_predictor.main.QuantitativeAnalyzer'):
            return OpeningHourPredictor()

    def test_initialization(self, predictor):
        assert predictor.config is not None
        assert predictor.data_acquirer is not None
        assert predictor.quant_analyzer is not None

    @patch('apps.opening_hour_predictor.main.get_sp500_symbols')
    def test_download_universe(self, mock_get_symbols, predictor):
        mock_get_symbols.return_value = ['AAPL', 'MSFT']

        symbols = predictor.download_universe('sp500')
        assert symbols == ['AAPL', 'MSFT']

        # Test custom
        symbols = predictor.download_universe('custom')
        assert 'AAPL' in symbols

    def test_score_stocks(self, predictor):
        # Mock analyzed data
        df = pd.DataFrame({'close': [100, 101, 102]})
        analyzed_data = {'AAPL': df, 'MSFT': df}

        # Mock quant analyzer metrics
        predictor.quant_analyzer.get_latest_metrics.side_effect = [
            {
                'latest_price': 150,
                'rsi_14': 20, # Oversold -> +30
                'macd_histogram': 0.1, # Positive -> +25
                'above_sma_20': True,
                'above_sma_50': True, # Above -> +20
                'volume_spike': True, # Spike -> +15
                'volatility': 0.20 # Good -> +10
            },
            {
                'latest_price': 200,
                'rsi_14': 80, # Overbought -> -30
                'macd_histogram': -0.1, # Negative -> -25
            }
        ]

        scores = predictor.score_stocks(analyzed_data)

        assert len(scores) == 2

        # Check AAPL score: 30 + 25 + 20 + 15 + 10 = 100
        aapl_score = scores[scores['symbol'] == 'AAPL']['score'].iloc[0]
        assert aapl_score == 100

        # Check MSFT score: -30 - 25 - 20 (not above MA) = -75
        msft_score = scores[scores['symbol'] == 'MSFT']['score'].iloc[0]
        assert msft_score < 0

    def test_predict_gainers_losers(self, predictor):
        df_scores = pd.DataFrame({
            'symbol': ['A', 'B', 'C', 'D'],
            'score': [100, 50, -50, -100]
        })

        gainers = predictor.predict_gainers(df_scores, top_n=2)
        assert len(gainers) == 2
        assert gainers.iloc[0]['symbol'] == 'A'

        losers = predictor.predict_losers(df_scores, top_n=2)
        assert len(losers) == 2
        assert losers.iloc[0]['symbol'] == 'D' # Should be sorted by worst score

    @patch('apps.opening_hour_predictor.main.OpeningHourPredictor.download_historical_data')
    @patch('apps.opening_hour_predictor.main.OpeningHourPredictor.calculate_indicators')
    @patch('apps.opening_hour_predictor.main.OpeningHourPredictor.score_stocks')
    def test_run_prediction_flow(self, mock_score, mock_calc, mock_download, predictor):
        # Setup mocks
        mock_download.return_value = {'AAPL': pd.DataFrame()}
        mock_calc.return_value = {'AAPL': pd.DataFrame()}

        scores_df = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT'],
            'score': [10, -10],
            'latest_price': [100, 200],
            'rsi_14': [50, 50],
            'macd_histogram': [0, 0],
            'volatility': [0.1, 0.1],
            'volume_spike': [False, False],
            'reasons': ['', '']
        })
        mock_score.return_value = scores_df

        # Run with small limit
        gainers, losers = predictor.run_prediction(universe='sp500', limit=2)

        assert len(gainers) > 0
        assert len(losers) > 0
        mock_download.assert_called()
        mock_calc.assert_called()
        mock_score.assert_called()
