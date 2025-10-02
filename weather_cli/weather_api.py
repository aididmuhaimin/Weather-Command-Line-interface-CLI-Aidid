"""
Weather API client for interacting with OpenWeatherMap API.

This module handles all API communications including geocoding (city to coordinates)
and fetching weather data (current conditions and forecasts).
"""

import os
import time
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from weather_cli.exceptions import (
    CityNotFoundError,
    InvalidAPIKeyError,
    APIRequestError,
    RateLimitError,
    ServiceUnavailableError
)

logger = logging.getLogger(__name__)


class WeatherAPI:
    """
    Client for OpenWeatherMap API with built-in retry logic and error handling.
    
    Features:
    - Automatic retry on transient failures
    - Rate limit handling
    - Comprehensive error reporting
    - Request/response logging
    - Clean output without icons
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "http://api.openweathermap.org/geo/1.0"
    
    # Rate limiting
    MAX_RETRIES = 3
    RETRY_BACKOFF = 0.5
    RATE_LIMIT_WAIT = 60  # seconds
    
    def __init__(self, api_key: str = None, timeout: int = 10):
        """
        Initialize the Weather API client.
        
        Args:
            api_key: OpenWeatherMap API key (falls back to env var)
            timeout: Request timeout in seconds
            
        Raises:
            InvalidAPIKeyError: If no API key is provided
        """
        logger.debug("Initializing WeatherAPI client")
        
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        self.timeout = timeout
        
        if not self.api_key:
            logger.error("No API key provided or found in environment")
            raise InvalidAPIKeyError(
                "API key is required. Set OPENWEATHER_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Validate API key format
        if len(self.api_key) < 10:
            logger.error(f"Invalid API key format: {self.api_key[:5]}...")
            raise InvalidAPIKeyError("API key appears to be invalid format")
        
        logger.info(f"WeatherAPI initialized with key: {self.api_key[:8]}...")
        
        # Setup session with retry logic
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.MAX_RETRIES,
            backoff_factor=self.RETRY_BACKOFF,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            'User-Agent': 'WeatherCLI/1.0.0',
            'Accept': 'application/json',
        })
        
        logger.debug("HTTP session created with retry logic")
        return session
    
    def get_coordinates(self, city: str, country: str) -> Tuple[float, float]:
        """
        Get latitude and longitude for a city/country combination.
        
        Args:
            city: City name (e.g., "Puchong", "New York")
            country: Two-letter country code (e.g., "MY", "US")
            
        Returns:
            Tuple of (latitude, longitude)
            
        Raises:
            CityNotFoundError: If city cannot be found
            APIRequestError: If API request fails
        """
        logger.info(f"Finding coordinates for {city}, {country}")
        
        # Validate inputs
        if not city or not city.strip():
            raise ValueError("City name cannot be empty")
        
        if not country or len(country) != 2:
            raise ValueError("Country must be 2-letter code (e.g., 'MY', 'US')")
        
        params = {
            'q': f"{city.strip()},{country.upper().strip()}",
            'limit': 1,
            'appid': self.api_key
        }
        
        logger.debug(f"Geocoding request: {params}")
        
        try:
            response = self._make_request("GET", self.GEO_URL + "/direct", params=params)
            data = response.json()
            
            logger.debug(f"Geocoding response: {data}")
            
            if not data or len(data) == 0:
                logger.warning(f"City not found: {city}, {country}")
                raise CityNotFoundError(city, country)
            
            # Extract coordinates from first result
            location = data[0]
            lat = float(location['lat'])
            lon = float(location['lon'])
            found_city = location.get('name', city)
            found_country = location.get('country', country)
            
            logger.info(f"Found {found_city}, {found_country} at {lat}, {lon}")
            return lat, lon
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding request failed: {str(e)}")
            raise APIRequestError(
                f"Failed to find coordinates for {city}, {country}",
                original_error=e,
                endpoint="geocoding"
            )
    
    def get_weather_data(self, lat: float, lon: float) -> Dict:
        """
        Fetch current weather and forecast data for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary containing:
            - current: Current weather data
            - forecast: 3-day forecast data
            
        Raises:
            APIRequestError: If weather data cannot be fetched
        """
        logger.info(f"Fetching weather data for coordinates {lat}, {lon}")
        
        # Validate coordinates
        if not -90 <= lat <= 90:
            raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
        if not -180 <= lon <= 180:
            raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': 'metric',  # Celsius
            'lang': 'en'
        }
        
        try:
            # Fetch current weather
            logger.debug("Fetching current weather...")
            current_response = self._make_request(
                "GET", self.BASE_URL + "/weather", params=params
            )
            current_data = current_response.json()
            logger.debug(f"Current weather keys: {list(current_data.keys())}")
            
            # Fetch forecast
            logger.debug("Fetching forecast data...")
            forecast_response = self._make_request(
                "GET", self.BASE_URL + "/forecast", params=params
            )
            forecast_data = forecast_response.json()
            logger.debug(f"Forecast items count: {len(forecast_data.get('list', []))}")
            
            # Process forecast into daily summaries
            daily_forecast = self._process_forecast(forecast_data)
            logger.info(f"Processed {len(daily_forecast)} days of forecast")
            
            result = {
                'current': current_data,
                'forecast': daily_forecast,
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            logger.info("Weather data fetched successfully")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather data request failed: {str(e)}")
            raise APIRequestError(
                f"Failed to fetch weather data for coordinates {lat}, {lon}",
                original_error=e,
                endpoint="weather"
            )
    
    def _process_forecast(self, forecast_data: Dict) -> List[Dict]:
        """
        Process raw forecast data into daily summaries.
        
        Takes 3-hour interval data and creates daily min/max temperature summaries.
        
        Args:
            forecast_data: Raw forecast data from API
            
        Returns:
            List of daily forecast dictionaries with date, min/max temps, and weather
        """
        logger.debug("Processing forecast data into daily summaries")
        
        forecast_list = forecast_data.get('list', [])
        if not forecast_list:
            logger.warning("No forecast data available")
            return []
        
        # Group by date
        daily_data = {}
        
        for item in forecast_list:
            try:
                # Extract datetime
                dt_txt = item.get('dt_txt', '')
                if not dt_txt:
                    continue
                    
                date = dt_txt.split(' ')[0]  # YYYY-MM-DD
                
                # Extract temperatures
                main_data = item.get('main', {})
                temp = main_data.get('temp')
                temp_min = main_data.get('temp_min')
                temp_max = main_data.get('temp_max')
                
                # Use current temp if min/max not available
                if temp_min is None and temp is not None:
                    temp_min = temp
                if temp_max is None and temp is not None:
                    temp_max = temp
                
                # Extract weather condition
                weather_list = item.get('weather', [])
                weather = weather_list[0].get('description', 'unknown') if weather_list else 'unknown'
                
                # Update daily data
                if date not in daily_data:
                    daily_data[date] = {
                        'temp_min': temp_min,
                        'temp_max': temp_max,
                        'weather': weather
                    }
                else:
                    # Update min/max
                    if temp_min is not None and daily_data[date]['temp_min'] is not None:
                        daily_data[date]['temp_min'] = min(
                            daily_data[date]['temp_min'], temp_min
                        )
                    elif temp_min is not None:
                        daily_data[date]['temp_min'] = temp_min
                        
                    if temp_max is not None and daily_data[date]['temp_max'] is not None:
                        daily_data[date]['temp_max'] = max(
                            daily_data[date]['temp_max'], temp_max
                        )
                    elif temp_max is not None:
                        daily_data[date]['temp_max'] = temp_max
                    
            except (KeyError, IndexError, TypeError) as e:
                logger.warning(f"Skipping malformed forecast item: {e}")
                continue
        
        # Convert to list and limit to next 3 days
        result = []
        today = datetime.now().date()
        
        for date_str, data in sorted(daily_data.items()):
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                # Skip today and only include future days
                if date_obj > today:
                    result.append({
                        'date': date_str,
                        'temp_min': round(data['temp_min'], 1) if data['temp_min'] is not None else None,
                        'temp_max': round(data['temp_max'], 1) if data['temp_max'] is not None else None,
                        'weather': data['weather'].capitalize()
                    })
            except ValueError:
                continue
            
            # Limit to 3 days
            if len(result) >= 3:
                break
        
        logger.debug(f"Processed {len(result)} days of forecast")
        return result
    
    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling and rate limit detection.
        
        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters
            
        Returns:
            Response object
            
        Raises:
            RateLimitError: If rate limited
            ServiceUnavailableError: If service is down
            APIRequestError: For other request failures
        """
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            
            # Check for rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', self.RATE_LIMIT_WAIT))
                logger.warning(f"Rate limited, retry after {retry_after} seconds")
                raise RateLimitError(
                    f"API rate limit exceeded. Please retry after {retry_after} seconds.",
                    retry_after=retry_after
                )
            
            # Check for service unavailable
            if response.status_code >= 500:
                logger.error(f"Service unavailable: {response.status_code}")
                raise ServiceUnavailableError(
                    f"Weather service is temporarily unavailable (HTTP {response.status_code})"
                )
            
            # Check for authentication errors
            if response.status_code == 401:
                logger.error("Authentication failed - invalid API key")
                raise InvalidAPIKeyError("Invalid API key provided")
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            logger.debug(f"Request successful: {response.status_code}")
            return response
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout after {self.timeout}s")
            raise APIRequestError(
                f"Request timeout - weather service is not responding",
                original_error=e,
                endpoint=url
            )
            
        except requests.exceptions.ConnectionError as e:
            logger.error("Connection error - check internet connection")
            raise APIRequestError(
                "Cannot connect to weather service - check internet connection",
                original_error=e,
                endpoint=url
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIRequestError(
                f"Weather service request failed: {str(e)}",
                original_error=e,
                endpoint=url
            )
    
    def get_rate_limit_info(self) -> Dict[str, int]:
        """
        Get current rate limit status from the API.
        
        Returns:
            Dictionary with rate limit information
        """
        return {
            'daily_limit': 1000,  # Free tier
            'requests_remaining': None,
            'reset_time': None
        }
    
    def __repr__(self) -> str:
        """String representation of the API client."""
        return f"WeatherAPI(key='{self.api_key[:8]}...', timeout={self.timeout})"