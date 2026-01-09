import pytest
import pandas as pd
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from apps.opening_hour_predictor.data.data_acquisition import MultiSourceDataAcquirer

class TestMultiSourceDataAcquirer:

    @pytest.fixture
    def config(self):
        return {
            'data': {
                'sources': ['yfinance'],
                'cache_ttl': 3600,
                'max_download_workers': 2
            },
            'redis': {
                'host': 'localhost',
                'port': 6379
            }
        }

    @pytest.fixture
    def acquirer(self, config):
        with patch('redis.Redis'): # Mock redis connection during init
            return MultiSourceDataAcquirer(config)

    def test_initialization(self, acquirer):
        assert acquirer.redis_client is not None  # It's a mock
        assert acquirer.config is not None

    @patch('yfinance.Ticker')
    def test_fetch_yfinance_success(self, mock_ticker_cls, acquirer):
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker

        # Create sample data
        dates = pd.date_range('2024-01-01', periods=10, freq='5min')
        df = pd.DataFrame({
            'Open': [100]*10,
            'High': [105]*10,
            'Low': [95]*10,
            'Close': [101]*10,
            'Volume': [1000]*10
        }, index=dates)

        mock_ticker.history.return_value = df

        result = acquirer._fetch_yfinance('AAPL', '2024-01-01', '2024-01-02')

        assert not result.empty
        assert 'close' in result.columns # Lowercase check

    @patch('yfinance.Ticker')
    def test_fetch_yfinance_empty(self, mock_ticker_cls, acquirer):
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame()

        with pytest.raises(ValueError):
            acquirer._fetch_yfinance('INVALID', '2024-01-01', '2024-01-02')

    def test_caching(self, acquirer):
        acquirer.redis_client = MagicMock()

        # Test cache miss
        acquirer.redis_client.get.return_value = None
        assert acquirer._get_from_cache("key") is None

        # Test cache hit
        import pickle
        df = pd.DataFrame({'a': [1, 2, 3]})
        acquirer.redis_client.get.return_value = pickle.dumps(df)

        cached_df = acquirer._get_from_cache("key")
        pd.testing.assert_frame_equal(df, cached_df)

    @patch('apps.opening_hour_predictor.data.data_acquisition.MultiSourceDataAcquirer._fetch_yfinance')
    def test_download_stock_with_fallback(self, mock_yf, acquirer):
        # Setup
        acquirer.config['data']['sources'] = ['finnhub', 'yfinance']

        # Mock finnhub failure (async)
        # Since finnhub is called via asyncio.run, we need to mock the internal async method or the call wrapper
        # The easiest way is to mock `_fetch_finnhub_async` to raise exception

        with patch('apps.opening_hour_predictor.data.data_acquisition.MultiSourceDataAcquirer._fetch_finnhub_async', side_effect=ValueError("Finnhub failed")):
            # Mock yfinance success
            dates = pd.date_range('2024-01-01', periods=10)
            df_yf = pd.DataFrame({'close': [100]*10}, index=dates)
            mock_yf.return_value = df_yf

            # Run
            result = acquirer.download_stock('AAPL', '2024-01-01', '2024-01-02')

            assert result is df_yf
            mock_yf.assert_called_once()

    def test_download_multiple_stocks(self, acquirer):
        symbols = ['AAPL', 'MSFT']

        # Mock download_stock
        acquirer.download_stock = MagicMock()
        acquirer.download_stock.side_effect = [
            pd.DataFrame({'close': [100]}), # AAPL
            pd.DataFrame({'close': [200]})  # MSFT
        ]

        results = acquirer.download_multiple_stocks(symbols, '2024-01-01', '2024-01-02')

        assert len(results) == 2
        assert 'AAPL' in results
        assert 'MSFT' in results

    @patch('yfinance.Ticker')
    def test_fetch_news(self, mock_ticker_cls, acquirer):
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker

        mock_ticker.news = [
            {
                'title': 'Test News',
                'publisher': 'Test Pub',
                'link': 'http://test.com',
                'providerPublishTime': pd.Timestamp.now().timestamp()
            }
        ]

        news = acquirer.fetch_news('AAPL')
        assert len(news) == 1
        assert news[0]['title'] == 'Test News'
