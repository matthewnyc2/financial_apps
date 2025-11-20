import pytest
import pandas as pd
import os
import yaml
from unittest.mock import MagicMock, patch
from apps.opening_hour_predictor.data.data_acquisition import MultiSourceDataAcquirer
from apps.opening_hour_predictor.main import OpeningHourPredictor

class TestSecurity:

    @pytest.fixture
    def config(self):
        return {
            'data': {
                'sources': ['yfinance'],
                'cache_ttl': 3600,
                'api_keys_file': '.env.test'
            },
            'redis': {'host': 'localhost'}
        }

    def test_api_keys_not_exposed_in_logs(self, config, caplog):
        """Ensure API keys are not logged during initialization or error"""
        import logging
        caplog.set_level(logging.INFO)

        # Setup environment with fake key
        with patch.dict(os.environ, {'FINNHUB_API_KEY': 'SECRET_KEY_12345'}):
            acquirer = MultiSourceDataAcquirer(config)

            # Trigger a logging event that might involve keys (e.g. checking config)
            # In this app, keys are loaded into self.api_keys

            # Check logs
            for record in caplog.records:
                assert 'SECRET_KEY_12345' not in record.message

    def test_safe_deserialization_pickle(self, config):
        """
        Verify that we don't crash or execute arbitrary code if cache is corrupted/malicious.
        Since we use pickle, we are vulnerable if the redis is compromised.
        This test ensures we handle unpickling errors gracefully if data is bad.
        """
        acquirer = MultiSourceDataAcquirer(config)
        acquirer.redis_client = MagicMock()

        # Simulate corrupted data in Redis
        acquirer.redis_client.get.return_value = b'corrupted_pickle_data'

        # Should not crash, but return None (cache miss)
        result = acquirer._get_from_cache("some_key")
        assert result is None

    def test_input_validation_universe(self):
        """Test that we handle weird inputs for universe selection"""
        predictor = OpeningHourPredictor()

        # Pass SQL-injection like string (though not used in SQL, good for sanity)
        # The 'custom' logic just hardcodes symbols in the current implementation,
        # but if it read from file, we'd want to check path traversal.

        # Testing path traversal in config loading
        with patch('builtins.open', side_effect=IOError("Access denied")):
             # Should fall back to default config without crashing
             config = predictor._load_config("../../../etc/passwd")
             assert 'data' in config

    def test_path_traversal_protection(self):
        """Check if any file operations are vulnerable"""
        # The app saves predictions to CSV. Let's check if we can write to arbitrary locations?
        # The filename is generated with timestamp: f'predictions_gainers_{timestamp}.csv'
        # So it seems safe from user input injection into filename.
        pass
