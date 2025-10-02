"""
Weather CLI Tool - A simple command-line weather application.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from weather_cli.weather_api import WeatherAPI
from weather_cli.formatter import WeatherFormatter
from weather_cli.exceptions import WeatherCLIError

__all__ = [
    "WeatherAPI",
    "WeatherFormatter", 
    "WeatherCLIError",
]