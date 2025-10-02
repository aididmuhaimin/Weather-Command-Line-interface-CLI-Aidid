"""
Unit tests for the CLI module.

Tests command-line interface functionality including argument parsing,
error handling, and output formatting using Click's testing utilities.
"""

import pytest
import logging
import json
from unittest.mock import Mock, patch
from click.testing import CliRunner

from weather_cli.cli import main, setup_logging
from weather_cli.exceptions import CityNotFoundError, InvalidAPIKeyError, APIRequestError
from tests import TEST_API_KEY, TEST_CITY, TEST_COUNTRY

logger = logging.getLogger(__name__)


class TestCLI:
    """Test cases for CLI interface."""
    
    @pytest.fixture
    def runner(self):
        """Create a test runner for Click commands."""
        return CliRunner()
    
    @pytest.fixture
    def mock_weather_api(self):
        """Create mock WeatherAPI instance."""
        mock_api = Mock()
        mock_api.get_coordinates.return_value = (3.0, 101.5)
        mock_api.get_weather_data.return_value = {
            'current': {
                'main': {'temp': 28.5},
                'weather': [{'description': 'cloudy'}],
                'name': 'Puchong',
                'sys': {'country': 'MY'}
            },
            'forecast': [
                {
                    'date': '2024-01-15',
                    'temp_min': 25.0,
                    'temp_max': 30.0,
                    'weather': 'Clouds'
                }
            ]
        }
        return mock_api
    
    def test_cli_help(self, runner):
        """Test CLI help command."""
        logger.debug("Testing CLI help")
        
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Fetch and display weather information" in result.output
        assert "--city" in result.output
        assert "--country" in result.output
        assert "--debug" in result.output
        
        logger.info("CLI help test passed")
    
    def test_cli_basic_success(self, runner, mock_weather_api):
        """Test successful basic CLI execution."""
        logger.debug("Testing basic CLI success")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_weather_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, ['--city', TEST_CITY, '--country', TEST_COUNTRY])
            
            assert result.exit_code == 0
            assert TEST_CITY in result.output
            
        logger.info("Basic CLI success test passed")
    
    def test_cli_with_debug(self, runner, mock_weather_api):
        """Test CLI with debug mode."""
        logger.debug("Testing CLI with debug mode")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_weather_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY, 
                '--debug'
            ])
            
            assert result.exit_code == 0
            
        logger.info("CLI debug mode test passed")
    
    def test_cli_different_units(self, runner, mock_weather_api):
        """Test CLI with different units."""
        logger.debug("Testing CLI with different units")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_weather_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            # Test imperial units
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY, 
                '--units', 'imperial'
            ])
            
            assert result.exit_code == 0
            
        logger.info("CLI units test passed")
    
    def test_cli_json_output(self, runner, mock_weather_api):
        """Test CLI JSON output format."""
        logger.debug("Testing CLI JSON output")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_weather_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY, 
                '--format', 'json'
            ])
            
            assert result.exit_code == 0
            
            # Check if output is valid JSON
            try:
                json_data = json.loads(result.output)
                assert 'current' in json_data
                assert 'forecast' in json_data
            except json.JSONDecodeError:
                pytest.fail("Output is not valid JSON")
        
        logger.info("CLI JSON output test passed")
    
    def test_cli_missing_api_key(self, runner):
        """Test CLI without API key."""
        logger.debug("Testing CLI without API key")
        
        with patch('os.getenv', return_value=None):
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY
            ])
            
            assert result.exit_code == 1
            assert "API key not found" in result.output
        
        logger.info("Missing API key test passed")
    
    def test_cli_city_not_found(self, runner):
        """Test CLI with city not found error."""
        logger.debug("Testing CLI city not found error")
        
        mock_api = Mock()
        mock_api.get_coordinates.side_effect = CityNotFoundError("TestCity", "XX")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', 'TestCity', 
                '--country', 'XX'
            ])
            
            assert result.exit_code == 1
            assert "TestCity" in result.output
            assert "XX" in result.output
        
        logger.info("City not found test passed")
    
    def test_cli_invalid_api_key(self, runner):
        """Test CLI with invalid API key."""
        logger.debug("Testing CLI invalid API key")
        
        mock_api = Mock()
        mock_api.get_coordinates.side_effect = InvalidAPIKeyError("Invalid API key")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY
            ])
            
            assert result.exit_code == 1
            assert "Invalid API key" in result.output
        
        logger.info("Invalid API key test passed")
    
    def test_cli_api_request_error(self, runner):
        """Test CLI with API request error."""
        logger.debug("Testing CLI API request error")
        
        mock_api = Mock()
        mock_api.get_coordinates.side_effect = APIRequestError("Network error")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY
            ])
            
            assert result.exit_code == 1
            assert "Network error" in result.output
        
        logger.info("API request error test passed")
    
    def test_cli_keyboard_interrupt(self, runner):
        """Test CLI handling of keyboard interrupt."""
        logger.debug("Testing CLI keyboard interrupt handling")
        
        mock_api = Mock()
        mock_api.get_coordinates.side_effect = KeyboardInterrupt()
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY
            ])
            
            assert result.exit_code == 1
            assert "cancelled" in result.output
        
        logger.info("Keyboard interrupt test passed")
    
    def test_cli_with_log_file(self, runner, mock_weather_api):
        """Test CLI with log file output."""
        logger.debug("Testing CLI with log file")
        
        with patch('weather_cli.cli.WeatherAPI', return_value=mock_weather_api), \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            with runner.isolated_filesystem():
                result = runner.invoke(main, [
                    '--city', TEST_CITY, 
                    '--country', TEST_COUNTRY,
                    '--log-file', 'test.log'
                ])
                
                assert result.exit_code == 0
                
                # Check if log file was created
                import os
                assert os.path.exists('test.log')
        
        logger.info("Log file test passed")


