"""
Unit tests for the WeatherAPI class.

Tests API communication, error handling, and data processing without 
making real API calls by using mocks.
"""

import pytest
import logging
from unittest.mock import Mock, patch
import requests

from weather_cli.weather_api import WeatherAPI
from weather_cli.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    APIRequestError,
    RateLimitError,
    ServiceUnavailableError
)
from tests import (
    TEST_API_KEY,
    TEST_CITY,
    TEST_COUNTRY,
    SAMPLE_GEO_RESPONSE,
    SAMPLE_WEATHER_RESPONSE,
    SAMPLE_FORECAST_RESPONSE
)

logger = logging.getLogger(__name__)


class TestWeatherAPI:
    """Test cases for WeatherAPI class."""
    
    def test_init_with_valid_key(self):
        """Test successful initialization with valid API key."""
        logger.debug("Testing WeatherAPI initialization")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        assert api.api_key == TEST_API_KEY
        assert api.timeout == 10  # default
        assert api.session is not None
        
        logger.info("WeatherAPI initialization test passed")
    
    def test_init_without_key(self):
        """Test initialization fails without API key."""
        logger.debug("Testing WeatherAPI without API key")
        
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            WeatherAPI(api_key=None)
        
        assert "API key is required" in str(exc_info.value)
        logger.info("API key validation test passed")
    
    def test_init_with_invalid_key_format(self):
        """Test initialization fails with invalid key format."""
        logger.debug("Testing WeatherAPI with invalid key format")
        
        with pytest.raises(InvalidAPIKeyError) as exc_info:
            WeatherAPI(api_key="short")
        
        assert "invalid format" in str(exc_info.value)
        logger.info("API key format validation test passed")
    
    def test_init_with_timeout(self):
        """Test initialization with custom timeout."""
        logger.debug("Testing WeatherAPI with custom timeout")
        
        api = WeatherAPI(api_key=TEST_API_KEY, timeout=30)
        assert api.timeout == 30
        
        logger.info("Timeout configuration test passed")
    
    @patch('requests.Session.request')
    def test_get_coordinates_success(self, mock_request):
        """Test successful coordinate retrieval."""
        logger.debug("Testing successful coordinate retrieval")
        
        # Mock successful response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_GEO_RESPONSE
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        lat, lon = api.get_coordinates(TEST_CITY, TEST_COUNTRY)
        
        assert lat == 3.0
        assert lon == 101.5
        
        # Verify request was made correctly
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert TEST_CITY in call_args[1]['params']['q']
        assert TEST_COUNTRY in call_args[1]['params']['q']
        
        logger.info("Coordinate retrieval test passed")
    
    @patch('requests.Session.request')
    def test_get_coordinates_city_not_found(self, mock_request):
        """Test city not found handling."""
        logger.debug("Testing city not found scenario")
        
        # Mock empty response
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        with pytest.raises(CityNotFoundError) as exc_info:
            api.get_coordinates("InvalidCity", "XX")
        
        assert "InvalidCity" in str(exc_info.value)
        assert "XX" in str(exc_info.value)
        
        logger.info("City not found test passed")
    
    @patch('requests.Session.request')
    def test_get_coordinates_invalid_inputs(self, mock_request):
        """Test coordinate retrieval with invalid inputs."""
        logger.debug("Testing coordinate retrieval with invalid inputs")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Empty city
        with pytest.raises(ValueError):
            api.get_coordinates("", "MY")
        
        # Invalid country code
        with pytest.raises(ValueError):
            api.get_coordinates("Puchong", "MALAYSIA")
        
        logger.info("Input validation test passed")
    
    @patch('requests.Session.request')
    def test_get_weather_data_success(self, mock_request):
        """Test successful weather data retrieval."""
        logger.debug("Testing successful weather data retrieval")
        
        # Mock successful responses
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_WEATHER_RESPONSE
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        weather_data = api.get_weather_data(3.0, 101.5)
        
        assert 'current' in weather_data
        assert 'forecast' in weather_data
        assert 'fetched_at' in weather_data
        
        current = weather_data['current']
        assert current['main']['temp'] == 28.5
        assert current['weather'][0]['description'] == 'broken clouds'
        
        logger.info("Weather data retrieval test passed")
    
    @patch('requests.Session.request')
    def test_get_weather_data_invalid_coordinates(self, mock_request):
        """Test weather data retrieval with invalid coordinates."""
        logger.debug("Testing weather data with invalid coordinates")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Invalid latitude
        with pytest.raises(ValueError):
            api.get_weather_data(100, 101.5)  # Latitude > 90
        
        # Invalid longitude
        with pytest.raises(ValueError):
            api.get_weather_data(3.0, 200)  # Longitude > 180
        
        logger.info("Coordinate validation test passed")
    
    @patch('requests.Session.request')
    def test_rate_limit_handling(self, mock_request):
        """Test rate limit error handling."""
        logger.debug("Testing rate limit handling")
        
        # Mock rate limit response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_request.return_value = mock_response
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        with pytest.raises(RateLimitError) as exc_info:
            api.get_coordinates(TEST_CITY, TEST_COUNTRY)
        
        assert "rate limit exceeded" in str(exc_info.value).lower()
        assert "60" in str(exc_info.value)
        
        logger.info("Rate limit handling test passed")
    
    @patch('requests.Session.request')
    def test_service_unavailable(self, mock_request):
        """Test service unavailable error handling."""
        logger.debug("Testing service unavailable handling")
        
        # Mock server error
        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("503 Service Unavailable")
        mock_request.return_value = mock_response
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        with pytest.raises(ServiceUnavailableError) as exc_info:
            api.get_coordinates(TEST_CITY, TEST_COUNTRY)
        
        assert "service unavailable" in str(exc_info.value).lower()
        
        logger.info("Service unavailable test passed")
    
    @patch('requests.Session.request')
    def test_network_timeout(self, mock_request):
        """Test network timeout handling."""
        logger.debug("Testing network timeout handling")
        
        # Mock timeout
        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        with pytest.raises(APIRequestError) as exc_info:
            api.get_coordinates(TEST_CITY, TEST_COUNTRY)
        
        assert "timeout" in str(exc_info.value).lower()
        
        logger.info("Network timeout test passed")
    
    @patch('requests.Session.request')
    def test_connection_error(self, mock_request):
        """Test connection error handling."""
        logger.debug("Testing connection error handling")
        
        # Mock connection error
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        with pytest.raises(APIRequestError) as exc_info:
            api.get_coordinates(TEST_CITY, TEST_COUNTRY)
        
        assert "connection" in str(exc_info.value).lower()
        
        logger.info("Connection error test passed")
    
    def test_forecast_processing(self):
        """Test forecast data processing."""
        logger.debug("Testing forecast data processing")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Process sample forecast
        daily_forecast = api._process_forecast(SAMPLE_FORECAST_RESPONSE)
        
        assert len(daily_forecast) > 0
        assert 'date' in daily_forecast[0]
        assert 'temp_min' in daily_forecast[0]
        assert 'temp_max' in daily_forecast[0]
        assert 'weather' in daily_forecast[0]
        
        # Check data types
        assert isinstance(daily_forecast[0]['temp_min'], (int, float))
        assert isinstance(daily_forecast[0]['temp_max'], (int, float))
        assert isinstance(daily_forecast[0]['weather'], str)
        
        logger.info("Forecast processing test passed")
    
    def test_forecast_processing_empty_data(self):
        """Test forecast processing with empty data."""
        logger.debug("Testing forecast processing with empty data")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Test with empty forecast
        empty_forecast = api._process_forecast({'list': []})
        assert empty_forecast == []
        
        # Test with missing list
        no_list_forecast = api._process_forecast({})
        assert no_list_forecast == []
        
        logger.info("Empty forecast processing test passed")
    
    def test_forecast_processing_malformed_data(self):
        """Test forecast processing with malformed data."""
        logger.debug("Testing forecast processing with malformed data")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Malformed forecast data
        malformed_data = {
            'list': [
                {'dt_txt': '2024-01-15 12:00:00'},  # Missing required fields
                {
                    'dt_txt': '2024-01-15 15:00:00',
                    'main': {'temp_min': 25, 'temp_max': 30},
                    'weather': [{'description': 'cloudy'}]
                }
            ]
        }
        
        # Should handle gracefully
        result = api._process_forecast(malformed_data)
        assert len(result) >= 0  # Should not crash
        
        logger.info("Malformed forecast processing test passed")
    
    def test_api_representation(self):
        """Test string representation of API client."""
        logger.debug("Testing API client representation")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        repr_str = repr(api)
        
        assert "WeatherAPI" in repr_str
        assert TEST_API_KEY[:8] in repr_str
        
        logger.info("API representation test passed")


class TestWeatherAPIEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_coordinate_boundaries(self):
        """Test coordinate boundary validation."""
        logger.debug("Testing coordinate boundaries")
        
        api = WeatherAPI(api_key=TEST_API_KEY)
        
        # Valid coordinates (should not raise)
        with patch('requests.Session.request'):
            api.get_weather_data(90, 180)    # Max values
            api.get_weather_data(-90, -180)  # Min values
            api.get_weather_data(0, 0)        # Zero values
        
        logger.info("Coordinate boundary test passed")
    
    def test_api_key_edge_cases(self):
        """Test API key edge cases."""
        logger.debug("Testing API key edge cases")
        
        # Very long key (should work)
        long_key = "a" * 100
        api = WeatherAPI(api_key=long_key)
        assert api.api_key == long_key
        
        # Exactly at boundary
        boundary_key = "x" * 10
        api = WeatherAPI(api_key=boundary_key)
        assert api.api_key == boundary_key
        
        logger.info("API key edge cases test passed")