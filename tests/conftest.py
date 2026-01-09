import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import MagicMock

@pytest.fixture
def sample_config():
    return {
        'data': {
            'sources': ['yfinance'],
            'cache_ttl': 3600,
            'max_download_workers': 2,
            'rate_limit_per_minute': 100
        },
        'analysis': {
            'max_compute_workers': 2,
            'technical_indicators': ['rsi_14', 'macd']
        },
        'redis': {
            'host': 'localhost',
            'port': 6379
        },
        'prediction': {
            'top_n_gainers': 5,
            'top_n_losers': 5
        }
    }

@pytest.fixture
def sample_ohlcv_data():
    """Generates a sample OHLCV DataFrame for testing"""
    dates = pd.date_range(start='2024-01-01', periods=100, freq='5min')
    np.random.seed(42)

    df = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)

    # Ensure high is highest and low is lowest
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)

    return df

@pytest.fixture
def mock_redis():
    mock = MagicMock()
    mock.get.return_value = None
    return mock

@pytest.fixture
def mock_yfinance_ticker():
    mock_ticker = MagicMock()
    # Mock history method
    dates = pd.date_range(start='2024-01-01', periods=50, freq='5min')
    df = pd.DataFrame({
        'Open': np.random.randn(50) + 100,
        'High': np.random.randn(50) + 105,
        'Low': np.random.randn(50) + 95,
        'Close': np.random.randn(50) + 100,
        'Volume': np.random.randint(1000, 10000, 50)
    }, index=dates)
    mock_ticker.history.return_value = df
    return mock_ticker