class TestCLIValidation:
    """Test CLI input validation."""
    
    def test_cli_missing_required_args(self, runner):
        """Test CLI with missing required arguments."""
        logger.debug("Testing CLI missing required arguments")
        
        # Missing --city
        result = runner.invoke(main, ['--country', 'MY'])
        assert result.exit_code == 2
        assert "Missing option '--city'" in result.output
        
        # Missing --country
        result = runner.invoke(main, ['--city', 'Puchong'])
        assert result.exit_code == 2
        assert "Missing option '--country'" in result.output
        
        logger.info("Missing arguments test passed")
    
    def test_cli_invalid_units(self, runner):
        """Test CLI with invalid units option."""
        logger.debug("Testing CLI invalid units")
        
        result = runner.invoke(main, [
            '--city', TEST_CITY, 
            '--country', TEST_COUNTRY,
            '--units', 'invalid'
        ])
        
        assert result.exit_code == 2
        assert "Invalid value for '--units'" in result.output
        
        logger.info("Invalid units test passed")
    
    def test_cli_invalid_format(self, runner):
        """Test CLI with invalid format option."""
        logger.debug("Testing CLI invalid format")
        
        result = runner.invoke(main, [
            '--city', TEST_CITY, 
            '--country', TEST_COUNTRY,
            '--format', 'invalid'
        ])
        
        assert result.exit_code == 2
        assert "Invalid value for '--format'" in result.output
        
        logger.info("Invalid format test passed")


class TestCLIOptions:
    """Test various CLI options and configurations."""
    
    def test_cli_timeout_option(self, runner, mock_weather_api):
        """Test CLI with custom timeout."""
        logger.debug("Testing CLI timeout option")
        
        with patch('weather_cli.cli.WeatherAPI') as mock_api_class, \
             patch('os.getenv', return_value=TEST_API_KEY):
            
            mock_api_class.return_value = mock_weather_api
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY,
                '--timeout', '30'
            ])
            
            assert result.exit_code == 0
            
            # Verify API was created with timeout
            mock_api_class.assert_called_once_with(api_key=TEST_API_KEY, timeout=30)
        
        logger.info("Timeout option test passed")
    
    def test_cli_api_key_option(self, runner, mock_weather_api):
        """Test CLI with API key option."""
        logger.debug("Testing CLI API key option")
        
        test_key = "custom-api-key-12345"
        
        with patch('weather_cli.cli.WeatherAPI') as mock_api_class, \
             patch('os.getenv', return_value=None):  # No env var
            
            mock_api_class.return_value = mock_weather_api
            
            result = runner.invoke(main, [
                '--city', TEST_CITY, 
                '--country', TEST_COUNTRY,
                '--api-key', test_key
            ])
            
            assert result.exit_code == 0
            
            # Verify API was created with custom key
            mock_api_class.assert_called_once_with(api_key=test_key, timeout=10)
        
        logger.info("API key option test passed")


def test_run_cli_function():
    """Test the run_cli entry point function."""
    logger.debug("Testing run_cli function")
    
    with patch('weather_cli.cli.main') as mock_main:
        from weather_cli.cli import run_cli
        
        run_cli()
        mock_main.assert_called_once()
    
    logger.info("run_cli function test passed")


def test_setup_logging():
    """Test logging setup function."""
    logger.debug("Testing setup_logging function")
    
    # Test debug mode
    setup_logging(debug=True)
    assert logging.getLogger().level == logging.DEBUG
    
    # Test normal mode
    setup_logging(debug=False)
    assert logging.getLogger().level == logging.INFO
    
    logger.info("setup_logging function test passed")