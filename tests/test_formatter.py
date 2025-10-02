"""
Unit tests for the WeatherFormatter class.

Tests output formatting, unit conversions, and display formatting
for various weather data scenarios.
"""

import pytest
import logging
from unittest.mock import Mock

from weather_cli.formatter import WeatherFormatter, format_temperature, format_wind_speed
from tests import SAMPLE_WEATHER_RESPONSE

logger = logging.getLogger(__name__)


class TestWeatherFormatter:
    """Test cases for WeatherFormatter class."""
    
    def test_init_default(self):
        """Test formatter initialization with default settings."""
        logger.debug("Testing formatter default initialization")
        
        formatter = WeatherFormatter()
        assert formatter.units == "metric"
        assert formatter.temp_unit == "°C"
        
        logger.info("Default initialization test passed")
    
    def test_init_imperial(self):
        """Test formatter initialization with imperial units."""
        logger.debug("Testing formatter imperial initialization")
        
        formatter = WeatherFormatter(units="imperial")
        assert formatter.units == "imperial"
        assert formatter.temp_unit == "°F"
        
        logger.info("Imperial initialization test passed")
    
    def test_init_invalid_units(self):
        """Test formatter initialization with invalid units."""
        logger.debug("Testing formatter invalid units")
        
        with pytest.raises(ValueError):
            WeatherFormatter(units="invalid")
        
        logger.info("Invalid units test passed")
    
    def test_format_current_weather_basic(self):
        """Test basic current weather formatting."""
        logger.debug("Testing basic current weather formatting")
        
        formatter = WeatherFormatter()
        result = formatter.format_current_weather(SAMPLE_WEATHER_RESPONSE)
        
        assert "28.5°C" in result
        assert "Broken clouds" in result
        
        logger.info("Basic current weather formatting test passed")
    
    def test_format_current_weather_with_details(self):
        """Test current weather formatting with all details."""
        logger.debug("Testing current weather with details")
        
        # Add humidity and wind data
        weather_data = SAMPLE_WEATHER_RESPONSE.copy()
        weather_data['main']['humidity'] = 75
        weather_data['wind'] = {'speed': 2.57, 'deg': 310}
        
        formatter = WeatherFormatter()
        result = formatter.format_current_weather(weather_data)
        
        assert "28.5°C" in result
        assert "Humidity: 75%" in result
        assert "Wind:" in result
        
        logger.info("Current weather with details test passed")
    
    def test_format_current_weather_imperial(self):
        """Test current weather formatting with imperial units."""
        logger.debug("Testing current weather with imperial units")
        
        formatter = WeatherFormatter(units="imperial")
        
        # Convert temperature to Fahrenheit
        weather_data = SAMPLE_WEATHER_RESPONSE.copy()
        weather_data['main']['temp'] = 83.3  # 28.5°C in Fahrenheit
        
        result = formatter.format_current_weather(weather_data)
        
        assert "83.3°F" in result
        assert "Broken clouds" in result
        
        logger.info("Imperial current weather test passed")
    
    def test_format_current_weather_missing_data(self):
        """Test current weather formatting with missing data."""
        logger.debug("Testing current weather with missing data")
        
        # Minimal weather data
        minimal_data = {
            'main': {'temp': 25.0},
            'weather': [{'description': 'clear'}]
        }
        
        formatter = WeatherFormatter()
        result = formatter.format_current_weather(minimal_data)
        
        assert "25.0°C" in result
        assert "Clear" in result
        
        logger.info("Missing data current weather test passed")
    
    def test_format_current_weather_empty_data(self):
        """Test current weather formatting with empty data."""
        logger.debug("Testing current weather with empty data")
        
        formatter = WeatherFormatter()
        result = formatter.format_current_weather({})
        
        assert "incomplete" in result or "Unable" in result
        
        logger.info("Empty data current weather test passed")
    
    def test_format_forecast_basic(self):
        """Test basic forecast formatting."""
        logger.debug("Testing basic forecast formatting")
        
        # Create test forecast data
        forecast_data = [
            {
                'date': '2024-01-15',
                'temp_min': 25.0,
                'temp_max': 30.0,
                'weather': 'Clouds'
            },
            {
                'date': '2024-01-16',
                'temp_min': 24.0,
                'temp_max': 29.0,
                'weather': 'Rain'
            }
        ]
        
        formatter = WeatherFormatter()
        result = formatter.format_forecast(forecast_data)
        
        assert "Forecast:" in result
        assert "25°C - 30°C" in result
        assert "24°C - 29°C" in result
        assert "Clouds" in result
        assert "Rain" in result
        
        logger.info("Basic forecast formatting test passed")
    
    def test_format_forecast_empty(self):
        """Test forecast formatting with empty data."""
        logger.debug("Testing forecast with empty data")
        
        formatter = WeatherFormatter()
        result = formatter.format_forecast([])
        
        assert "No forecast data available" in result
        
        logger.info("Empty forecast test passed")
    
    def test_format_forecast_imperial(self):
        """Test forecast formatting with imperial units."""
        logger.debug("Testing forecast with imperial units")
        
        forecast_data = [
            {
                'date': '2024-01-15',
                'temp_min': 77.0,  # 25°C
                'temp_max': 86.0,  # 30°C
                'weather': 'Clouds'
            }
        ]
        
        formatter = WeatherFormatter(units="imperial")
        result = formatter.format_forecast(forecast_data)
        
        assert "77°F - 86°F" in result
        
        logger.info("Imperial forecast test passed")
    
    def test_format_forecast_missing_temperatures(self):
        """Test forecast formatting with missing temperatures."""
        logger.debug("Testing forecast with missing temperatures")
        
        forecast_data = [
            {
                'date': '2024-01-15',
                'temp_min': None,
                'temp_max': None,
                'weather': 'Clouds'
            }
        ]
        
        formatter = WeatherFormatter()
        result = formatter.format_forecast(forecast_data)
        
        assert "No temp data" in result or "Clouds" in result
        
        logger.info("Missing temperatures forecast test passed")
    
    def test_format_weather_summary(self):
        """Test complete weather summary formatting."""
        logger.debug("Testing weather summary formatting")
        
        current_data = SAMPLE_WEATHER_RESPONSE.copy()
        forecast_data = [
            {
                'date': '2024-01-15',
                'temp_min': 25.0,
                'temp_max': 30.0,
                'weather': 'Clouds'
            }
        ]
        
        formatter = WeatherFormatter()
        result = formatter.format_weather_summary(current_data, forecast_data)
        
        assert "Puchong, MY" in result
        assert "28.5°C" in result
        assert "Forecast:" in result
        assert "25°C - 30°C" in result
        
        logger.info("Weather summary test passed")
    
    def test_format_weather_summary_no_location(self):
        """Test weather summary without location info."""
        logger.debug("Testing weather summary without location")
        
        # Current data without location info
        current_data = {
            'main': {'temp': 25.0},
            'weather': [{'description': 'clear'}]
        }
        forecast_data = []
        
        formatter = WeatherFormatter()
        result = formatter.format_weather_summary(current_data, forecast_data)
        
        assert "25°C" in result
        
        logger.info("Weather summary without location test passed")
    
    def test_format_error(self):
        """Test error message formatting."""
        logger.debug("Testing error formatting")
        
        formatter = WeatherFormatter()
        result = formatter.format_error("Test error message")
        
        assert "Error: Test error message" == result
        
        logger.info("Error formatting test passed")
    
    def test_format_warning(self):
        """Test warning message formatting."""
        logger.debug("Testing warning formatting")
        
        formatter = WeatherFormatter()
        result = formatter.format_warning("Test warning message")
        
        assert "Warning: Test warning message" == result
        
        logger.info("Warning formatting test passed")
    
    def test_format_success(self):
        """Test success message formatting."""
        logger.debug("Testing success formatting")
        
        formatter = WeatherFormatter()
        result = formatter.format_success("Test success message")
        
        assert "Success: Test success message" == result
        
        logger.info("Success formatting test passed")
    
    def test_extract_temperature(self):
        """Test temperature extraction from weather data."""
        logger.debug("Testing temperature extraction")
        
        formatter = WeatherFormatter()
        
        # Normal temperature
        temp = formatter._extract_temperature({'main': {'temp': 25.5}})
        assert temp == 25.5
        
        # Integer temperature
        temp = formatter._extract_temperature({'main': {'temp': 25}})
        assert temp == 25.0
        
        # Missing temperature
        temp = formatter._extract_temperature({'main': {}})
        assert temp is None
        
        # No main section
        temp = formatter._extract_temperature({})
        assert temp is None
        
        logger.info("Temperature extraction test passed")
    
    def test_extract_condition(self):
        """Test weather condition extraction."""
        logger.debug("Testing condition extraction")
        
        formatter = WeatherFormatter()
        
        # Normal condition
        condition = formatter._extract_condition({
            'weather': [{'description': 'broken clouds'}]
        })
        assert condition == "Broken clouds"
        
        # Single word
        condition = formatter._extract_condition({
            'weather': [{'description': 'rain'}]
        })
        assert condition == "Rain"
        
        # Missing weather
        condition = formatter._extract_condition({})
        assert condition == "Unknown"
        
        # Empty weather list
        condition = formatter._extract_condition({'weather': []})
        assert condition == "Unknown"
        
        logger.info("Condition extraction test passed")
    
    def test_extract_humidity(self):
        """Test humidity extraction."""
        logger.debug("Testing humidity extraction")
        
        formatter = WeatherFormatter()
        
        # Normal humidity
        humidity = formatter._extract_humidity({'main': {'humidity': 75}})
        assert humidity == 75
        
        # Float humidity (should convert to int)
        humidity = formatter._extract_humidity({'main': {'humidity': 75.5}})
        assert humidity == 75
        
        # Missing humidity
        humidity = formatter._extract_humidity({'main': {}})
        assert humidity is None
        
        logger.info("Humidity extraction test passed")
    
    def test_extract_wind(self):
        """Test wind information extraction."""
        logger.debug("Testing wind extraction")
        
        formatter = WeatherFormatter()
        
        # Metric units
        wind = formatter._extract_wind({'wind': {'speed': 5.0}})
        assert "km/h" in wind
        
        # Imperial units
        formatter_imperial = WeatherFormatter(units="imperial")
        wind = formatter_imperial._extract_wind({'wind': {'speed': 5.0}})
        assert "mph" in wind
        
        # Missing wind
        wind = formatter._extract_wind({})
        assert wind is None
        
        logger.info("Wind extraction test passed")
    
    def test_format_date(self):
        """Test date formatting."""
        logger.debug("Testing date formatting")
        
        formatter = WeatherFormatter()
        
        # Normal date
        formatted = formatter._format_date('2024-01-15')
        assert "Jan" in formatted
        assert "15" in formatted
        
        # Invalid date
        formatted = formatter._format_date('invalid-date')
        assert formatted == 'invalid-date'
        
        logger.info("Date formatting test passed")
    
    def test_set_units(self):
        """Test changing units after initialization."""
        logger.debug("Testing unit change")
        
        formatter = WeatherFormatter(units="metric")
        assert formatter.units == "metric"
        assert formatter.temp_unit == "°C"
        
        # Change to imperial
        formatter.set_units("imperial")
        assert formatter.units == "imperial"
        assert formatter.temp_unit == "°F"
        
        # Try invalid units
        with pytest.raises(ValueError):
            formatter.set_units("invalid")
        
        logger.info("Unit change test passed")
    
    def test_create_weather_table(self):
        """Test weather table creation."""
        logger.debug("Testing weather table creation")
        
        forecast_data = [
            {
                'date': '2024-01-15',
                'temp_min': 25.0,
                'temp_max': 30.0,
                'weather': 'Clouds'
            }
        ]
        
        formatter = WeatherFormatter()
        table = formatter.create_weather_table(forecast_data)
        
        assert "Date" in table
        assert "Weather" in table
        assert "Temp Range" in table
        assert "25°C-30°C" in table or "25°C - 30°C" in table
        
        logger.info("Weather table creation test passed")
    
    def test_create_weather_table_empty(self):
        """Test weather table with empty data."""
        logger.debug("Testing weather table with empty data")
        
        formatter = WeatherFormatter()
        table = formatter.create_weather_table([])
        
        assert "No forecast data" in table
        
        logger.info("Empty weather table test passed")
    
    def test_repr(self):
        """Test string representation."""
        logger.debug("Testing formatter representation")
        
        formatter = WeatherFormatter(units="metric")
        repr_str = repr(formatter)
        
        assert "WeatherFormatter" in repr_str
        assert "metric" in repr_str
        
        logger.info("Formatter representation test passed")


class TestUtilityFunctions:
    """Test standalone utility functions."""
    
    def test_format_temperature(self):
        """Test temperature formatting function."""
        logger.debug("Testing format_temperature function")
        
        # Metric
        result = format_temperature(25.5, "metric")
        assert result == "25.5°C"
        
        # Imperial
        result = format_temperature(77.9, "imperial")
        assert result == "77.9°F"
        
        # Integer input
        result = format_temperature(25, "metric")
        assert result == "25.0°C"
        
        logger.info("Format temperature function test passed")
    
    def test_format_wind_speed(self):
        """Test wind speed formatting function."""
        logger.debug("Testing format_wind_speed function")
        
        # Metric (m/s to km/h)
        result = format_wind_speed(5.0, "metric")
        assert "km/h" in result
        assert "18.0" in result  # 5 m/s = 18 km/h
        
        # Imperial (m/s to mph)
        result = format_wind_speed(5.0, "imperial")
        assert "mph" in result
        assert "11.2" in result  # 5 m/s ≈ 11.2 mph
        
        logger.info("Format wind speed function test passed")