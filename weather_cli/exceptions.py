"""
Custom exceptions for the Weather CLI application.

This module defines all custom exceptions used throughout the application
to provide clear error handling and debugging capabilities.
"""

import logging

# Get logger for this module
logger = logging.getLogger(__name__)


class WeatherCLIError(Exception):
    """Base exception for all Weather CLI related errors."""
    
    def __init__(self, message: str, error_code: str = None):
        """
        Initialize the base exception.
        
        Args:
            message: Human-readable error message
            error_code: Optional error code for categorization
        """
        self.message = message
        self.error_code = error_code
        self.error_type = self.__class__.__name__
        
        # Log the exception creation
        logger.error(f"{self.error_type}: {message}" + 
                    (f" (Code: {error_code})" if error_code else ""))
        
        super().__init__(self.message)
    
    def __str__(self):
        """Return string representation of the exception."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class InvalidAPIKeyError(WeatherCLIError):
    """Raised when the API key is invalid, missing, or malformed."""
    
    def __init__(self, message: str = None, api_key: str = None):
        """
        Initialize invalid API key exception.
        
        Args:
            message: Custom error message
            api_key: The problematic API key (for logging, not storage)
        """
        if not message:
            message = "Invalid or missing API key. Please set OPENWEATHER_API_KEY environment variable."
        
        self.api_key = api_key[:8] + "..." if api_key and len(api_key) > 8 else api_key
        
        # Log additional details
        logger.error(f"API Key Error - Provided key: {self.api_key}")
        
        super().__init__(message, error_code="INVALID_API_KEY")


class CityNotFoundError(WeatherCLIError):
    """Raised when a specified city cannot be found in the API."""
    
    def __init__(self, city: str, country: str, message: str = None):
        """
        Initialize city not found exception.
        
        Args:
            city: City name that was not found
            country: Country code that was searched
            message: Custom error message
        """
        self.city = city
        self.country = country
        
        if not message:
            message = f"City '{city}' in country '{country}' not found. " \
                     f"Please check spelling and use 2-letter country codes (e.g., 'US', 'GB', 'MY')."
        
        # Log the failed search
        logger.error(f"City Search Failed - City: {city}, Country: {country}")
        
        super().__init__(message, error_code="CITY_NOT_FOUND")


class APIRequestError(WeatherCLIError):
    """Raised when an API request fails due to network or server issues."""
    
    def __init__(self, message: str, original_error: Exception = None, 
                 status_code: int = None, endpoint: str = None):
        """
        Initialize API request error.
        
        Args:
            message: Error message
            original_error: The original exception that occurred
            status_code: HTTP status code if available
            endpoint: API endpoint that failed
        """
        self.original_error = original_error
        self.status_code = status_code
        self.endpoint = endpoint
        
        # Build informative message
        details = []
        if status_code:
            details.append(f"Status: {status_code}")
        if endpoint:
            details.append(f"Endpoint: {endpoint}")
        
        if details:
            message = f"{message} ({', '.join(details)})"
        
        # Log technical details
        logger.error(f"API Request Failed - {message}")
        if original_error:
            logger.debug(f"Original error: {original_error}")
        
        super().__init__(message, error_code="API_REQUEST_FAILED")


class ConfigurationError(WeatherCLIError):
    """Raised when there's a configuration issue."""
    
    def __init__(self, message: str, config_key: str = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the issue
        """
        self.config_key = config_key
        
        if config_key:
            message = f"Configuration error for '{config_key}': {message}"
        
        super().__init__(message, error_code="CONFIG_ERROR")


class ValidationError(WeatherCLIError):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, value: str, message: str = None):
        """
        Initialize validation error.
        
        Args:
            field: Field name that failed validation
            value: Value that caused validation to fail
            message: Custom error message
        """
        self.field = field
        self.value = value
        
        if not message:
            message = f"Invalid {field}: '{value}'. Please provide a valid {field}."
        
        super().__init__(message, error_code="VALIDATION_ERROR")


class RateLimitError(WeatherCLIError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str = None, retry_after: int = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        self.retry_after = retry_after
        
        if not message:
            message = "API rate limit exceeded."
            if retry_after:
                message += f" Please retry after {retry_after} seconds."
        
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED")


class ServiceUnavailableError(WeatherCLIError):
    """Raised when the weather service is temporarily unavailable."""
    
    def __init__(self, message: str = None, service: str = "OpenWeatherMap"):
        """
        Initialize service unavailable error.
        
        Args:
            message: Error message
            service: Name of the unavailable service
        """
        self.service = service
        
        if not message:
            message = f"{service} service is temporarily unavailable. Please try again later."
        
        super().__init__(message, error_code="SERVICE_UNAVAILABLE")


# Exception hierarchy for easy catching
ERROR_HIERARCHY = {
    "WeatherCLIError": WeatherCLIError,
    "InvalidAPIKeyError": InvalidAPIKeyError,
    "CityNotFoundError": CityNotFoundError,
    "APIRequestError": APIRequestError,
    "ConfigurationError": ConfigurationError,
    "ValidationError": ValidationError,
    "RateLimitError": RateLimitError,
    "ServiceUnavailableError": ServiceUnavailableError,
}