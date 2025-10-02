"""
Weather data formatting and display utilities.

This module handles the presentation of weather data in a clean, 
readable format suitable for terminal display.
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class WeatherFormatter:
    """
    Formats weather data for terminal display with clean, readable output.
    
    Features:
    - Temperature unit conversion (Celsius/Fahrenheit)
    - Weather condition formatting
    - Forecast summaries
    - Clean text output without any icons or special characters
    """
    
    def __init__(self, units: str = "metric"):
        """
        Initialize the formatter.
        
        Args:
            units: Unit system ("metric" for Celsius, "imperial" for Fahrenheit)
        """
        self.units = units
        self.temp_unit = "°C" if units == "metric" else "°F"
        
        logger.debug(f"WeatherFormatter initialized with {units} units")
    
    def format_current_weather(self, weather_data: Dict) -> str:
        """
        Format current weather data for display.
        
        Args:
            weather_data: Current weather data from API
            
        Returns:
            Formatted string for display
        """
        logger.debug("Formatting current weather data")
        
        try:
            # Extract basic info
            temp = self._extract_temperature(weather_data)
            condition = self._extract_condition(weather_data)
            humidity = self._extract_humidity(weather_data)
            wind = self._extract_wind(weather_data)
            pressure = self._extract_pressure(weather_data)
            
            # Build output
            lines = []
            lines.append(f"Current: {temp}{self.temp_unit} - {condition}")
            
            # Add details if available
            details = []
            if humidity is not None:
                details.append(f"Humidity: {humidity}%")
            if wind is not None:
                details.append(f"Wind: {wind}")
            if pressure is not None:
                details.append(f"Pressure: {pressure}hPa")
            
            if details:
                lines.append("  " + " | ".join(details))
            
            return "\n".join(lines)
            
        except KeyError as e:
            logger.error(f"Missing key in weather data: {e}")
            return f"Weather data incomplete - missing: {e}"
        except Exception as e:
            logger.error(f"Error formatting weather: {e}")
            return "Unable to display current weather"
    
    def format_forecast(self, forecast_data: List[Dict]) -> str:
        """
        Format forecast data for display.
        
        Args:
            forecast_data: List of daily forecast dictionaries
            
        Returns:
            Formatted forecast string
        """
        logger.debug(f"Formatting {len(forecast_data)} days of forecast")
        
        if not forecast_data:
            return "No forecast data available"
        
        lines = ["Forecast:"]
        
        for day in forecast_data:
            try:
                date_str = self._format_date(day.get('date', ''))
                temp_min = day.get('temp_min')
                temp_max = day.get('temp_max')
                weather = day.get('weather', 'Unknown')
                
                # Format temperature range
                if temp_min is not None and temp_max is not None:
                    temp_range = f"{temp_min}{self.temp_unit} - {temp_max}{self.temp_unit}"
                elif temp_min is not None:
                    temp_range = f"{temp_min}{self.temp_unit}"
                elif temp_max is not None:
                    temp_range = f"{temp_max}{self.temp_unit}"
                else:
                    temp_range = "No temp data"
                
                # Build day line
                day_line = f"{date_str}: {temp_range} | {weather}"
                lines.append(day_line)
                
            except Exception as e:
                logger.warning(f"Skipping malformed forecast day: {e}")
                continue
        
        return "\n".join(lines)
    
    def format_weather_summary(self, current: Dict, forecast: List[Dict]) -> str:
        """
        Create a complete weather summary combining current and forecast data.
        
        Args:
            current: Current weather data
            forecast: Forecast data list
            
        Returns:
            Complete formatted weather summary
        """
        logger.debug("Creating weather summary")
        
        sections = []
        
        # Location info (if available)
        location = self._extract_location(current)
        if location:
            sections.append(f"Location: {location}")
        
        # Current weather
        current_section = self.format_current_weather(current)
        sections.append(current_section)
        
        # Forecast
        if forecast:
            sections.append("")
            forecast_section = self.format_forecast(forecast)
            sections.append(forecast_section)
        
        return "\n".join(sections)
    
    def format_error(self, error_message: str) -> str:
        """
        Format an error message for display.
        
        Args:
            error_message: The error message
            
        Returns:
            Formatted error string
        """
        return f"Error: {error_message}"
    
    def format_warning(self, warning_message: str) -> str:
        """
        Format a warning message for display.
        
        Args:
            warning_message: The warning message
            
        Returns:
            Formatted warning string
        """
        return f"Warning: {warning_message}"
    
    def format_success(self, success_message: str) -> str:
        """
        Format a success message for display.
        
        Args:
            success_message: The success message
            
        Returns:
            Formatted success string
        """
        return f"Success: {success_message}"
    
    def _extract_temperature(self, weather_data: Dict) -> Optional[float]:
        """Extract temperature from weather data."""
        main_data = weather_data.get('main', {})
        temp = main_data.get('temp')
        
        if temp is not None:
            return round(float(temp), 1)
        return None
    
    def _extract_condition(self, weather_data: Dict) -> str:
        """Extract weather condition description."""
        weather_list = weather_data.get('weather', [])
        if weather_list and len(weather_list) > 0:
            return weather_list[0].get('description', 'Unknown').capitalize()
        return 'Unknown'
    
    def _extract_humidity(self, weather_data: Dict) -> Optional[int]:
        """Extract humidity percentage."""
        main_data = weather_data.get('main', {})
        humidity = main_data.get('humidity')
        
        if humidity is not None:
            return int(humidity)
        return None
    
    def _extract_pressure(self, weather_data: Dict) -> Optional[int]:
        """Extract atmospheric pressure."""
        main_data = weather_data.get('main', {})
        pressure = main_data.get('pressure')
        
        if pressure is not None:
            return int(pressure)
        return None
    
    def _extract_wind(self, weather_data: Dict) -> Optional[str]:
        """Extract wind information."""
        wind_data = weather_data.get('wind', {})
        speed = wind_data.get('speed')
        
        if speed is not None:
            # Convert m/s to km/h for metric, mph for imperial
            if self.units == "metric":
                speed_kmh = round(float(speed) * 3.6, 1)
                return f"{speed_kmh} km/h"
            else:
                speed_mph = round(float(speed) * 2.237, 1)
                return f"{speed_mph} mph"
        return None
    
    def _extract_location(self, weather_data: Dict) -> Optional[str]:
        """Extract location name from weather data."""
        name = weather_data.get('name')
        sys_data = weather_data.get('sys', {})
        country = sys_data.get('country')
        
        if name:
            if country:
                return f"{name}, {country}"
            return name
        return None
    
    def _format_date(self, date_str: str) -> str:
        """Format date string to readable format."""
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            return dt.strftime('%a %d %b')  # Wed 15 Jan
        except (ValueError, TypeError):
            return date_str  # Return original if parsing fails
    
    def set_units(self, units: str):
        """
        Change unit system.
        
        Args:
            units: "metric" for Celsius, "imperial" for Fahrenheit
        """
        if units not in ["metric", "imperial"]:
            raise ValueError("Units must be 'metric' or 'imperial'")
        
        self.units = units
        self.temp_unit = "°C" if units == "metric" else "°F"
        logger.debug(f"Changed units to {units}")
    
    def create_weather_table(self, forecast_data: List[Dict]) -> str:
        """
        Create a formatted table of weather data.
        
        Args:
            forecast_data: List of forecast days
            
        Returns:
            Formatted table string using plain text
        """
        if not forecast_data:
            return "No forecast data"
        
        lines = []
        lines.append("-" * 50)
        lines.append(f"{'Date':<12} {'Weather':<15} {'Temp Range':<20}")
        lines.append("-" * 50)
        
        for day in forecast_data:
            date = self._format_date(day.get('date', ''))
            weather = day.get('weather', 'Unknown')[:14]  # Truncate if too long
            temp_min = day.get('temp_min', '')
            temp_max = day.get('temp_max', '')
            
            if temp_min and temp_max:
                temp_range = f"{temp_min}{self.temp_unit}-{temp_max}{self.temp_unit}"
            else:
                temp_range = "N/A"
            
            line = f"{date:<12} {weather:<15} {temp_range:<20}"
            lines.append(line)
        
        lines.append("-" * 50)
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """String representation of the formatter."""
        return f"WeatherFormatter(units='{self.units}')"


# Convenience functions for quick formatting
def format_temperature(temp: float, units: str = "metric") -> str:
    """Format temperature with units."""
    unit = "°C" if units == "metric" else "°F"
    return f"{round(temp, 1)}{unit}"


def format_wind_speed(speed_ms: float, units: str = "metric") -> str:
    """Format wind speed in appropriate units."""
    if units == "metric":
        speed_kmh = round(speed_ms * 3.6, 1)
        return f"{speed_kmh} km/h"
    else:
        speed_mph = round(speed_ms * 2.237, 1)
        return f"{speed_mph} mph"