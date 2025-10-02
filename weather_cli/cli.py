"""
Command-line interface for the Weather CLI application.

Provides a simple, intuitive interface for fetching weather information
with clean text output without any icons or special characters.
"""

import os
import sys
import logging
from typing import Optional

import click

from weather_cli.weather_api import WeatherAPI
from weather_cli.formatter import WeatherFormatter
from weather_cli.exceptions import (
    WeatherCLIError,
    CityNotFoundError,
    InvalidAPIKeyError,
    APIRequestError
)

# Configure module logger
logger = logging.getLogger(__name__)


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Configure application logging.
    
    Args:
        debug: Enable debug logging level
        log_file: Optional file to log to
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
    
    logger.debug("Logging configured" + (" in debug mode" if debug else ""))


@click.command()
@click.option(
    '--city', 
    required=True,
    help='City name (e.g., "Puchong", "New York", "London")'
)
@click.option(
    '--country',
    required=True,
    help='Two-letter country code (e.g., "MY", "US", "GB")'
)
@click.option(
    '--units',
    type=click.Choice(['metric', 'imperial']),
    default='metric',
    help='Temperature units (metric=Celsius, imperial=Fahrenheit)'
)
@click.option(
    '--debug',
    is_flag=True,
    help='Enable debug logging'
)
@click.option(
    '--log-file',
    type=click.Path(),
    help='Log to file (optional)'
)
@click.option(
    '--api-key',
    help='API key (overrides environment variable)'
)
@click.option(
    '--timeout',
    type=int,
    default=10,
    help='Request timeout in seconds (default: 10)'
)
@click.option(
    '--format',
    'output_format',
    type=click.Choice(['simple', 'detailed', 'json']),
    default='simple',
    help='Output format (default: simple)'
)
@click.version_option(version='1.0.0')
def main(city: str, country: str, units: str, debug: bool, log_file: Optional[str],
         api_key: Optional[str], timeout: int, output_format: str):
    """
    Fetch and display weather information for a given city and country.
    
    Examples:
    
    \b
        # Basic usage
        weather-cli --city "Puchong" --country "MY"
        
    \b
        # With options
        weather-cli --city "New York" --country "US" --units imperial --debug
        
    \b
        # Save debug log
        weather-cli --city "London" --country "GB" --debug --log-file weather.log
        
    \b
        # Different output format
        weather-cli --city "Tokyo" --country "JP" --format detailed
    """
    # Configure logging
    setup_logging(debug=debug, log_file=log_file)
    
    logger.info("=" * 50)
    logger.info("Weather CLI Tool Started")
    logger.info(f"City: {city}, Country: {country}, Units: {units}")
    logger.info("=" * 50)
    
    # Initialize formatter early for error handling
    formatter = WeatherFormatter(units=units)
    
    try:
        # Get API key
        if not api_key:
            api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            logger.error("No API key provided")
            click.echo(
                "Error: API key not found. Please set OPENWEATHER_API_KEY environment variable "
                "or use --api-key option.",
                err=True
            )
            raise click.Abort()
        
        # Initialize API
        logger.debug("Initializing WeatherAPI...")
        weather_api = WeatherAPI(api_key=api_key, timeout=timeout)
        
        # Show progress
        if not debug:
            click.echo(f"Fetching weather for {city}, {country}...")
        
        # Get coordinates
        logger.info(f"Finding coordinates for {city}, {country}")
        lat, lon = weather_api.get_coordinates(city, country)
        logger.info(f"Coordinates found: {lat}, {lon}")
        
        # Get weather data
        logger.info("Fetching weather data...")
        weather_data = weather_api.get_weather_data(lat, lon)
        
        # Format and display results
        logger.debug("Formatting weather data...")
        
        if output_format == 'json':
            # JSON output (for scripts)
            import json
            click.echo(json.dumps(weather_data, indent=2))
            
        elif output_format == 'detailed':
            # Detailed formatted output
            output = formatter.format_weather_summary(
                weather_data['current'], 
                weather_data['forecast']
            )
            click.echo("\n" + "=" * 60)
            click.echo(output)
            click.echo("=" * 60)
            
        else:
            # Simple formatted output (default)
            current = formatter.format_current_weather(weather_data['current'])
            forecast = formatter.format_forecast(weather_data['forecast'])
            
            click.echo("\n" + "=" * 50)
            click.echo(current)
            if weather_data['forecast']:
                click.echo("")
                click.echo(forecast)
            click.echo("=" * 50)
        
        # Success message
        logger.info("Weather data displayed successfully")
        
    except CityNotFoundError as e:
        logger.error(f"City not found: {e}")
        click.echo(formatter.format_error(str(e)), err=True)
        raise click.Abort()
        
    except InvalidAPIKeyError as e:
        logger.error(f"Invalid API key: {e}")
        click.echo(formatter.format_error(str(e)), err=True)
        raise click.Abort()
        
    except APIRequestError as e:
        logger.error(f"API request failed: {e}")
        click.echo(formatter.format_error(str(e)), err=True)
        raise click.Abort()
        
    except KeyboardInterrupt:
        logger.info("User interrupted the program")
        click.echo("\nOperation cancelled by user", err=True)
        raise click.Abort()
        
    except Exception as e:
        logger.exception("Unexpected error occurred")
        click.echo(
            formatter.format_error(f"An unexpected error occurred: {str(e)}"),
            err=True
        )
        raise click.Abort()


def run_cli():
    """Entry point for the CLI application."""
    try:
        main()
    except click.Abort:
        # Handle graceful exit
        sys.exit(1)
    except Exception as e:
        # Handle any unhandled exceptions
        logger.exception("Unhandled exception in CLI")
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# For development/testing
if __name__ == '__main__':
    run_cli()